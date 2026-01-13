use serde::Serialize;
use std::path::Path;

use crate::formats::WorkbookFormat;
use crate::detector::FileProfile;

#[derive(Debug, Serialize, Clone)]
pub struct XmlStats {
    pub worksheets: usize,
    pub shared_strings_bytes: u64,
    pub styles_bytes: u64,
}

#[derive(Debug, Serialize, Clone)]
pub struct ModuleResult {
    pub name: String,
    pub bytes_before: u64,
    pub bytes_after: u64,
    pub delta_bytes: i64,
    pub delta_percent: f64,
    pub notes: Vec<String>,
    pub warnings: Vec<String>,
}

impl ModuleResult {
    pub fn new(
        name: impl Into<String>,
        bytes_before: u64,
        bytes_after: u64,
        notes: Vec<String>,
        warnings: Vec<String>,
    ) -> Self {
        let delta_bytes = bytes_after as i64 - bytes_before as i64;
        let delta_percent = percent_delta(bytes_before, bytes_after);
        ModuleResult {
            name: name.into(),
            bytes_before,
            bytes_after,
            delta_bytes,
            delta_percent,
            notes,
            warnings,
        }
    }
}

#[derive(Debug, Serialize, Clone)]
pub struct OptimizationReport {
    pub input_path: String,
    pub output_path: String,
    pub format: String,
    pub original_size_bytes: u64,
    pub final_size_bytes: u64,
    pub delta_bytes: i64,
    pub delta_percent: f64,
    pub modules: Vec<ModuleResult>,
    pub warnings: Vec<String>,
    pub notes: Vec<String>,
}

impl OptimizationReport {
    pub fn new(
        input_path: &Path,
        output_path: &Path,
        format: WorkbookFormat,
        original_size_bytes: u64,
        final_size_bytes: u64,
        modules: Vec<ModuleResult>,
        warnings: Vec<String>,
        notes: Vec<String>,
    ) -> Self {
        let delta_bytes = final_size_bytes as i64 - original_size_bytes as i64;
        let delta_percent = percent_delta(original_size_bytes, final_size_bytes);
        OptimizationReport {
            input_path: input_path.display().to_string(),
            output_path: output_path.display().to_string(),
            format: format.as_str().to_string(),
            original_size_bytes,
            final_size_bytes,
            delta_bytes,
            delta_percent,
            modules,
            warnings,
            notes,
        }
    }
}

#[derive(Debug, Serialize, Clone)]
pub struct AnalysisReport {
    pub format: String,
    pub size_bytes: u64,
    pub has_vba: bool,
    pub has_media: bool,
    pub xml_stats: XmlStats,
    pub recommendations: Vec<String>,
    pub risks: Vec<String>,
}

impl AnalysisReport {
    pub fn from_profile(profile: &FileProfile) -> Self {
        let mut recommendations = Vec::new();
        let mut risks = Vec::new();

        if profile.xml_stats.shared_strings_bytes > 0 {
            recommendations.push("xml_shared_strings".to_string());
        }
        if profile.xml_stats.styles_bytes > 0 {
            recommendations.push("xml_styles".to_string());
        }
        if profile.has_vba {
            recommendations.push("vba".to_string());
        }
        if profile.has_media {
            recommendations.push("media".to_string());
            risks.push("lossy media disabled".to_string());
        }

        AnalysisReport {
            format: profile.format.as_str().to_string(),
            size_bytes: profile.size_bytes,
            has_vba: profile.has_vba,
            has_media: profile.has_media,
            xml_stats: profile.xml_stats.clone(),
            recommendations,
            risks,
        }
    }
}

fn percent_delta(original: u64, final_size: u64) -> f64 {
    if original == 0 {
        return 0.0;
    }
    let delta = final_size as f64 - original as f64;
    (delta / original as f64) * 100.0
}
