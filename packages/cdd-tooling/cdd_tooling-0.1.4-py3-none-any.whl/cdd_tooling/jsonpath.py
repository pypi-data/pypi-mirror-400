# src/cdd/jsonpath.py
"""Minimal JSONPath resolver per spec."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union


@dataclass(frozen=True)
class PathResolution:
    """Result of JSONPath resolution."""
    ok: bool
    value: Any = None
    error: Union[str, None] = None  # "path_not_found" | "type_mismatch" | "invalid_path"


def interpolate_vars(value: Any, vars_dict: Dict[str, Any]) -> Any:
    """
    Replace {var} and $.vars.X references in strings with actual values.
    
    Supports:
      - {pack_id} -> vars_dict["pack_id"]
      - $.vars.pack_id -> vars_dict["pack_id"]
    """
    if isinstance(value, str):
        # First handle {var} style
        def replacer_brace(m):
            var_name = m.group(1)
            return str(vars_dict.get(var_name, ''))
        value = re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', replacer_brace, value)
        
        # Then handle $.vars.X style
        def replacer_path(m):
            var_name = m.group(1)
            return str(vars_dict.get(var_name, ''))
        value = re.sub(r'\$\.vars\.([a-zA-Z_][a-zA-Z0-9_]*)', replacer_path, value)
        
        return value
    elif isinstance(value, list):
        return [interpolate_vars(v, vars_dict) for v in value]
    elif isinstance(value, dict):
        return {k: interpolate_vars(v, vars_dict) for k, v in value.items()}
    return value


def resolve_jsonpath(root: Any, path: str) -> PathResolution:
    """
    Minimal JSONPath resolver per spec.
    
    Supports:
      - $.key.key2[0].key3
      - $.key["quoted.key"].value
      
    Missing path resolves to null (ok=True, value=None).
    No type coercion.
    """
    if path is None:
        return PathResolution(ok=True, value=None)

    if not isinstance(path, str) or not path.startswith("$."):
        return PathResolution(ok=False, error="invalid_path")

    tokens = _tokenize(path)
    if tokens and tokens[0] == ("invalid", None):
        return PathResolution(ok=False, error="invalid_path")

    cur = root

    for tok_type, tok_val in tokens:
        if tok_type == "key":
            if isinstance(cur, dict):
                if tok_val in cur:
                    cur = cur[tok_val]
                else:
                    return PathResolution(ok=True, value=None)  # missing => null
            else:
                return PathResolution(ok=False, error="type_mismatch")
        elif tok_type == "idx":
            if isinstance(cur, list):
                idx = tok_val
                if 0 <= idx < len(cur):
                    cur = cur[idx]
                else:
                    return PathResolution(ok=True, value=None)  # missing => null
            else:
                return PathResolution(ok=False, error="type_mismatch")

    return PathResolution(ok=True, value=cur)


def _tokenize(path: str) -> List[Tuple[str, Any]]:
    """Parse $.a.b[0].c["quoted"] into tokens."""
    s = path[2:]  # strip "$."
    out: List[Tuple[str, Any]] = []
    i = 0
    buf = ""
    
    while i < len(s):
        ch = s[i]
        if ch == ".":
            if buf:
                out.append(("key", buf))
                buf = ""
            i += 1
            continue
        if ch == "[":
            if buf:
                out.append(("key", buf))
                buf = ""
            j = s.find("]", i)
            if j == -1:
                return [("invalid", None)]
            inner = s[i + 1 : j].strip()
            
            # Check for quoted string ["key"] or ['key']
            if (inner.startswith('"') and inner.endswith('"')) or \
               (inner.startswith("'") and inner.endswith("'")):
                out.append(("key", inner[1:-1]))
            elif inner.lstrip("-").isdigit():
                out.append(("idx", int(inner)))
            else:
                return [("invalid", None)]
            i = j + 1
            continue
        buf += ch
        i += 1
    
    if buf:
        out.append(("key", buf))
    
    return out
