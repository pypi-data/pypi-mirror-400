# excel-slim

Excel file optimization with a Rust core and a Python-first API. The default path is lossless and deterministic, with optional lossy media optimization when explicitly enabled.

## Highlights

- Python API: `excel_slim.optimize()` and `excel_slim.analyze()`
- CLI mirrors Python options (no subprocess in Python)
- Lossless by default, lossy media is opt-in
- Deterministic output (stable ordering, timestamps)
- Handles `.xlsx` and `.xlsm` (VBA pass-through)

## Install

### Python (published on PyPI)

```bash
pip install excel-slim
```

### Python (from source)

```bash
python -m pip install maturin
maturin develop
```

### CLI (from source)

```bash
cargo build -p excel-slim-cli --release
./target/release/excel-slim --help
```

## Quick start

### Python

```python
import excel_slim

report = excel_slim.optimize(
    "input.xlsx",
    output="output.xlsx",
    profile="safe",
    xml=True,
    zip=True,
    vba="auto",
    media="off",
)

info = excel_slim.analyze("input.xlsm")
```

### CLI

```bash
excel-slim input.xlsx --report
excel-slim input.xlsm --xml --zip --vba=auto --media=lossless --report=json
```

## Python API

### analyze

```python
info = excel_slim.analyze("input.xlsx")
```

Returns a dict with:
- `format`: `xlsx|xlsm|xls|csv|unknown`
- `size_bytes`
- `has_vba`, `has_media`
- `xml_stats`: worksheets, shared strings size, styles size
- `recommendations`, `risks`

### optimize

```python
report = excel_slim.optimize(
    "input.xlsx",
    output="output.xlsx",
    profile="safe",        # safe | balanced | aggressive
    xml=True,               # XML optimizations
    zip=True,               # ZIP repack
    vba="auto",            # auto | off | on
    media="off",           # off | lossless | lossy
    report=True,
    report_format="dict",  # dict | json_string
)
```

`optimize()` returns an `OptimizationReport` with per-module savings and metadata.

### Convenience API

```python
from excel_slim import WorkbookOptimizer

opt = WorkbookOptimizer("input.xlsx")
opt.profile("safe").xml(True).zip(True).media("lossless")
report = opt.optimize("output.xlsx")
```

## Profiles

- `safe`: fast, lossless only. Skips heavy XML passes.
- `balanced`: enables style pruning for additional savings.
- `aggressive`: enables XML minify and best compression (slowest).

## Determinism

- Stable ZIP ordering
- Fixed timestamps
- Consistent compression settings by profile

## Safety

- Never executes macros or formulas
- VBA streams are preserved as-is
- Zip entry validation prevents path traversal

## Development

### Requirements

- Rust 1.70+
- Python 3.8+
- maturin (`python -m pip install maturin`)

### Build + test

```bash
cargo test
python -m pytest
```

## Publish (PyPI)

This uses maturin to build and publish wheels.

```bash
maturin build --release
maturin publish --release
```

Set your token in the environment before publishing:

```bash
export MATURIN_PYPI_TOKEN="pypi-..."
```

## Roadmap

See the engineering plan in the project brief for shared strings, styles pruning, VBA compression, media optimization, and XLS support phases.
