use crate::detector::FileProfile;
use crate::error::SlimError;
use crate::modules::{Module, ModuleContext};
use crate::pipeline::Options;
use crate::report::ModuleResult;
use quick_xml::events::{BytesStart, BytesText, Event};
use quick_xml::{Reader, Writer};
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Cursor, Read, Write};
use std::path::Path;
use zip::write::FileOptions;
use zip::{CompressionMethod, DateTime, ZipArchive, ZipWriter};

#[derive(Debug, Default)]
pub struct XmlSharedStrings;

impl Module for XmlSharedStrings {
    fn name(&self) -> &'static str {
        "xml_shared_strings"
    }

    fn is_applicable(&self, _profile: &FileProfile, options: &Options) -> bool {
        options.xml
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

        // 1. Analyze sharedStrings.xml if it exists
        let analysis = if let Ok(file) = archive.by_name("xl/sharedStrings.xml") {
            let mut reader = BufReader::new(file);
            analyze_shared_strings(&mut reader)?
        } else {
            return pass_through(ctx, before, "skipped (no shared strings)".to_string());
        };

        let (unique_strings, mapping) = match analysis {
            SharedStringsAnalysis::NoDuplicates => {
                return pass_through(ctx, before, "skipped (no duplicates)".to_string());
            }
            SharedStringsAnalysis::Dedup {
                unique_strings,
                mapping,
            } => (unique_strings, mapping),
        };

        // 2. Rewrite ZIP
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

            // Copy permissions if available
            let options = FileOptions::default()
                .compression_method(CompressionMethod::Deflated)
                .last_modified_time(fixed_time)
                .unix_permissions(file.unix_mode().unwrap_or(0o644));

            writer.start_file(&name, options).map_err(|err| {
                SlimError::InvalidZip {
                    message: err.to_string(),
                }
            })?;

            if name == "xl/sharedStrings.xml" {
                let data = write_shared_strings(&unique_strings, mapping.len())?;
                writer
                    .write_all(&data)
                    .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
            } else if name.starts_with("xl/worksheets/sheet") && name.ends_with(".xml") {
                let data = process_worksheet(&mut file, &mapping)?;
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
            "unique shared strings: {} -> {}",
            mapping.len(),
            unique_strings.len()
        )];

        Ok(ModuleResult::new(self.name(), before, after, notes, Vec::new()))
    }
}

fn pass_through(
    ctx: &ModuleContext<'_>,
    before: u64,
    reason: String,
) -> Result<ModuleResult, SlimError> {
    std::fs::copy(ctx.input_path, ctx.output_path)
        .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
    let after = std::fs::metadata(ctx.output_path)
        .map_err(|err| SlimError::io(&ctx.output_path.to_path_buf(), err))?
        .len();
    Ok(ModuleResult::new(
        "xml_shared_strings",
        before,
        after,
        vec![],
        vec![reason],
    ))
}


enum SharedStringsAnalysis {
    NoDuplicates,
    Dedup {
        unique_strings: Vec<String>,
        mapping: Vec<usize>,
    },
}

fn analyze_shared_strings(reader: &mut impl BufRead) -> Result<SharedStringsAnalysis, SlimError> {
    let mut xml_reader = Reader::from_reader(reader);
    xml_reader.trim_text(false);

    let mut declared_count: Option<usize> = None;
    let mut declared_unique: Option<usize> = None;
    let mut saw_sst = false;

    let mut buf_event = Vec::new();

    loop {
        match xml_reader.read_event_into(&mut buf_event) {
            Ok(Event::Start(ref e)) if e.name().as_ref() == b"sst" => {
                saw_sst = true;
                parse_sst_counts(e, &mut declared_count, &mut declared_unique)?;
                if declared_count.is_some() && declared_count == declared_unique {
                    return Ok(SharedStringsAnalysis::NoDuplicates);
                }
                break;
            }
            Ok(Event::Empty(ref e)) if e.name().as_ref() == b"sst" => {
                parse_sst_counts(e, &mut declared_count, &mut declared_unique)?;
                return Ok(SharedStringsAnalysis::NoDuplicates);
            }
            Ok(Event::Eof) => break,
            Err(e) => return Err(SlimError::XmlParseError { message: e.to_string() }),
            _ => {}
        }
        buf_event.clear();
    }

    if !saw_sst {
        return Ok(SharedStringsAnalysis::NoDuplicates);
    }

    let mut unique_map: HashMap<String, usize> = HashMap::new();
    let mut unique_list: Vec<String> = Vec::new();
    let mut mapping: Vec<usize> = Vec::new();

    loop {
        match xml_reader.read_event_into(&mut buf_event) {
            Ok(Event::Start(ref e)) if e.name().as_ref() == b"si" => {
                let si_xml = read_si_content(&mut xml_reader)?;
                if let Some(idx) = unique_map.get(&si_xml) {
                    mapping.push(*idx);
                } else {
                    let new_idx = unique_list.len();
                    unique_map.insert(si_xml.clone(), new_idx);
                    unique_list.push(si_xml);
                    mapping.push(new_idx);
                }
            }
            Ok(Event::Empty(ref e)) if e.name().as_ref() == b"si" => {
                let si_xml = String::new();
                if let Some(idx) = unique_map.get(&si_xml) {
                    mapping.push(*idx);
                } else {
                    let new_idx = unique_list.len();
                    unique_map.insert(si_xml.clone(), new_idx);
                    unique_list.push(si_xml);
                    mapping.push(new_idx);
                }
            }
            Ok(Event::End(ref e)) if e.name().as_ref() == b"sst" => break,
            Ok(Event::Eof) => break,
            Err(e) => return Err(SlimError::XmlParseError { message: e.to_string() }),
            _ => {}
        }
        buf_event.clear();
    }

    Ok(SharedStringsAnalysis::Dedup {
        unique_strings: unique_list,
        mapping,
    })
}

fn parse_sst_counts(
    e: &quick_xml::events::BytesStart<'_>,
    declared_count: &mut Option<usize>,
    declared_unique: &mut Option<usize>,
) -> Result<(), SlimError> {
    for attr in e.attributes() {
        let attr = attr.map_err(|e| SlimError::XmlParseError {
            message: e.to_string(),
        })?;
        if attr.key.as_ref() == b"count" {
            *declared_count = parse_usize(&attr.value)?;
        } else if attr.key.as_ref() == b"uniqueCount" {
            *declared_unique = parse_usize(&attr.value)?;
        }
    }
    Ok(())
}

fn parse_usize(bytes: &[u8]) -> Result<Option<usize>, SlimError> {
    let value = std::str::from_utf8(bytes).map_err(|e| SlimError::XmlParseError {
        message: e.to_string(),
    })?;
    Ok(value.parse::<usize>().ok())
}

fn read_si_content<B: BufRead>(reader: &mut Reader<B>) -> Result<String, SlimError> {
    let mut writer = Writer::new(Cursor::new(Vec::new()));
    let mut buf = Vec::new();
    let mut depth = 0;

    loop {
        let event = reader
            .read_event_into(&mut buf)
            .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
        match event {
            Event::End(ref e) if e.name().as_ref() == b"si" && depth == 0 => {
                break;
            }
            Event::Eof => {
                return Err(SlimError::XmlParseError {
                    message: "unexpected EOF while reading shared string".to_string(),
                });
            }
            Event::Start(ref e) if e.name().as_ref() == b"si" => {
                depth += 1;
                writer
                    .write_event(Event::Start(e.clone()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Event::End(ref e) if e.name().as_ref() == b"si" => {
                depth -= 1;
                writer
                    .write_event(Event::End(e.clone()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            e => {
                writer
                    .write_event(e)
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
        }
        buf.clear();
    }
    
    let result = writer.into_inner().into_inner();
    String::from_utf8(result).map_err(|e| SlimError::Internal { message: e.to_string() })
}

fn write_shared_strings(strings: &[String], total_count: usize) -> Result<Vec<u8>, SlimError> {
    let mut item_writer = Writer::new(Cursor::new(Vec::new()));
    item_writer
        .write_event(Event::Decl(quick_xml::events::BytesDecl::new(
            "1.0",
            Some("UTF-8"),
            Some("yes"),
        )))
        .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;

    let mut root = BytesStart::new("sst");
    root.push_attribute(("xmlns", "http://schemas.openxmlformats.org/spreadsheetml/2006/main"));
    let count = strings.len().to_string();
    let total = total_count.to_string();
    root.push_attribute(("count", total.as_str()));
    root.push_attribute(("uniqueCount", count.as_str()));

    item_writer
        .write_event(Event::Start(root))
        .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;

    {
        let inner = item_writer.get_mut();
        for s in strings {
            inner
                .write_all(b"<si>")
                .map_err(|e| SlimError::Internal { message: e.to_string() })?;
            inner
                .write_all(s.as_bytes())
                .map_err(|e| SlimError::Internal { message: e.to_string() })?;
            inner
                .write_all(b"</si>")
                .map_err(|e| SlimError::Internal { message: e.to_string() })?;
        }
    }

    item_writer
        .write_event(Event::End(quick_xml::events::BytesEnd::new("sst")))
        .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;

    Ok(item_writer.into_inner().into_inner())
}

fn process_worksheet(reader: &mut impl Read, mapping: &[usize]) -> Result<Vec<u8>, SlimError> {
    let mut buf = Vec::new();
    reader
        .read_to_end(&mut buf)
        .map_err(|e| SlimError::Internal { message: e.to_string() })?;

    let mut xml_reader = Reader::from_reader(Cursor::new(&buf));
    xml_reader.trim_text(false);
    let mut writer = Writer::new(Cursor::new(Vec::new()));
    
    let mut buf_event = Vec::new();
    
    let mut state = 0; // 0=Normal, 1=InSharedCell, 2=InValue

    loop {
        let event = xml_reader.read_event_into(&mut buf_event);
        match event {
            Ok(Event::Start(ref e)) => {
                if e.name().as_ref() == b"c" {
                    let mut is_shared = false;
                    for attr in e.attributes() {
                        let a = attr.map_err(|e| SlimError::XmlParseError {
                            message: e.to_string(),
                        })?;
                        if a.key.as_ref() == b"t" && a.value.as_ref() == b"s" {
                            is_shared = true;
                        }
                    }
                    state = if is_shared { 1 } else { 0 };
                } else if state == 1 && e.name().as_ref() == b"v" {
                    state = 2;
                }
                writer
                    .write_event(Event::Start(e.clone()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::Text(ref e)) if state == 2 => {
                let text = e.unescape().map_err(|e| SlimError::XmlParseError {
                    message: e.to_string(),
                })?;
                if let Ok(old_idx) = text.parse::<usize>() {
                    if let Some(new_idx) = mapping.get(old_idx) {
                        let new_text = new_idx.to_string();
                        writer
                            .write_event(Event::Text(BytesText::new(&new_text)))
                            .map_err(|e| SlimError::XmlParseError {
                                message: e.to_string(),
                            })?;
                    } else {
                        writer
                            .write_event(Event::Text(e.clone()))
                            .map_err(|e| SlimError::XmlParseError {
                                message: e.to_string(),
                            })?;
                    }
                } else {
                    writer
                        .write_event(Event::Text(e.clone()))
                        .map_err(|e| SlimError::XmlParseError {
                            message: e.to_string(),
                        })?;
                }
            }
            Ok(Event::End(ref e)) => {
                if e.name().as_ref() == b"c" {
                    state = 0;
                } else if e.name().as_ref() == b"v" && state == 2 {
                    state = 1;
                }
                writer
                    .write_event(Event::End(e.clone()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::Eof) => break,
            Ok(e) => {
                writer
                    .write_event(e)
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Err(e) => return Err(SlimError::XmlParseError { message: e.to_string() }),
        }
        buf_event.clear();
    }
    
    Ok(writer.into_inner().into_inner())
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
