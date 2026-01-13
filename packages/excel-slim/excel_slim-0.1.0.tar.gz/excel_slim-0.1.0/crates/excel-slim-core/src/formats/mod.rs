use serde::Serialize;
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum WorkbookFormat {
    Xlsx,
    Xlsm,
    Xls,
    Csv,
    Unknown,
}

impl WorkbookFormat {
    pub fn as_str(&self) -> &'static str {
        match self {
            WorkbookFormat::Xlsx => "xlsx",
            WorkbookFormat::Xlsm => "xlsm",
            WorkbookFormat::Xls => "xls",
            WorkbookFormat::Csv => "csv",
            WorkbookFormat::Unknown => "unknown",
        }
    }
}

impl fmt::Display for WorkbookFormat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}

pub mod xls;
pub mod xlsm;
pub mod xlsx;
