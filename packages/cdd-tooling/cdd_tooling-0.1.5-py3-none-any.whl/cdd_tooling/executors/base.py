# src/cdd/executors/base.py
"""Base types and protocol for executors."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Protocol

ExecutorName = Literal["python", "shell", "static", "sclang"]


@dataclass
class RunContext:
    """
    Canonical runtime context exposed to JSONPath as $.env / $.vars / $.runner / ...
    Keep this aligned with SPEC.md.
    """
    artifacts_dir: Path
    work_dir: Path  # cwd baseline (contract dir per spec)
    vars: Dict[str, Any] = field(default_factory=dict)
    env: Dict[str, Any] = field(default_factory=dict)  # os, os_family, python_*, node_*, etc.
    runner: Dict[str, Any] = field(default_factory=dict)  # runner_version, strict flags, etc.
    contract: Dict[str, Any] = field(default_factory=dict)  # contract name, version, status


@dataclass
class StepSpec:
    """Parsed step from YAML."""
    action: str
    with_: Dict[str, Any] = field(default_factory=dict)  # maps from YAML `with`
    save_as: Optional[str] = None
    method: Optional[str] = None
    n: Optional[int] = None
    warmup: bool = False
    command: Optional[List[str]] = None
    seconds: Optional[float] = None


@dataclass
class StepResult:
    """Standard result envelope per spec."""
    ok: bool
    value: Any = None
    error_code: Optional[str] = None
    message: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    artifacts: List[Dict[str, Any]] = field(default_factory=list)


class Executor(Protocol):
    """
    Common interface for executors.
    Executors can be stateful (setup/teardown), but MUST be deterministic for unit/static.
    """
    name: ExecutorName

    def supports(self, action: str) -> bool:
        """Return True if this executor handles the given action."""
        ...

    def setup(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        """Optional: called once per contract run."""
        ...

    def execute_step(
        self,
        ctx: RunContext,
        runner_cfg: Dict[str, Any],
        test_id: str,
        step: StepSpec,
        timeout_ms: int,
    ) -> StepResult:
        """Execute a single step and return the result envelope."""
        ...

    def teardown(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        """Optional: called once per contract run."""
        ...
