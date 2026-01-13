use std::fs;
use std::path::{Path, PathBuf};

use tempfile::TempDir;

use crate::detector::{detect_path, FileProfile};
use crate::error::SlimError;
use crate::formats::WorkbookFormat;
use crate::modules::{ContainerZip, Module, ModuleContext};
use crate::report::OptimizationReport;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Profile {
    Safe,
    Balanced,
    Aggressive,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VbaMode {
    Auto,
    Off,
    On,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MediaMode {
    Off,
    Lossless,
    Lossy,
}

#[derive(Debug, Clone)]
pub struct Options {
    pub profile: Profile,
    pub xml: bool,
    pub zip: bool,
    pub vba: VbaMode,
    pub media: MediaMode,
}

impl Default for Options {
    fn default() -> Self {
        Options {
            profile: Profile::Safe,
            xml: true,
            zip: true,
            vba: VbaMode::Auto,
            media: MediaMode::Off,
        }
    }
}

pub fn run_pipeline(
    input_path: &Path,
    output_path: Option<&Path>,
    options: Options,
) -> Result<OptimizationReport, SlimError> {
    let profile = detect_path(input_path)?;

    let output_path = match output_path {
        Some(path) => path.to_path_buf(),
        None => default_output_path(input_path),
    };

    let original_size = fs::metadata(input_path)
        .map_err(|err| SlimError::io(&input_path.to_path_buf(), err))?
        .len();

    let warnings = Vec::new();
    let mut notes = Vec::new();

    let modules = plan_modules(&profile, &options);
    if modules.is_empty() {
        if input_path != output_path {
            fs::copy(input_path, &output_path)
                .map_err(|err| SlimError::io(&output_path.to_path_buf(), err))?;
        }
        notes.push("no optimizations applied".to_string());

        let final_size = fs::metadata(&output_path)
            .map_err(|err| SlimError::io(&output_path.to_path_buf(), err))?
            .len();

        return Ok(OptimizationReport::new(
            input_path,
            &output_path,
            profile.format,
            original_size,
            final_size,
            Vec::new(),
            warnings,
            notes,
        ));
    }

    let temp_dir = TempDir::new().map_err(|err| SlimError::Internal {
        message: format!("temp dir: {err}"),
    })?;
    let in_place = input_path == output_path;
    let final_output = if in_place {
        temp_dir.path().join("final.zip")
    } else {
        output_path.clone()
    };

    let mut current_input = input_path.to_path_buf();
    let mut module_results = Vec::new();

    for (index, module) in modules.iter().enumerate() {
        let is_last = index == modules.len() - 1;
        let next_output = if is_last {
            final_output.clone()
        } else {
            temp_dir.path().join(format!("stage-{index}.zip"))
        };

        let context = ModuleContext {
            input_path: &current_input,
            output_path: &next_output,
            file_profile: &profile,
            options: &options,
        };

        let result = module.run(&context)?;
        module_results.push(result);
        current_input = next_output;
    }

    if in_place {
        fs::rename(&final_output, &output_path)
            .map_err(|err| SlimError::io(&output_path.to_path_buf(), err))?;
    }

    let final_size = fs::metadata(&output_path)
        .map_err(|err| SlimError::io(&output_path.to_path_buf(), err))?
        .len();

    Ok(OptimizationReport::new(
        input_path,
        &output_path,
        profile.format,
        original_size,
        final_size,
        module_results,
        warnings,
        notes,
    ))
}

fn plan_modules(profile: &FileProfile, options: &Options) -> Vec<Box<dyn Module>> {
    let mut modules: Vec<Box<dyn Module>> = Vec::new();

    if options.xml && matches!(profile.format, WorkbookFormat::Xlsx | WorkbookFormat::Xlsm) {
        modules.push(Box::new(crate::modules::xml_shared_strings::XmlSharedStrings));
    }

    if options.xml
        && options.profile != Profile::Safe
        && matches!(profile.format, WorkbookFormat::Xlsx | WorkbookFormat::Xlsm)
    {
        modules.push(Box::new(crate::modules::xml_styles::XmlStyles));
    }

    if options.xml
        && options.profile == Profile::Aggressive
        && matches!(profile.format, WorkbookFormat::Xlsx | WorkbookFormat::Xlsm)
    {
        modules.push(Box::new(crate::modules::xml_minify::XmlMinify));
    }

    if !matches!(options.media, MediaMode::Off)
        && matches!(profile.format, WorkbookFormat::Xlsx | WorkbookFormat::Xlsm)
    {
        modules.push(Box::new(crate::modules::media::MediaModule));
    }

    if options.zip && matches!(profile.format, WorkbookFormat::Xlsx | WorkbookFormat::Xlsm) {
        modules.push(Box::new(ContainerZip::default()));
    }

    modules
}

fn default_output_path(input_path: &Path) -> PathBuf {
    let stem = input_path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("workbook");
    let extension = input_path.extension().and_then(|s| s.to_str());

    match extension {
        Some(ext) => input_path.with_file_name(format!("{stem}.slim.{ext}")),
        None => input_path.with_file_name(format!("{stem}.slim")),
    }
}
