use std::fs::File;
use std::io::{self, Write};
use std::path::Path;

use zip::read::ZipFile;
use zip::write::FileOptions;
use zip::{CompressionMethod, DateTime, ZipArchive, ZipWriter};

use crate::detector::FileProfile;
use crate::error::SlimError;
use crate::modules::{Module, ModuleContext};
use crate::pipeline::{Options, Profile};
use crate::report::ModuleResult;

const ZIP_BALANCED_LEVEL: i32 = 7;
const ZIP_BEST_LEVEL: i32 = 9;
const ZIP_SAFE_LEVEL: i32 = 6;

#[derive(Debug, Default)]
pub struct ContainerZip;

impl Module for ContainerZip {
    fn name(&self) -> &'static str {
        "container_zip"
    }

    fn is_applicable(&self, _profile: &FileProfile, _options: &Options) -> bool {
        true
    }

    fn run(&self, ctx: &ModuleContext<'_>) -> Result<ModuleResult, SlimError> {
        let before = std::fs::metadata(ctx.input_path)
            .map_err(|err| SlimError::io(&ctx.input_path.to_path_buf(), err))?
            .len();

        let level = compression_level(ctx.options.profile);
        repack_zip(ctx.input_path, ctx.output_path, level)?;

        let after = std::fs::metadata(ctx.output_path)
            .map_err(|err| SlimError::io(&ctx.output_path.to_path_buf(), err))?
            .len();

        Ok(ModuleResult::new(
            self.name(),
            before,
            after,
            Vec::new(),
            Vec::new(),
        ))
    }
}

fn repack_zip(input_path: &Path, output_path: &Path, level: i32) -> Result<(), SlimError> {
    let input_file = File::open(input_path)
        .map_err(|err| SlimError::io(&input_path.to_path_buf(), err))?;
    let mut archive = ZipArchive::new(input_file)
        .map_err(|err| SlimError::InvalidZip { message: err.to_string() })?;

    let mut names = Vec::with_capacity(archive.len());
    for i in 0..archive.len() {
        let entry = archive
            .by_index(i)
            .map_err(|err| SlimError::InvalidZip { message: err.to_string() })?;
        names.push(entry.name().to_string());
    }
    names.sort();

    let output_file = File::create(output_path)
        .map_err(|err| SlimError::io(&output_path.to_path_buf(), err))?;
    let mut writer = ZipWriter::new(output_file);

    let fixed_time = DateTime::from_date_and_time(1980, 1, 1, 0, 0, 0).map_err(|_| {
        SlimError::Internal {
            message: "failed to build fixed timestamp".to_string(),
        }
    })?;

    for name in names {
        validate_zip_name(input_path, &name)?;
        let mut entry = archive
            .by_name(&name)
            .map_err(|err| SlimError::InvalidZip { message: err.to_string() })?;

        if entry.name().ends_with('/') {
            continue;
        }

        let mut options = FileOptions::default()
            .compression_method(CompressionMethod::Deflated)
            .compression_level(Some(level))
            .last_modified_time(fixed_time);

        if let Some(mode) = entry.unix_mode() {
            options = options.unix_permissions(mode);
        }

        writer
            .start_file(name, options)
            .map_err(|err| SlimError::InvalidZip { message: err.to_string() })?;
        copy_entry(&mut entry, &mut writer)?;
    }

    writer
        .finish()
        .map_err(|err| SlimError::InvalidZip { message: err.to_string() })?;

    Ok(())
}

fn copy_entry(entry: &mut ZipFile<'_>, writer: &mut ZipWriter<File>) -> Result<(), SlimError> {
    io::copy(entry, writer).map_err(|err| SlimError::InvalidZip {
        message: format!("zip copy failed: {err}"),
    })?;
    writer
        .flush()
        .map_err(|err| SlimError::InvalidZip { message: err.to_string() })?;
    Ok(())
}

fn compression_level(profile: Profile) -> i32 {
    match profile {
        Profile::Safe => ZIP_SAFE_LEVEL,
        Profile::Balanced => ZIP_BALANCED_LEVEL,
        Profile::Aggressive => ZIP_BEST_LEVEL,
    }
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
