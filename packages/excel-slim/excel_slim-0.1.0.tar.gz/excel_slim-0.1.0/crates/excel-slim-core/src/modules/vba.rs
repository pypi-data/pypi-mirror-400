use crate::detector::FileProfile;
use crate::error::SlimError;
use crate::modules::{Module, ModuleContext};
use crate::pipeline::Options;
use crate::report::ModuleResult;

#[derive(Debug, Default)]
pub struct VbaModule;

impl Module for VbaModule {
    fn name(&self) -> &'static str {
        "vba"
    }

    fn is_applicable(&self, _profile: &FileProfile, _options: &Options) -> bool {
        false
    }

    fn run(&self, _ctx: &ModuleContext<'_>) -> Result<ModuleResult, SlimError> {
        Err(SlimError::Internal {
            message: "vba compression not implemented".to_string(),
        })
    }
}
