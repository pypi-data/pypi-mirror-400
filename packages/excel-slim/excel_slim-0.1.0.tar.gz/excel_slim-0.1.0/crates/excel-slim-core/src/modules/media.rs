use crate::detector::FileProfile;
use crate::error::SlimError;
use crate::modules::{Module, ModuleContext};
use crate::pipeline::{MediaMode, Options};
use crate::report::ModuleResult;
use image::codecs::jpeg::JpegEncoder;
use image::codecs::png::{CompressionType, FilterType, PngEncoder};
use image::{GenericImageView, ImageEncoder, ImageFormat};
use std::fs::File;
use std::io::{BufReader, BufWriter, Read, Write};
use std::path::Path;
use zip::write::FileOptions;
use zip::{CompressionMethod, DateTime, ZipArchive, ZipWriter};

const JPEG_QUALITY: u8 = 85;
#[derive(Debug, Default)]
pub struct MediaModule;

impl Module for MediaModule {
    fn name(&self) -> &'static str {
        "media"
    }

    fn is_applicable(&self, _profile: &FileProfile, options: &Options) -> bool {
        !matches!(options.media, MediaMode::Off)
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
        let mut lossy = 0usize;
        let mut warnings = Vec::new();

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

            if name.starts_with("xl/media/") {
                let mut buf = Vec::new();
                file.read_to_end(&mut buf)
                    .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
                let original_len = buf.len();
                let (data, used_lossy, warn) = optimize_media(&name, &buf, ctx.options.media);
                if let Some(warn) = warn {
                    warnings.push(warn);
                }
                let data = if data.len() >= original_len { &buf } else { &data };
                writer
                    .write_all(data)
                    .map_err(|e| SlimError::io(&ctx.output_path.to_path_buf(), e))?;
                touched += 1;
                if used_lossy {
                    lossy += 1;
                }
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
            vec!["skipped (no media files)".to_string()]
        } else if lossy > 0 {
            vec![format!("optimized media: {touched} (lossy: {lossy})")]
        } else {
            vec![format!("optimized media: {touched}")]
        };

        Ok(ModuleResult::new(self.name(), before, after, notes, warnings))
    }
}

fn optimize_media(name: &str, data: &[u8], mode: MediaMode) -> (Vec<u8>, bool, Option<String>) {
    let ext = Path::new(name)
        .extension()
        .and_then(|s| s.to_str())
        .unwrap_or("")
        .to_ascii_lowercase();

    match ext.as_str() {
        "png" => match encode_png(data) {
            Ok(out) => (out, false, None),
            Err(err) => (data.to_vec(), false, Some(err)),
        },
        "jpg" | "jpeg" => match mode {
            MediaMode::Lossy => match encode_jpeg_lossy(data, JPEG_QUALITY) {
                Ok(out) => (out, true, None),
                Err(err) => (data.to_vec(), false, Some(err)),
            },
            _ => (data.to_vec(), false, None),
        },
        _ => (data.to_vec(), false, None),
    }
}

fn encode_png(data: &[u8]) -> Result<Vec<u8>, String> {
    let image = image::load_from_memory_with_format(data, ImageFormat::Png)
        .map_err(|e| format!("png decode failed: {e}"))?;
    let (width, height) = image.dimensions();
    let color = image.color();
    let raw = image.into_bytes();
    let mut out = Vec::new();
    let encoder = PngEncoder::new_with_quality(&mut out, CompressionType::Best, FilterType::Adaptive);
    encoder
        .write_image(&raw, width, height, color.into())
        .map_err(|e| format!("png encode failed: {e}"))?;
    Ok(out)
}

fn encode_jpeg_lossy(data: &[u8], quality: u8) -> Result<Vec<u8>, String> {
    let image = image::load_from_memory_with_format(data, ImageFormat::Jpeg)
        .map_err(|e| format!("jpeg decode failed: {e}"))?;
    let mut out = Vec::new();
    let mut encoder = JpegEncoder::new_with_quality(&mut out, quality);
    encoder
        .encode_image(&image)
        .map_err(|e| format!("jpeg encode failed: {e}"))?;
    Ok(out)
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
