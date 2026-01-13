# src/cdd/analyze/__init__.py
"""Source artifact analysis for evidence-based contracts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cdd_tooling.analyze.source import is_source_file, analyze_source as analyze_source_ref


def analyze_source(source_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Analyze a source artifact and produce structured output.
    
    This is the foundation of Source-First CDD: analyze before you specify.
    
    Supported types:
    - PDF: extract images, detect rectangles/lines/text positions
    - HTML: extract element structure, classes, required elements
    - Source (py, js, scd, etc.): capture reference snapshot + patterns template
    - Image: basic shape detection (future)
    
    Returns:
        Analysis result dict with structure.json path and summary
    """
    source_path = Path(source_path)
    output_dir = Path(output_dir)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")
    
    suffix = source_path.suffix.lower()
    
    if suffix == '.pdf':
        from cdd_tooling.analyze.pdf import analyze_pdf
        return analyze_pdf(source_path, output_dir)
    elif suffix in ('.html', '.htm'):
        from cdd_tooling.analyze.html import analyze_html
        return analyze_html(source_path, output_dir)
    elif is_source_file(source_path):
        return analyze_source_ref(source_path, output_dir)
    elif suffix in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
        # Future: image analysis
        raise NotImplementedError(f"Image analysis not yet implemented: {suffix}")
    else:
        raise ValueError(f"Unsupported source type: {suffix}")


def load_analysis(analysis_dir: Path) -> Optional[Dict[str, Any]]:
    """Load structure.json from an analysis directory."""
    structure_path = Path(analysis_dir) / "structure.json"
    if not structure_path.exists():
        return None
    return json.loads(structure_path.read_text())


def find_element(analysis: Dict[str, Any], element_id: str) -> Optional[Dict[str, Any]]:
    """Find an element by ID in analysis structure."""
    for page in analysis.get("pages", []):
        for element in page.get("elements", []):
            if element.get("id") == element_id:
                return element
    return None


def list_elements(analysis: Dict[str, Any], element_type: Optional[str] = None) -> List[str]:
    """List all element IDs in analysis, optionally filtered by type."""
    ids = []
    for page in analysis.get("pages", []):
        for element in page.get("elements", []):
            if element_type is None or element.get("type") == element_type:
                ids.append(element.get("id"))
    return ids
