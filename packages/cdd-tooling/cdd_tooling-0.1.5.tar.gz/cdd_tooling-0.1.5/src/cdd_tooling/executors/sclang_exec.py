# src/cdd/executors/sclang_exec.py
"""SuperCollider executor: handles render_nrt action."""
from __future__ import annotations

from typing import Any, Dict

from cdd_tooling.executors.base import Executor, RunContext, StepResult, StepSpec


class SclangExecutor:
    """
    Execute SuperCollider NRT renders.
    
    MVP: Placeholder implementation.
    Full implementation will:
    - Generate .scd script from template
    - Run sclang NRT render
    - Parse metrics JSON output
    - Return audio file path + metrics
    """

    name = "sclang"

    def supports(self, action: str) -> bool:
        return action in ("render_nrt", "shell")

    def setup(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        ctx.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def execute_step(
        self,
        ctx: RunContext,
        runner_cfg: Dict[str, Any],
        test_id: str,
        step: StepSpec,
        timeout_ms: int,
    ) -> StepResult:
        if step.action == "render_nrt":
            return self._do_render_nrt(ctx, runner_cfg, step, timeout_ms)
        elif step.action == "shell":
            # Delegate to shell executor behavior
            from cdd_tooling.executors.shell_exec import ShellExecutor
            shell = ShellExecutor()
            return shell.execute_step(ctx, runner_cfg, test_id, step, timeout_ms)
        else:
            return StepResult(ok=False, error_code="unsupported_action", message=f"Unknown action: {step.action}")

    def teardown(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        pass

    def _do_render_nrt(
        self,
        ctx: RunContext,
        runner_cfg: Dict[str, Any],
        step: StepSpec,
        timeout_ms: int,
    ) -> StepResult:
        """
        MVP placeholder for NRT render.
        
        Full implementation will:
        1. Read script_template from runner_cfg
        2. Substitute step.with_ values (synthdef, dur_s, sr, seed)
        3. Write temp .scd file
        4. Run sclang -i <script>
        5. Parse output metrics.json
        6. Return wav_path, hash, metrics
        """
        synthdef = step.with_.get("synthdef", "unknown")
        dur_s = step.with_.get("dur_s", 1.0)
        
        # Placeholder response
        return StepResult(
            ok=False,
            error_code="not_implemented",
            message=f"sclang render_nrt not yet implemented (synthdef={synthdef}, dur={dur_s}s)",
            value={
                "wav_path": None,
                "hash": None,
                "metrics": {
                    "rms_db": None,
                    "peak_dbfs": None,
                    "dc_offset": None,
                },
            },
        )
