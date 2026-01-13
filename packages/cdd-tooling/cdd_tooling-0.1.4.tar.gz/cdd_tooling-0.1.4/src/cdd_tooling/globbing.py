# src/cdd/globbing.py
"""File globbing and variable interpolation utilities."""
from __future__ import annotations

from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional

from cdd_tooling.jsonpath import interpolate_vars


def expand_files(
    files_spec: Any, 
    base_dir: Path, 
    vars_dict: Optional[Dict[str, Any]] = None
) -> List[Path]:
    """
    Expand files specification to list of paths.
    
    files_spec can be:
      - string glob: "packs/foo/generators/*.scd"
      - list of globs: ["*.scd", "*.sc"]
      - list of explicit files
      
    Supports {var} and $.vars.X interpolation from vars_dict.
    
    Args:
        files_spec: Glob pattern(s) or file list
        base_dir: Base directory for relative path resolution
        vars_dict: Variables for {var} interpolation
        
    Returns:
        Sorted, deduplicated list of matching Paths
    """
    if files_spec is None:
        return []
    
    vars_dict = vars_dict or {}
    
    if isinstance(files_spec, str):
        patterns = [files_spec]
    elif isinstance(files_spec, list):
        patterns = files_spec
    else:
        return []
    
    paths = []
    for pattern in patterns:
        # Interpolate variables
        pattern = interpolate_vars(pattern, vars_dict)
        # Expand glob relative to base_dir
        matches = glob(str(base_dir / pattern), recursive=True)
        paths.extend(Path(m) for m in matches)
    
    return sorted(set(paths))
