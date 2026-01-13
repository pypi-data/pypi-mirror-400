# src/cdd_tooling/spec/__init__.py
"""Spec and version loading utilities."""
from __future__ import annotations

from importlib import metadata
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, Optional


def _read_spec_text_installed() -> Optional[str]:
    """Read SPEC.md from installed package data if present."""
    try:
        return files("cdd_tooling.spec").joinpath("SPEC.md").read_text(encoding="utf-8")
    except Exception:
        return None


def _read_spec_text_repo_fallback() -> Optional[str]:
    """Fallback to repo root SPEC.md during development."""
    spec_file = Path(__file__).parent.parent.parent.parent / "SPEC.md"
    if spec_file.exists():
        return spec_file.read_text(encoding="utf-8")
    return None


def load_spec_text() -> str:
    """Load the full SPEC.md text."""
    text = _read_spec_text_installed()
    if text is not None:
        return text
    text = _read_spec_text_repo_fallback()
    if text is not None:
        return text
    return "(SPEC.md not found - see https://github.com/thegdyne/cdd)"


def _parse_front_matter(text: str) -> Dict[str, Any]:
    """
    Parse ONLY the first YAML front-matter block from SPEC.md.

    Minimal parser: we only need doc_version/schema_version keys.
    Avoids requiring PyYAML at runtime.
    """
    if not text.startswith("---"):
        return {}

    end = text.find("\n---", 3)
    if end == -1:
        return {}

    fm = text[3:end].splitlines()
    out: Dict[str, Any] = {}

    for line in fm:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        out[k] = v

    return out


def get_spec_doc_version() -> str:
    """
    Return the SPEC document version from SPEC.md front-matter.
    This is what `cdd spec --version` should report.
    """
    text = load_spec_text()
    meta = _parse_front_matter(text)
    v = meta.get("doc_version")
    return str(v) if v else "unknown"


def get_tool_version() -> str:
    """
    Back-compat alias: historically returned a hardcoded SPEC_VERSION.
    Now returns SPEC document version from front-matter.
    """
    return get_spec_doc_version()


def get_tooling_version() -> str:
    """Get the tooling package version."""
    try:
        return metadata.version("cdd-tooling")
    except metadata.PackageNotFoundError:
        # Development mode - read from pyproject.toml (optional: implement later)
        return "0.1.1"


def load_schema_version() -> str:
    """
    Return the report schema version.

    If your schema is explicitly versioned in SPEC.md front-matter, use it.
    Otherwise, default to major-only coupling: <major>.0 based on doc_version.
    """
    text = load_spec_text()
    meta = _parse_front_matter(text)

    schema_v = meta.get("schema_version")
    if schema_v:
        return str(schema_v)

    doc_v = meta.get("doc_version")
    if isinstance(doc_v, str) and doc_v:
        major = doc_v.split(".")[0]
        return f"{major}.0" if major else "1.0"

    return "1.0"
