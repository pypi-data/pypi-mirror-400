# src/cdd/executors/shell_exec.py
"""Shell executor: handles shell action."""
from __future__ import annotations
import os
import subprocess
import time
from typing import Any, Dict
from cdd_tooling.executors.base import RunContext, StepResult, StepSpec
from cdd_tooling.jsonpath import interpolate_vars


class ShellExecutor:
    """Execute shell commands."""
    name = "shell"

    def supports(self, action: str) -> bool:
        return action == "shell"

    def setup(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        """Ensure artifacts directory exists."""
        ctx.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def execute_step(
        self,
        ctx: RunContext,
        runner_cfg: Dict[str, Any],
        test_id: str,
        step: StepSpec,
        timeout_ms: int,
    ) -> StepResult:
        if step.action != "shell":
            return StepResult(ok=False, error_code="unsupported_action", message=f"ShellExecutor only handles 'shell', got: {step.action}")

        command = step.command
        if not command:
            return StepResult(ok=False, error_code="missing_command", message="shell action requires 'command' field")

        # Interpolate variables in command
        command = interpolate_vars(command, ctx.vars)

        # Build environment
        env = os.environ.copy()
        env.update(runner_cfg.get("env") or {})
        env["CONTRACT"] = ctx.contract.get("contract", "")
        env["RUN_ID"] = ctx.runner.get("run_id", "")
        env["ARTIFACTS_DIR"] = str(ctx.artifacts_dir)

        timeout_s = timeout_ms / 1000.0 if timeout_ms else None
        start = time.perf_counter()

        try:
            result = subprocess.run(
                command,
                cwd=ctx.work_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
            duration_ms = int((time.perf_counter() - start) * 1000)

            return StepResult(
                ok=result.returncode == 0,
                value={"returncode": result.returncode},
                error_code="nonzero_exit" if result.returncode != 0 else None,
                message=f"Exit code: {result.returncode}" if result.returncode != 0 else None,
                meta={"duration_ms": duration_ms},
                stdout=result.stdout,
                stderr=result.stderr,
            )

        except subprocess.TimeoutExpired:
            return StepResult(
                ok=False,
                error_code="timeout",
                message=f"Command timed out after {timeout_ms}ms",
            )
        except Exception as e:
            return StepResult(
                ok=False,
                error_code="exception",
                message=str(e),
            )

    def teardown(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        pass
