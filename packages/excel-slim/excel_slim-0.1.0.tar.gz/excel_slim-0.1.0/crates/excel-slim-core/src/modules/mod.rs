use crate::detector::FileProfile;
use crate::error::SlimError;
use crate::pipeline::Options;
use crate::report::ModuleResult;
use std::path::Path;

pub mod container_zip;
pub mod media;
pub mod vba;
pub mod xml_minify;
pub mod xml_shared_strings;
pub mod xml_styles;

pub use container_zip::ContainerZip;

pub struct ModuleContext<'a> {
    pub input_path: &'a Path,
    pub output_path: &'a Path,
    pub file_profile: &'a FileProfile,
    pub options: &'a Options,
}

pub trait Module {
    fn name(&self) -> &'static str;
    fn is_applicable(&self, profile: &FileProfile, options: &Options) -> bool;
    fn run(&self, ctx: &ModuleContext<'_>) -> Result<ModuleResult, SlimError>;
}
