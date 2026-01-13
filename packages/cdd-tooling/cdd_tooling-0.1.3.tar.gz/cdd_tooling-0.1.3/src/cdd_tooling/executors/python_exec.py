# src/cdd/executors/python_exec.py
"""Python executor: handles call and call_n actions."""
from __future__ import annotations

import importlib.util
import statistics
import sys
import time
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List

from cdd_tooling.executors.base import Executor, RunContext, StepResult, StepSpec


class PythonExecutor:
    """Execute Python functions via call and call_n actions."""

    name = "python"
    _module: Any = None
    _symbol: str | None = None

    def supports(self, action: str) -> bool:
        return action in ("call", "call_n")

    def setup(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        """Load the module specified in runner.entry."""
        entry = runner_cfg.get("entry")
        if not entry:
            raise ValueError("PythonExecutor requires runner.entry")

        entry_path = ctx.work_dir / entry
        if not entry_path.exists():
            raise FileNotFoundError(f"Entry file not found: {entry_path}")

        # Dynamic import
        spec = importlib.util.spec_from_file_location("_cdd_target", entry_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {entry_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules["_cdd_target"] = module
        spec.loader.exec_module(module)

        self._module = module
        self._symbol = runner_cfg.get("symbol")

    def execute_step(
        self,
        ctx: RunContext,
        runner_cfg: Dict[str, Any],
        test_id: str,
        step: StepSpec,
        timeout_ms: int,
    ) -> StepResult:
        if step.action == "call":
            return self._do_call(ctx, runner_cfg, step)
        elif step.action == "call_n":
            return self._do_call_n(ctx, runner_cfg, step)
        else:
            return StepResult(ok=False, error_code="unsupported_action", message=f"Unknown action: {step.action}")

    def teardown(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        self._module = None
        self._symbol = None

    def _resolve_symbol(self, step: StepSpec) -> str:
        """Get the function name to call."""
        if step.method:
            return step.method
        if self._symbol:
            return self._symbol
        raise ValueError("No call target: set runner.symbol or step.method")

    def _do_call(self, ctx: RunContext, runner_cfg: Dict[str, Any], step: StepSpec) -> StepResult:
        symbol = self._resolve_symbol(step)
        fn = getattr(self._module, symbol, None)
        if fn is None:
            return StepResult(ok=False, error_code="symbol_not_found", message=f"Symbol not found: {symbol}")

        # Capture stdout/stderr
        old_stdout, old_stderr = sys.stdout, sys.stderr
        captured_out, captured_err = StringIO(), StringIO()

        try:
            sys.stdout, sys.stderr = captured_out, captured_err
            start = time.perf_counter()
            result = fn(**step.with_)
            duration_ms = int((time.perf_counter() - start) * 1000)
        except Exception as e:
            return StepResult(
                ok=False,
                error_code="exception",
                message=str(e),
                stdout=captured_out.getvalue(),
                stderr=captured_err.getvalue(),
            )
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

        # Normalize result to envelope
        if isinstance(result, dict) and "ok" in result:
            # Already envelope-shaped
            return StepResult(
                ok=result.get("ok", True),
                value=result.get("value"),
                error_code=result.get("error_code"),
                message=result.get("message"),
                meta={"duration_ms": duration_ms, **(result.get("meta") or {})},
                stdout=captured_out.getvalue(),
                stderr=captured_err.getvalue(),
            )
        else:
            # Raw return value
            return StepResult(
                ok=True,
                value=result,
                meta={"duration_ms": duration_ms},
                stdout=captured_out.getvalue(),
                stderr=captured_err.getvalue(),
            )

    def _do_call_n(self, ctx: RunContext, runner_cfg: Dict[str, Any], step: StepSpec) -> StepResult:
        n = step.n or 1
        symbol = self._resolve_symbol(step)
        fn = getattr(self._module, symbol, None)
        if fn is None:
            return StepResult(ok=False, error_code="symbol_not_found", message=f"Symbol not found: {symbol}")

        durations: List[float] = []
        first_error: StepResult | None = None

        for _ in range(n):
            start = time.perf_counter()
            try:
                fn(**step.with_)
                duration_ms = (time.perf_counter() - start) * 1000
                durations.append(duration_ms)
            except Exception as e:
                if first_error is None:
                    first_error = StepResult(ok=False, error_code="exception", message=str(e))
                # Continue collecting what we can

        if not durations:
            # All failed
            return StepResult(
                ok=False,
                error_code=first_error.error_code if first_error else "all_failed",
                message=first_error.message if first_error else "All iterations failed",
                value={"n": n, "durations_ms": []},
            )

        sorted_durs = sorted(durations)
        value = {
            "n": n,
            "durations_ms": durations,
            "min_ms": min(durations),
            "max_ms": max(durations),
            "mean_ms": statistics.mean(durations),
            "p50_ms": sorted_durs[len(sorted_durs) // 2],
            "p95_ms": sorted_durs[int(len(sorted_durs) * 0.95)] if len(sorted_durs) >= 20 else sorted_durs[-1],
            "p99_ms": sorted_durs[int(len(sorted_durs) * 0.99)] if len(sorted_durs) >= 100 else sorted_durs[-1],
        }

        return StepResult(
            ok=first_error is None,
            value=value,
            error_code=first_error.error_code if first_error else None,
            message=first_error.message if first_error else None,
        )
