use crate::detector::FileProfile;
use crate::error::SlimError;
use crate::modules::{Module, ModuleContext};
use crate::pipeline::{Options, Profile};
use crate::report::ModuleResult;
use quick_xml::events::Event;
use quick_xml::Reader;
use quick_xml::Writer;
use std::collections::HashSet;
use std::fs::File;
use std::io::{BufReader, BufWriter, Cursor, Read, Write};
use std::path::Path;
use zip::write::FileOptions;
use zip::{CompressionMethod, DateTime, ZipArchive, ZipWriter};

#[derive(Debug, Default)]
pub struct XmlStyles;

impl Module for XmlStyles {
    fn name(&self) -> &'static str {
        "xml_styles"
    }

    fn is_applicable(&self, _profile: &FileProfile, options: &Options) -> bool {
        options.xml && options.profile != Profile::Safe
    }

    fn run(&self, ctx: &ModuleContext<'_>) -> Result<ModuleResult, SlimError> {
        let before = std::fs::metadata(ctx.input_path)
            .map_err(|err| SlimError::io(&ctx.input_path.to_path_buf(), err))?
            .len();

        let input_file = File::open(ctx.input_path)
            .map_err(|err| SlimError::io(&ctx.input_path.to_path_buf(), err))?;
        let mut archive = ZipArchive::new(BufReader::new(input_file)).map_err(|err| {
            SlimError::InvalidZip {
                message: err.to_string(),
            }
        })?;

        let mut styles_bytes = Vec::new();
        if let Ok(mut file) = archive.by_name("xl/styles.xml") {
            file.read_to_end(&mut styles_bytes)
                .map_err(|e| SlimError::io(&ctx.input_path.to_path_buf(), e))?;
        } else {
            return pass_through(ctx, before);
        }

        let cell_xfs = parse_cell_xfs(&styles_bytes)?;
        if cell_xfs.is_empty() {
            return pass_through(ctx, before);
        }

        let used_styles = collect_used_styles(&mut archive)?;
        let (mapping, kept) = build_mapping(cell_xfs.len(), &used_styles);

        if kept.len() == cell_xfs.len() {
            return pass_through(ctx, before);
        }

        let mut new_cell_xfs = Vec::with_capacity(kept.len());
        for old_idx in &kept {
            if let Some(xf) = cell_xfs.get(*old_idx) {
                new_cell_xfs.push(xf.clone());
            }
        }

        let new_styles = rewrite_styles(&styles_bytes, &new_cell_xfs)?;

        let output_file = File::create(ctx.output_path)
            .map_err(|err| SlimError::io(&ctx.output_path.to_path_buf(), err))?;
        let mut writer = ZipWriter::new(BufWriter::new(output_file));

        let fixed_time = DateTime::from_date_and_time(1980, 1, 1, 0, 0, 0).map_err(|_| {
            SlimError::Internal {
                message: "failed to build fixed timestamp".to_string(),
            }
        })?;

        for i in 0..archive.len() {
            let mut file = archive.by_index(i).map_err(|err| SlimError::InvalidZip {
                message: err.to_string(),
            })?;
            let name = file.name().to_string();
            validate_zip_name(ctx.input_path, &name)?;

            if name.ends_with('/') {
                continue;
            }

            let mut options = FileOptions::default()
                .compression_method(CompressionMethod::Deflated)
                .last_modified_time(fixed_time);

            if let Some(mode) = file.unix_mode() {
                options = options.unix_permissions(mode);
            }

            writer.start_file(&name, options).map_err(|err| {
                SlimError::InvalidZip {
                    message: err.to_string(),
                }
            })?;

            if name == "xl/styles.xml" {
                writer
                    .write_all(&new_styles)
                    .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
            } else if name.starts_with("xl/worksheets/") && name.ends_with(".xml") {
                let data = rewrite_worksheet_styles(&mut file, &mapping)?;
                writer
                    .write_all(&data)
                    .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
            } else {
                std::io::copy(&mut file, &mut writer)
                    .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
            }
        }

        writer.finish().map_err(|err| SlimError::InvalidZip {
            message: err.to_string(),
        })?;

        let after = std::fs::metadata(ctx.output_path)
            .map_err(|err| SlimError::io(&ctx.output_path.to_path_buf(), err))?
            .len();

        let notes = vec![format!(
            "cellXfs: {} -> {}",
            cell_xfs.len(),
            new_cell_xfs.len()
        )];

        Ok(ModuleResult::new(self.name(), before, after, notes, Vec::new()))
    }
}

fn pass_through(ctx: &ModuleContext<'_>, before: u64) -> Result<ModuleResult, SlimError> {
    std::fs::copy(ctx.input_path, ctx.output_path)
        .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
    let after = std::fs::metadata(ctx.output_path)
        .map_err(|err| SlimError::io(&ctx.output_path.to_path_buf(), err))?
        .len();
    Ok(ModuleResult::new(
        "xml_styles",
        before,
        after,
        vec![],
        vec!["skipped (no style pruning)".to_string()],
    ))
}

fn collect_used_styles(archive: &mut ZipArchive<BufReader<File>>) -> Result<HashSet<usize>, SlimError> {
    let mut used = HashSet::new();
    used.insert(0);

    let mut worksheet_names = Vec::new();
    for i in 0..archive.len() {
        let file = archive.by_index(i).map_err(|err| SlimError::InvalidZip {
            message: err.to_string(),
        })?;
        let name = file.name().to_string();
        if name.starts_with("xl/worksheets/") && name.ends_with(".xml") {
            worksheet_names.push(name);
        }
    }

    for name in worksheet_names {
        let mut file = archive.by_name(&name).map_err(|err| SlimError::InvalidZip {
            message: err.to_string(),
        })?;
        collect_used_styles_from_sheet(&mut file, &mut used)?;
    }

    Ok(used)
}

fn collect_used_styles_from_sheet(
    reader: &mut impl Read,
    used: &mut HashSet<usize>,
) -> Result<(), SlimError> {
    let mut buf = Vec::new();
    reader
        .read_to_end(&mut buf)
        .map_err(|e| SlimError::Internal { message: e.to_string() })?;
    let mut xml_reader = Reader::from_reader(&buf[..]);
    xml_reader.trim_text(false);
    let mut buf_event = Vec::new();

    loop {
        match xml_reader.read_event_into(&mut buf_event) {
            Ok(Event::Start(ref e)) | Ok(Event::Empty(ref e))
                if matches!(e.name().as_ref(), b"c" | b"row" | b"col") =>
            {
                for attr in e.attributes() {
                    let attr = attr.map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
                    let key = attr.key.as_ref();
                    let is_style_attr = if e.name().as_ref() == b"col" {
                        key == b"style"
                    } else {
                        key == b"s"
                    };
                    if is_style_attr {
                        let value = std::str::from_utf8(attr.value.as_ref())
                            .map_err(|e| SlimError::XmlParseError {
                                message: e.to_string(),
                            })?;
                        if let Ok(idx) = value.parse::<usize>() {
                            used.insert(idx);
                        }
                    }
                }
            }
            Ok(Event::Eof) => break,
            Err(e) => {
                return Err(SlimError::XmlParseError {
                    message: e.to_string(),
                })
            }
            _ => {}
        }
        buf_event.clear();
    }

    Ok(())
}

fn build_mapping(total: usize, used: &HashSet<usize>) -> (Vec<usize>, Vec<usize>) {
    let mut kept = Vec::new();
    for i in 0..total {
        if i == 0 || used.contains(&i) {
            kept.push(i);
        }
    }
    let mut mapping = vec![0usize; total];
    for (new_idx, old_idx) in kept.iter().enumerate() {
        mapping[*old_idx] = new_idx;
    }
    (mapping, kept)
}

fn parse_cell_xfs(styles: &[u8]) -> Result<Vec<Vec<u8>>, SlimError> {
    let mut reader = Reader::from_reader(styles);
    reader.trim_text(false);
    let mut buf = Vec::new();
    let mut in_cell_xfs = false;
    let mut xfs = Vec::new();

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(ref e)) if e.name().as_ref() == b"cellXfs" => {
                in_cell_xfs = true;
            }
            Ok(Event::End(ref e)) if e.name().as_ref() == b"cellXfs" => {
                break;
            }
            Ok(Event::Start(ref e)) if in_cell_xfs && e.name().as_ref() == b"xf" => {
                let xf = capture_element(&mut reader, e.clone(), b"xf")?;
                xfs.push(xf);
            }
            Ok(Event::Empty(ref e)) if in_cell_xfs && e.name().as_ref() == b"xf" => {
                let mut writer = Writer::new(Cursor::new(Vec::new()));
                writer
                    .write_event(Event::Empty(e.clone()))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
                xfs.push(writer.into_inner().into_inner());
            }
            Ok(Event::Eof) => break,
            Err(e) => {
                return Err(SlimError::XmlParseError {
                    message: e.to_string(),
                })
            }
            _ => {}
        }
        buf.clear();
    }

    Ok(xfs)
}

fn capture_element(
    reader: &mut Reader<&[u8]>,
    start: quick_xml::events::BytesStart<'_>,
    tag: &[u8],
) -> Result<Vec<u8>, SlimError> {
    let mut writer = Writer::new(Cursor::new(Vec::new()));
    writer
        .write_event(Event::Start(start))
        .map_err(|e| SlimError::XmlParseError {
            message: e.to_string(),
        })?;
    let mut buf = Vec::new();
    let mut depth = 0usize;

    loop {
        let event = reader.read_event_into(&mut buf);
        match event {
            Ok(Event::Start(ref e)) => {
                depth += 1;
                writer
                    .write_event(Event::Start(e.clone()))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Ok(Event::Empty(ref e)) => {
                writer
                    .write_event(Event::Empty(e.clone()))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Ok(Event::End(ref e)) => {
                writer
                    .write_event(Event::End(e.clone()))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
                if depth == 0 && e.name().as_ref() == tag {
                    break;
                }
                if depth > 0 {
                    depth -= 1;
                }
            }
            Ok(Event::Eof) => {
                return Err(SlimError::XmlParseError {
                    message: "unexpected EOF while reading styles".to_string(),
                })
            }
            Ok(e) => {
                writer
                    .write_event(e)
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Err(e) => {
                return Err(SlimError::XmlParseError {
                    message: e.to_string(),
                })
            }
        }
        buf.clear();
    }

    Ok(writer.into_inner().into_inner())
}

fn rewrite_styles(styles: &[u8], new_cell_xfs: &[Vec<u8>]) -> Result<Vec<u8>, SlimError> {
    let mut reader = Reader::from_reader(styles);
    reader.trim_text(false);
    let mut writer = Writer::new(Cursor::new(Vec::new()));
    let mut buf = Vec::new();

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(ref e)) if e.name().as_ref() == b"cellXfs" => {
                let mut new_start = quick_xml::events::BytesStart::new("cellXfs");
                for attr in e.attributes() {
                    let attr = attr.map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
                    if attr.key.as_ref() != b"count" {
                        new_start.push_attribute(attr);
                    }
                }
                new_start.push_attribute(("count", new_cell_xfs.len().to_string().as_str()));
                writer
                    .write_event(Event::Start(new_start))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;

                {
                    let inner = writer.get_mut();
                    for xf in new_cell_xfs {
                        inner
                            .write_all(xf)
                            .map_err(|e| SlimError::Internal { message: e.to_string() })?;
                    }
                }

                skip_to_end(&mut reader, b"cellXfs")?;
                writer
                    .write_event(Event::End(quick_xml::events::BytesEnd::new("cellXfs")))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Ok(Event::Empty(ref e)) if e.name().as_ref() == b"cellXfs" => {
                let mut new_start = quick_xml::events::BytesStart::new("cellXfs");
                for attr in e.attributes() {
                    let attr = attr.map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
                    if attr.key.as_ref() != b"count" {
                        new_start.push_attribute(attr);
                    }
                }
                new_start.push_attribute(("count", new_cell_xfs.len().to_string().as_str()));
                writer
                    .write_event(Event::Start(new_start))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;

                {
                    let inner = writer.get_mut();
                    for xf in new_cell_xfs {
                        inner
                            .write_all(xf)
                            .map_err(|e| SlimError::Internal { message: e.to_string() })?;
                    }
                }

                writer
                    .write_event(Event::End(quick_xml::events::BytesEnd::new("cellXfs")))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Ok(Event::Eof) => break,
            Ok(event) => {
                writer
                    .write_event(event)
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Err(e) => {
                return Err(SlimError::XmlParseError {
                    message: e.to_string(),
                })
            }
        }
        buf.clear();
    }

    Ok(writer.into_inner().into_inner())
}

fn skip_to_end(reader: &mut Reader<&[u8]>, tag: &[u8]) -> Result<(), SlimError> {
    let mut depth = 0usize;
    let mut buf = Vec::new();
    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(_)) => depth += 1,
            Ok(Event::End(ref e)) => {
                if depth == 0 && e.name().as_ref() == tag {
                    break;
                }
                if depth > 0 {
                    depth -= 1;
                }
            }
            Ok(Event::Eof) => {
                return Err(SlimError::XmlParseError {
                    message: "unexpected EOF while skipping styles".to_string(),
                })
            }
            Err(e) => {
                return Err(SlimError::XmlParseError {
                    message: e.to_string(),
                })
            }
            _ => {}
        }
        buf.clear();
    }
    Ok(())
}

fn rewrite_worksheet_styles(
    reader: &mut impl Read,
    mapping: &[usize],
) -> Result<Vec<u8>, SlimError> {
    let mut buf = Vec::new();
    reader
        .read_to_end(&mut buf)
        .map_err(|e| SlimError::Internal { message: e.to_string() })?;
    let mut xml_reader = Reader::from_reader(&buf[..]);
    xml_reader.trim_text(false);
    let mut writer = Writer::new(Cursor::new(Vec::new()));
    let mut buf_event = Vec::new();

    loop {
        match xml_reader.read_event_into(&mut buf_event) {
            Ok(Event::Start(ref e)) if matches!(e.name().as_ref(), b"c" | b"row" | b"col") => {
                let new = rewrite_cell_start(e, mapping)?;
                writer
                    .write_event(Event::Start(new))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Ok(Event::Empty(ref e)) if matches!(e.name().as_ref(), b"c" | b"row" | b"col") => {
                let new = rewrite_cell_start(e, mapping)?;
                writer
                    .write_event(Event::Empty(new))
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Ok(Event::Eof) => break,
            Ok(event) => {
                writer
                    .write_event(event)
                    .map_err(|e| SlimError::XmlParseError {
                        message: e.to_string(),
                    })?;
            }
            Err(e) => {
                return Err(SlimError::XmlParseError {
                    message: e.to_string(),
                })
            }
        }
        buf_event.clear();
    }

    Ok(writer.into_inner().into_inner())
}

fn rewrite_cell_start(
    e: &quick_xml::events::BytesStart<'_>,
    mapping: &[usize],
) -> Result<quick_xml::events::BytesStart<'static>, SlimError> {
    let name = e.name();
    let name_str = std::str::from_utf8(name.as_ref()).map_err(|e| SlimError::XmlParseError {
        message: e.to_string(),
    })?;
    let mut new = quick_xml::events::BytesStart::new(name_str);
    let name_bytes = name.as_ref();
    for attr in e.attributes() {
        let attr = attr.map_err(|e| SlimError::XmlParseError {
            message: e.to_string(),
        })?;
        let key = attr.key.as_ref();
        let is_style_attr = if name_bytes == b"col" {
            key == b"style"
        } else {
            key == b"s"
        };
        if is_style_attr {
            let value = std::str::from_utf8(attr.value.as_ref()).map_err(|e| SlimError::XmlParseError {
                message: e.to_string(),
            })?;
            if let Ok(old_idx) = value.parse::<usize>() {
                if let Some(new_idx) = mapping.get(old_idx) {
                    let new_value = new_idx.to_string();
                    let key_str = if name_bytes == b"col" { "style" } else { "s" };
                    new.push_attribute((key_str, new_value.as_str()));
                    continue;
                }
            }
        }
        new.push_attribute(attr);
    }
    Ok(new.into_owned())
}

fn validate_zip_name(path: &Path, name: &str) -> Result<(), SlimError> {
    let p = Path::new(name);
    if p.is_absolute() {
        return Err(SlimError::InvalidZip {
            message: format!("{}: invalid absolute path entry {name}", path.display()),
        });
    }
    for component in p.components() {
        if matches!(component, std::path::Component::ParentDir) {
            return Err(SlimError::InvalidZip {
                message: format!("{}: invalid parent component in {name}", path.display()),
            });
        }
    }
    if name.contains('\\') {
        return Err(SlimError::InvalidZip {
            message: format!("{}: invalid backslash in {name}", path.display()),
        });
    }
    Ok(())
}
