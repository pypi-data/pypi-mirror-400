use std::path::PathBuf;

use thiserror::Error;

#[derive(Debug, Error)]
pub enum SlimError {
    #[error("kind=io: {message}")]
    Io {
        message: String,
        #[source]
        source: std::io::Error,
    },
    #[error("kind=unsupported_format: {message}")]
    UnsupportedFormat { message: String },
    #[error("kind=invalid_zip: {message}")]
    InvalidZip { message: String },
    #[error("kind=xml_parse_error: {message}")]
    XmlParseError { message: String },
    #[error("kind=invalid_options: {message}")]
    InvalidOptions { message: String },
    #[error("kind=internal: {message}")]
    Internal { message: String },
}

impl SlimError {
    pub fn kind(&self) -> &'static str {
        match self {
            SlimError::Io { .. } => "io",
            SlimError::UnsupportedFormat { .. } => "unsupported_format",
            SlimError::InvalidZip { .. } => "invalid_zip",
            SlimError::XmlParseError { .. } => "xml_parse_error",
            SlimError::InvalidOptions { .. } => "invalid_options",
            SlimError::Internal { .. } => "internal",
        }
    }

    pub fn io(path: &PathBuf, source: std::io::Error) -> Self {
        SlimError::Io {
            message: format!("{}: {}", path.display(), source),
            source,
        }
    }
}
