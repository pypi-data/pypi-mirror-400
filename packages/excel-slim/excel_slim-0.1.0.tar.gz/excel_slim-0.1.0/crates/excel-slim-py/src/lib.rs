use pyo3::prelude::*;
use pyo3::types::PyDict;

use excel_slim_core::{analyze_path, optimize_path, MediaMode, Options, Profile, SlimError, VbaMode};

#[pyfunction]
fn analyze_json(path: &str) -> PyResult<String> {
    match analyze_path(std::path::Path::new(path)) {
        Ok(report) => serde_json::to_string(&report)
            .map_err(|err| SlimError::Internal { message: err.to_string() })
            .map_err(to_py_err),
        Err(err) => Err(to_py_err(err)),
    }
}

#[pyfunction]
fn optimize_json(path: &str, output: Option<&str>, options: Option<&PyDict>) -> PyResult<String> {
    let opts = parse_options(options)?;
    match optimize_path(
        std::path::Path::new(path),
        output.map(std::path::Path::new),
        opts,
    ) {
        Ok(report) => serde_json::to_string(&report)
            .map_err(|err| SlimError::Internal { message: err.to_string() })
            .map_err(to_py_err),
        Err(err) => Err(to_py_err(err)),
    }
}

fn parse_options(options: Option<&PyDict>) -> PyResult<Options> {
    let mut opts = Options::default();
    let Some(dict) = options else {
        return Ok(opts);
    };

    if let Ok(Some(profile)) = dict.get_item("profile") {
        let value: String = profile.extract()?;
        opts.profile = match value.as_str() {
            "safe" => Profile::Safe,
            "balanced" => Profile::Balanced,
            "aggressive" => Profile::Aggressive,
            other => {
                return Err(to_py_err(SlimError::InvalidOptions {
                    message: format!("unknown profile: {other}"),
                }))
            }
        };
    }

    if let Ok(Some(xml)) = dict.get_item("xml") {
        opts.xml = xml.extract()?;
    }

    if let Ok(Some(zip)) = dict.get_item("zip") {
        opts.zip = zip.extract()?;
    }

    if let Ok(Some(vba)) = dict.get_item("vba") {
        let value: String = vba.extract()?;
        opts.vba = match value.as_str() {
            "auto" => VbaMode::Auto,
            "off" => VbaMode::Off,
            "on" => VbaMode::On,
            other => {
                return Err(to_py_err(SlimError::InvalidOptions {
                    message: format!("unknown vba mode: {other}"),
                }))
            }
        };
    }

    if let Ok(Some(media)) = dict.get_item("media") {
        let value: String = media.extract()?;
        opts.media = match value.as_str() {
            "off" => MediaMode::Off,
            "lossless" => MediaMode::Lossless,
            "lossy" => MediaMode::Lossy,
            other => {
                return Err(to_py_err(SlimError::InvalidOptions {
                    message: format!("unknown media mode: {other}"),
                }))
            }
        };
    }

    Ok(opts)
}

fn to_py_err(err: SlimError) -> PyErr {
    pyo3::exceptions::PyRuntimeError::new_err(err.to_string())
}

#[pymodule]
fn _native(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(analyze_json, m)?)?;
    m.add_function(wrap_pyfunction!(optimize_json, m)?)?;
    Ok(())
}
