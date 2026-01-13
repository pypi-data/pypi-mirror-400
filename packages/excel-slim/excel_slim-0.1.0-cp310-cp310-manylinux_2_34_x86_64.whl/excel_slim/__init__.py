import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from . import _native
except Exception as exc:  # pragma: no cover
    raise ImportError("excel_slim native module is not available") from exc


class ExcelSlimError(Exception):
    def __init__(self, message: str, kind: Optional[str] = None) -> None:
        super().__init__(message)
        self.kind = kind


@dataclass
class OptimizationReport:
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)

    def to_json(self) -> str:
        return json.dumps(self.data)


class WorkbookOptimizer:
    def __init__(self, path: str) -> None:
        self._path = path
        self._options: Dict[str, Any] = {
            "profile": "safe",
            "xml": True,
            "zip": True,
            "vba": "auto",
            "media": "off",
        }

    def profile(self, value: str) -> "WorkbookOptimizer":
        self._options["profile"] = value
        return self

    def xml(self, value: bool) -> "WorkbookOptimizer":
        self._options["xml"] = bool(value)
        return self

    def zip(self, value: bool) -> "WorkbookOptimizer":
        self._options["zip"] = bool(value)
        return self

    def vba(self, value: str) -> "WorkbookOptimizer":
        self._options["vba"] = value
        return self

    def media(self, value: str) -> "WorkbookOptimizer":
        self._options["media"] = value
        return self

    def optimize(self, output: Optional[str] = None) -> OptimizationReport:
        return optimize(self._path, output=output, **self._options)


def _parse_kind(message: str) -> Optional[str]:
    if not message.startswith("kind="):
        return None
    prefix, _, rest = message.partition(":")
    _, _, kind = prefix.partition("=")
    return kind.strip() or None


def _raise_wrapped(exc: Exception) -> None:
    message = str(exc)
    kind = _parse_kind(message)
    if kind is not None and ":" in message:
        _, _, rest = message.partition(":")
        message = rest.strip()
    raise ExcelSlimError(message, kind=kind) from exc


def analyze(path: str) -> Dict[str, Any]:
    try:
        payload = _native.analyze_json(path)
    except Exception as exc:
        _raise_wrapped(exc)
    return json.loads(payload)


def optimize(
    path: str,
    output: Optional[str] = None,
    profile: str = "safe",
    xml: bool = True,
    zip: bool = True,
    vba: str = "auto",
    media: str = "off",
    report: bool = True,
    report_format: str = "dict",
) -> OptimizationReport:
    options = {
        "profile": profile,
        "xml": xml,
        "zip": zip,
        "vba": vba,
        "media": media,
    }
    try:
        payload = _native.optimize_json(path, output, options)
    except Exception as exc:
        _raise_wrapped(exc)
    data = json.loads(payload)
    return OptimizationReport(data)


__all__ = [
    "ExcelSlimError",
    "OptimizationReport",
    "WorkbookOptimizer",
    "analyze",
    "optimize",
]
