use crate::detector::FileProfile;
use crate::error::SlimError;
use crate::modules::{Module, ModuleContext};
use crate::pipeline::{Options, Profile};
use crate::report::ModuleResult;
use quick_xml::events::Event;
use quick_xml::{Reader, Writer};
use std::fs::File;
use std::io::{BufReader, BufWriter, Read, Write};
use std::path::Path;
use zip::write::FileOptions;
use zip::{CompressionMethod, DateTime, ZipArchive, ZipWriter};

#[derive(Debug, Default)]
pub struct XmlMinify;

impl Module for XmlMinify {
    fn name(&self) -> &'static str {
        "xml_minify"
    }

    fn is_applicable(&self, _profile: &FileProfile, options: &Options) -> bool {
        options.xml && options.profile == Profile::Aggressive
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

        let output_file = File::create(ctx.output_path)
            .map_err(|err| SlimError::io(&ctx.output_path.to_path_buf(), err))?;
        let mut writer = ZipWriter::new(BufWriter::new(output_file));

        let fixed_time = DateTime::from_date_and_time(1980, 1, 1, 0, 0, 0).map_err(|_| {
            SlimError::Internal {
                message: "failed to build fixed timestamp".to_string(),
            }
        })?;

        let mut touched = 0usize;

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

            if name.ends_with(".xml") {
                let mut original = Vec::new();
                file.read_to_end(&mut original)
                    .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
                let minified = minify_xml(&original)?;
                let data = if minified.len() < original.len() {
                    touched += 1;
                    minified
                } else {
                    original
                };
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

        let notes = if touched == 0 {
            vec!["skipped (no xml savings)".to_string()]
        } else {
            vec![format!("minified xml files: {touched}")]
        };

        Ok(ModuleResult::new(self.name(), before, after, notes, Vec::new()))
    }
}

fn minify_xml(buf: &[u8]) -> Result<Vec<u8>, SlimError> {
    let mut xml_reader = Reader::from_reader(buf);
    xml_reader.trim_text(false);

    let mut writer = Writer::new(Vec::new());
    let mut buf_event = Vec::new();
    let mut preserve_stack: Vec<bool> = Vec::new();

    loop {
        let event = xml_reader.read_event_into(&mut buf_event);
        match event {
            Ok(Event::Start(ref e)) => {
                let preserve = should_preserve_whitespace(e, preserve_stack.last().copied());
                preserve_stack.push(preserve);
                writer
                    .write_event(Event::Start(e.to_owned()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::Empty(ref e)) => {
                writer
                    .write_event(Event::Empty(e.to_owned()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::End(ref e)) => {
                preserve_stack.pop();
                writer
                    .write_event(Event::End(e.to_owned()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::Text(ref e)) => {
                let preserve = preserve_stack.last().copied().unwrap_or(false);
                if preserve || !is_whitespace_only(e.as_ref()) {
                    writer
                        .write_event(Event::Text(e.to_owned()))
                        .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
                }
            }
            Ok(Event::CData(ref e)) => {
                writer
                    .write_event(Event::CData(e.to_owned()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::Decl(ref e)) => {
                writer
                    .write_event(Event::Decl(e.to_owned()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::DocType(ref e)) => {
                writer
                    .write_event(Event::DocType(e.to_owned()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::PI(ref e)) => {
                writer
                    .write_event(Event::PI(e.to_owned()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::Comment(ref e)) => {
                writer
                    .write_event(Event::Comment(e.to_owned()))
                    .map_err(|e| SlimError::XmlParseError { message: e.to_string() })?;
            }
            Ok(Event::Eof) => break,
            Err(e) => {
                return Err(SlimError::XmlParseError {
                    message: e.to_string(),
                })
            }
        }
        buf_event.clear();
    }

    Ok(writer.into_inner())
}

fn should_preserve_whitespace(
    elem: &quick_xml::events::BytesStart<'_>,
    parent_preserve: Option<bool>,
) -> bool {
    let mut preserve = parent_preserve.unwrap_or(false);
    if elem.name().as_ref() == b"t" {
        preserve = true;
    }
    for attr in elem.attributes().flatten() {
        if attr.key.as_ref() == b"xml:space" && attr.value.as_ref() == b"preserve" {
            preserve = true;
        }
    }
    preserve
}

fn is_whitespace_only(bytes: &[u8]) -> bool {
    bytes.iter().all(|b| matches!(b, b' ' | b'\n' | b'\r' | b'\t'))
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
