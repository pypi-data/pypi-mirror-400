mod detector;
mod error;
mod pipeline;
mod report;

pub mod formats;
pub mod modules;

pub use error::SlimError;
pub use pipeline::{MediaMode, Options, Profile, VbaMode};
pub use report::{AnalysisReport, ModuleResult, OptimizationReport, XmlStats};

use std::path::Path;

pub fn analyze_path(path: &Path) -> Result<AnalysisReport, SlimError> {
    let profile = detector::detect_path(path)?;
    Ok(AnalysisReport::from_profile(&profile))
}

pub fn optimize_path(
    input_path: &Path,
    output_path: Option<&Path>,
    options: Options,
) -> Result<OptimizationReport, SlimError> {
    pipeline::run_pipeline(input_path, output_path, options)
}
