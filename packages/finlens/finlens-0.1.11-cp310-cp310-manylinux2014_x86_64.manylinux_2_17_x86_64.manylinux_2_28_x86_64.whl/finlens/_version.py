from __future__ import annotations

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover - Python <3.8
    from importlib_metadata import PackageNotFoundError, version  # type: ignore


def _resolve_version() -> str:
    try:
        return version("finlens")
    except PackageNotFoundError:
        return "0.0.0"


__all__ = ["__version__"]
__version__ = _resolve_version()
