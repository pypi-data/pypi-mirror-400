use std::fs::File;
use std::io::Read;
use std::path::Path;

use zip::ZipArchive;

use crate::error::SlimError;
use crate::formats::WorkbookFormat;
use crate::report::XmlStats;

const ZIP_MAGIC: [u8; 2] = [0x50, 0x4b];
const OLE_MAGIC: [u8; 8] = [0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1, 0x1a, 0xe1];

#[derive(Debug, Clone)]
pub struct FileProfile {
    pub format: WorkbookFormat,
    pub size_bytes: u64,
    pub has_vba: bool,
    pub has_media: bool,
    pub xml_stats: XmlStats,
}

pub fn detect_path(path: &Path) -> Result<FileProfile, SlimError> {
    let metadata = std::fs::metadata(path).map_err(|err| SlimError::io(&path.to_path_buf(), err))?;
    let size_bytes = metadata.len();

    let mut file = File::open(path).map_err(|err| SlimError::io(&path.to_path_buf(), err))?;
    let mut magic = [0u8; 8];
    let read = file.read(&mut magic).map_err(|err| SlimError::io(&path.to_path_buf(), err))?;
    let magic = &magic[..read];

    if magic.starts_with(&ZIP_MAGIC) {
        return detect_zip(path, size_bytes);
    }

    if magic == OLE_MAGIC.as_slice() {
        return Ok(FileProfile {
            format: WorkbookFormat::Xls,
            size_bytes,
            has_vba: false,
            has_media: false,
            xml_stats: XmlStats {
                worksheets: 0,
                shared_strings_bytes: 0,
                styles_bytes: 0,
            },
        });
    }

    if let Some(ext) = path.extension().and_then(|s| s.to_str()) {
        if ext.eq_ignore_ascii_case("csv") {
            return Ok(FileProfile {
                format: WorkbookFormat::Csv,
                size_bytes,
                has_vba: false,
                has_media: false,
                xml_stats: XmlStats {
                    worksheets: 0,
                    shared_strings_bytes: 0,
                    styles_bytes: 0,
                },
            });
        }
    }

    Ok(FileProfile {
        format: WorkbookFormat::Unknown,
        size_bytes,
        has_vba: false,
        has_media: false,
        xml_stats: XmlStats {
            worksheets: 0,
            shared_strings_bytes: 0,
            styles_bytes: 0,
        },
    })
}

fn detect_zip(path: &Path, size_bytes: u64) -> Result<FileProfile, SlimError> {
    let file = File::open(path).map_err(|err| SlimError::io(&path.to_path_buf(), err))?;
    let mut archive = ZipArchive::new(file)
        .map_err(|err| SlimError::InvalidZip { message: err.to_string() })?;

    let mut has_content_types = false;
    let mut has_vba = false;
    let mut has_media = false;
    let mut worksheets = 0usize;
    let mut shared_strings_bytes = 0u64;
    let mut styles_bytes = 0u64;

    for i in 0..archive.len() {
        let entry = archive
            .by_index(i)
            .map_err(|err| SlimError::InvalidZip { message: err.to_string() })?;
        let name = entry.name().to_string();
        validate_zip_name(path, &name)?;

        if name == "[Content_Types].xml" {
            has_content_types = true;
        }
        if name == "xl/vbaProject.bin" {
            has_vba = true;
        }
        if name.starts_with("xl/media/") {
            has_media = true;
        }
        if name.starts_with("xl/worksheets/") && name.ends_with(".xml") {
            worksheets += 1;
        }
        if name == "xl/sharedStrings.xml" {
            shared_strings_bytes = entry.size();
        }
        if name == "xl/styles.xml" {
            styles_bytes = entry.size();
        }
    }

    let format = if has_content_types {
        if has_vba {
            WorkbookFormat::Xlsm
        } else {
            WorkbookFormat::Xlsx
        }
    } else {
        WorkbookFormat::Unknown
    };

    Ok(FileProfile {
        format,
        size_bytes,
        has_vba,
        has_media,
        xml_stats: XmlStats {
            worksheets,
            shared_strings_bytes,
            styles_bytes,
        },
    })
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
