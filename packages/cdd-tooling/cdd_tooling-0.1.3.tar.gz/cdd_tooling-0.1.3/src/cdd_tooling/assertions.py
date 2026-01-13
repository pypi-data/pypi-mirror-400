# src/cdd/assertions.py
"""Assertion operators and evaluation per spec."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cdd_tooling.jsonpath import resolve_jsonpath


@dataclass
class AssertionResult:
    """Result of a single assertion evaluation."""
    op: str
    actual: Any
    expected: Any
    pass_: bool
    error: Optional[str] = None  # "path_not_found" | "type_mismatch" | "invalid_path" | ...
    message: Optional[str] = None  # user-provided context for failure reporting
    details: Dict[str, Any] = field(default_factory=dict)


def run_assertions(context: Dict[str, Any], asserts: List[Dict[str, Any]]) -> List[AssertionResult]:
    """
    Evaluate assertions against context.
    
    context: the object JSONPaths resolve against
    asserts: list of assertion dicts from YAML
    """
    results: List[AssertionResult] = []
    
    for a in asserts:
        op = a.get("op")
        actual_expr = a.get("actual")
        expected_expr = a.get("expected")
        pattern_expr = a.get("pattern")  # for matches/not_matches
        message = a.get("message")  # user context

        actual_val, actual_err = _eval_value(context, actual_expr)
        expected_val, expected_err = _eval_value(context, expected_expr)
        pattern_val, pattern_err = _eval_value(context, pattern_expr) if pattern_expr else (None, None)

        # Implicit expected for file_exists
        if op == "file_exists" and expected_expr is None:
            expected_val = True
            expected_err = None

        if actual_err:
            results.append(AssertionResult(
                op=op, actual=None, expected=expected_val, 
                pass_=False, error=actual_err, message=message
            ))
            continue
        if expected_err:
            results.append(AssertionResult(
                op=op, actual=actual_val, expected=None, 
                pass_=False, error=expected_err, message=message
            ))
            continue
        if pattern_err:
            results.append(AssertionResult(
                op=op, actual=actual_val, expected=pattern_val, 
                pass_=False, error=pattern_err, message=message
            ))
            continue

        res = _apply_op(op, actual_val, expected_val, pattern_val, a)
        res.message = message  # Attach message
        results.append(res)
    
    return results


def _eval_value(context: Dict[str, Any], expr: Any) -> Tuple[Any, Optional[str]]:
    """
    Evaluate an expression.
    
    expr can be:
    - literal (number/string/bool/null)
    - JSONPath string starting with "$."
    """
    if isinstance(expr, str) and expr.startswith("$."):
        r = resolve_jsonpath(context, expr)
        if not r.ok and r.error:
            return None, r.error
        return r.value, None
    return expr, None


def _apply_op(op: str, actual: Any, expected: Any, pattern: Any, raw: Dict[str, Any]) -> AssertionResult:
    """Apply an assertion operator."""
    try:
        if op == "eq":
            return AssertionResult(op, actual, expected, actual == expected)
        
        if op == "ne":
            return AssertionResult(op, actual, expected, actual != expected)

        if op == "lt":
            return _num(op, actual, expected, lambda a, e: a < e)
        
        if op == "lte":
            return _num(op, actual, expected, lambda a, e: a <= e)
        
        if op == "gt":
            return _num(op, actual, expected, lambda a, e: a > e)
        
        if op == "gte":
            return _num(op, actual, expected, lambda a, e: a >= e)

        if op == "in_range":
            mn = raw.get("min")
            mx = raw.get("max")
            if not all(isinstance(x, (int, float)) for x in (actual, mn, mx) if x is not None):
                return AssertionResult(op, actual, {"min": mn, "max": mx}, False, error="type_mismatch")
            ok = mn <= actual <= mx
            return AssertionResult(op, actual, {"min": mn, "max": mx}, ok)

        if op == "approx":
            tol = raw.get("tolerance")
            if not all(isinstance(x, (int, float)) for x in (actual, expected, tol) if x is not None):
                return AssertionResult(op, actual, expected, False, error="type_mismatch")
            ok = abs(actual - expected) <= tol
            return AssertionResult(op, actual, expected, ok, details={"tolerance": tol})

        if op == "contains":
            # SPEC: for arrays, exact element equality; for strings, substring
            if isinstance(actual, list):
                return AssertionResult(op, actual, expected, expected in actual)
            if isinstance(actual, str) and isinstance(expected, str):
                return AssertionResult(op, actual, expected, expected in actual)
            return AssertionResult(op, actual, expected, False, error="type_mismatch")

        if op == "has_keys":
            if not isinstance(actual, dict):
                return AssertionResult(op, actual, expected, False, error="type_mismatch")
            if not isinstance(expected, list) or not all(isinstance(k, str) for k in expected):
                return AssertionResult(op, actual, expected, False, error="type_mismatch")
            ok = all(k in actual for k in expected)
            return AssertionResult(op, actual, expected, ok)

        if op == "matches":
            pat = pattern or expected
            if not isinstance(actual, str) or not isinstance(pat, str):
                return AssertionResult(op, actual, pat, False, error="type_mismatch")
            ok = re.search(pat, actual, re.MULTILINE) is not None
            return AssertionResult(op, actual, pat, ok)

        if op == "not_matches":
            pat = pattern or expected
            if not isinstance(actual, str) or not isinstance(pat, str):
                return AssertionResult(op, actual, pat, False, error="type_mismatch")
            ok = re.search(pat, actual, re.MULTILINE) is None
            return AssertionResult(op, actual, pat, ok)

        if op == "file_exists":
            if not isinstance(actual, str):
                return AssertionResult(op, actual, expected, False, error="type_mismatch")
            p = Path(actual)
            ok = p.exists()
            return AssertionResult(op, actual, True, ok)

        if op == "call_order":
            # SPEC: greedy L->R subsequence match
            if not isinstance(actual, list) or not isinstance(expected, list):
                return AssertionResult(op, actual, expected, False, error="type_mismatch")
            if not all(isinstance(x, str) for x in actual) or not all(isinstance(x, str) for x in expected):
                return AssertionResult(op, actual, expected, False, error="type_mismatch")

            pos = 0
            for want in expected:
                while pos < len(actual) and actual[pos] != want:
                    pos += 1
                if pos >= len(actual):
                    return AssertionResult(op, actual, expected, False)
                pos += 1
            return AssertionResult(op, actual, expected, True)

        return AssertionResult(op, actual, expected, False, error="unknown_op")

    except Exception as e:
        return AssertionResult(op, actual, expected, False, error="exception", details={"exception": str(e)})


def _num(op: str, actual: Any, expected: Any, fn) -> AssertionResult:
    """Helper for numeric comparisons."""
    if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
        return AssertionResult(op, actual, expected, False, error="type_mismatch")
    return AssertionResult(op, actual, expected, fn(actual, expected))
