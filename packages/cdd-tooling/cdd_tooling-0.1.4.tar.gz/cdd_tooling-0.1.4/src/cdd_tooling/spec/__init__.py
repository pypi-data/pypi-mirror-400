# src/cdd_tooling/spec/__init__.py
"""Spec and version loading utilities."""
from __future__ import annotations
from importlib import metadata
from pathlib import Path

# The CDD spec version this tooling implements
SPEC_VERSION = "1.1.5"


def get_tool_version() -> str:
    """Get the CDD spec version (what this tooling implements)."""
    return SPEC_VERSION


def get_tooling_version() -> str:
    """Get the tooling package version."""
    try:
        return metadata.version("cdd-tooling")
    except metadata.PackageNotFoundError:
        # Development mode - read from pyproject.toml
        return "0.1.1"


def load_schema_version() -> str:
    """Return the report schema version (coupled to spec version for v1.x)."""
    parts = SPEC_VERSION.split(".")
    return f"{parts[0]}.0" if len(parts) >= 1 else "1.0"


def load_spec_text() -> str:
    """Load the full SPEC.md text."""
    # Try installed package data first
    try:
        from importlib.resources import files
        return files("cdd_tooling.spec").joinpath("SPEC.md").read_text(encoding="utf-8")
    except (ImportError, FileNotFoundError, TypeError):
        pass
    # Fallback to repo root
    spec_file = Path(__file__).parent.parent.parent.parent / "SPEC.md"
    if spec_file.exists():
        return spec_file.read_text(encoding="utf-8")
    return "(SPEC.md not found - see https://github.com/thegdyne/cdd)"
