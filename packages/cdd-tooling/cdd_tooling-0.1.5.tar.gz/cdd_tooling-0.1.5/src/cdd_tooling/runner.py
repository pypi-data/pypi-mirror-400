# src/cdd/runner.py
"""Contract test runner."""
from __future__ import annotations

import datetime
import hashlib
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cdd_tooling.assertions import AssertionResult, run_assertions
from cdd_tooling.executors.base import RunContext, StepResult, StepSpec
from cdd_tooling.executors.registry import ExecutorRegistry
from cdd_tooling.spec import get_tool_version, load_schema_version


def _parse_semver(v: str) -> Tuple[int, int, int]:
    parts = (v or "").strip().split(".")
    if len(parts) < 3:
        parts = parts + ["0"] * (3 - len(parts))
    return int(parts[0]), int(parts[1]), int(parts[2])


def _major(v: str) -> int:
    return _parse_semver(v)[0]


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _hash_run_id(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must parse to a mapping")
    return data


def _find_project_contract(contracts_path: Path) -> Path:
    if contracts_path.is_file():
        return contracts_path
    p = contracts_path / "project.yaml"
    if not p.exists():
        raise FileNotFoundError(f"Missing project contract: {p}")
    return p


def _collect_contract_files(contracts_path: Path) -> List[Path]:
    if contracts_path.is_file():
        return [contracts_path]
    return sorted([p for p in contracts_path.rglob("*.yaml") if p.is_file()])


def _read_cdd_version_fallback(repo_root: Path) -> Optional[str]:
    p = repo_root / ".cdd-version"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").strip() or None


@dataclass
class RunnerConfig:
    require_exact_spec: bool = False
    matrix_fail_fast: bool = False
    artifacts_root: Path = Path("artifacts")


class ContractRunner:
    """
    High-level contract test runner.
    
    - Loads contracts
    - Checks project cdd_spec compatibility
    - Runs tests via executors
    - Emits spec-compliant reports
    """

    def __init__(
        self,
        executors: ExecutorRegistry,
        artifacts_root: Path = Path("artifacts"),
        require_exact_spec: bool = False,
        matrix_fail_fast: bool = False,
    ):
        self.executors = executors
        self.cfg = RunnerConfig(
            require_exact_spec=require_exact_spec,
            matrix_fail_fast=matrix_fail_fast,
            artifacts_root=artifacts_root,
        )

    def run(
        self,
        contracts_path: Path,
        injected_vars: Optional[Dict[str, Any]] = None,
        only_test_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        injected_vars = injected_vars or {}
        only_test_ids = only_test_ids or []

        repo_root = contracts_path.parent.parent if contracts_path.is_file() else contracts_path.parent
        
        try:
            project_path = _find_project_contract(contracts_path if contracts_path.is_dir() else repo_root / "contracts")
            project = _load_yaml(project_path)
        except FileNotFoundError:
            # No project.yaml - run single contract
            project = {}
            project_path = contracts_path

        tool_ver = get_tool_version()
        project_spec = project.get("cdd_spec") or _read_cdd_version_fallback(repo_root)

        warnings: List[Dict[str, str]] = []
        errors: List[Dict[str, str]] = []

        if project_spec:
            try:
                if _major(project_spec) != _major(tool_ver):
                    errors.append({
                        "code": "spec_major_mismatch",
                        "message": f"Project targets CDD {project_spec}, tooling is {tool_ver}",
                    })
                elif self.cfg.require_exact_spec and project_spec != tool_ver:
                    errors.append({
                        "code": "spec_exact_mismatch",
                        "message": f"Project targets CDD {project_spec}, tooling is {tool_ver} (exact required)",
                    })
                elif project_spec != tool_ver:
                    warnings.append({
                        "code": "spec_version_mismatch",
                        "message": f"Project targets CDD {project_spec}, tooling is {tool_ver}",
                    })
            except Exception as e:
                warnings.append({
                    "code": "spec_version_parse_error",
                    "message": f"Could not parse cdd_spec {project_spec!r}: {e}",
                })
        else:
            warnings.append({
                "code": "spec_version_missing",
                "message": "No cdd_spec or .cdd-version found",
            })

        run_id = f"run_{_hash_run_id(str(project_path) + _now_iso())}"
        schema_version = load_schema_version()

        if errors:
            return self._error_report(
                contract="project",
                run_id=run_id,
                schema_version=schema_version,
                tool_version=tool_ver,
                project_spec=project_spec,
                warnings=warnings,
                errors=errors,
            )

        contracts_dir = project_path.parent if project_path.is_file() else project_path
        contract_files = _collect_contract_files(contracts_dir)
        contract_files = [p for p in contract_files if p.name != "project.yaml"]

        all_results: List[Dict[str, Any]] = []
        artifacts_root = self.cfg.artifacts_root / run_id
        artifacts_root.mkdir(parents=True, exist_ok=True)

        for cpath in contract_files:
            contract_doc = _load_yaml(cpath)
            contract_name = contract_doc.get("contract", cpath.stem)

            ctx = self._build_context(
                contract_doc=contract_doc,
                contract_path=cpath,
                artifacts_dir=artifacts_root / contract_name,
                injected_vars=injected_vars,
                tool_version=tool_ver,
                project_spec=project_spec,
            )

            results = self._run_contract_tests(
                ctx=ctx,
                contract_doc=contract_doc,
                contract_path=cpath,
                only_test_ids=only_test_ids,
            )
            all_results.extend(results)

        summary = {
            "passed": sum(1 for r in all_results if r.get("status") == "pass"),
            "failed": sum(1 for r in all_results if r.get("status") == "fail"),
            "skipped": sum(1 for r in all_results if r.get("status") == "skipped"),
            "error": sum(1 for r in all_results if r.get("status") == "error"),
        }

        return {
            "schema_version": schema_version,
            "report_type": "single",
            "contract": project.get("project", "unknown"),
            "run_id": run_id,
            "tool_version": tool_ver,
            "project_spec": project_spec,
            "started_at": _now_iso(),
            "warnings": warnings,
            "errors": [],
            "summary": summary,
            "results": all_results,
            "artifacts_dir": str(artifacts_root),
        }

    def _run_contract_tests(
        self,
        ctx: RunContext,
        contract_doc: Dict[str, Any],
        contract_path: Path,
        only_test_ids: List[str],
    ) -> List[Dict[str, Any]]:
        runner_cfg = contract_doc.get("runner", {}) or {}
        executor_name = runner_cfg.get("executor", "python")
        timeout_ms = int(runner_cfg.get("timeout_ms", 30000))

        tests = contract_doc.get("tests", []) or []
        if not isinstance(tests, list):
            return [self._test_error("INVALID", None, "error", "tests must be a list")]

        is_static_executor = executor_name == "static"
        executor = None

        if not is_static_executor:
            try:
                executor = self.executors.create(executor_name)
            except Exception as e:
                return [self._test_error("EXECUTOR", None, "error", f"Unknown executor '{executor_name}': {e}")]

            try:
                executor.setup(ctx, runner_cfg)
            except Exception as e:
                return [self._test_error("EXECUTOR", None, "error", f"Executor setup failed: {e}")]

        # Static analysis (for executor: static)
        ast_blob: Optional[Dict[str, Any]] = None
        if is_static_executor:
            ast_blob = self._run_static_analyze(ctx, runner_cfg, contract_doc, contract_path)
            ctx.runner["ast"] = ast_blob

        results: List[Dict[str, Any]] = []

        for t in tests:
            if not isinstance(t, dict):
                results.append(self._test_error("UNKNOWN", None, "error", "test entry must be an object"))
                continue

            test_id = t.get("id", "")
            if only_test_ids and test_id not in only_test_ids:
                continue

            test_type = t.get("type", "")
            
            # Handle type: static tests (file scanning) - distinct from executor: static
            if test_type == "static" and t.get("files"):
                result = self._run_static_file_test(ctx, t, contract_path)
                results.append(result)
                
                if self.cfg.matrix_fail_fast and result.get("status") in ("fail", "error"):
                    break
                continue

            # Static executor: no steps allowed
            steps = t.get("steps", [])
            if is_static_executor and steps not in (None, [], {}):
                results.append(self._test_error(test_id, t.get("requirement"), "error", "Static tests must have no steps"))
                continue

            if is_static_executor:
                step_results: List[StepResult] = []
                saved: Dict[str, Any] = {}
            else:
                step_results, saved = self._execute_steps(ctx, runner_cfg, test_id, steps, executor, timeout_ms)

            assertion_context = self._build_assertion_context(ctx, t, step_results, saved)
            asserts = t.get("assert", []) or []
            assertion_results = run_assertions(assertion_context, asserts)
            status, msg = self._status_from_assertions(assertion_results)

            assertions_out = [self._assertion_to_dict(ar) for ar in assertion_results]

            results.append({
                "id": test_id,
                "name": t.get("name", ""),
                "requirement": t.get("requirement"),
                "type": t.get("type"),
                "status": status,
                "message": msg,
                "assertions": assertions_out,
                "steps": [self._step_result_to_dict(sr) for sr in step_results],
            })

            if self.cfg.matrix_fail_fast and status in ("fail", "error"):
                break

        if executor is not None:
            try:
                executor.teardown(ctx, runner_cfg)
            except Exception:
                results.append(self._test_error("TEARDOWN", None, "error", "Executor teardown failed"))

        return results

    def _run_static_file_test(
        self,
        ctx: RunContext,
        test: Dict[str, Any],
        contract_path: Path,
    ) -> Dict[str, Any]:
        """
        Run a static file scanning test (type: static with files: field).
        
        Uses the static executor's file scanning capability.
        """
        from cdd_tooling.executors.static_exec import run_static_test
        
        test_id = test.get("id", "")
        name = test.get("name", "")
        requirement = test.get("requirement")
        
        start = time.time()
        
        # Run static file scan
        result = run_static_test(
            test=test,
            base_dir=contract_path.parent,
            vars_dict=ctx.vars,
        )
        
        dur_ms = int((time.time() - start) * 1000)
        
        status = result.get("status", "error")
        assertions = result.get("assertions", [])
        error = result.get("error")
        files_scanned = result.get("files_scanned", 0)
        
        # Convert AssertionResult objects to dicts
        assertions_out = []
        for ar in assertions:
            if isinstance(ar, AssertionResult):
                assertions_out.append(self._assertion_to_dict(ar))
            elif isinstance(ar, dict):
                assertions_out.append(ar)
        
        message = error if error else f"Scanned {files_scanned} files"
        if status == "fail":
            message = f"{len(assertions_out)} failures in {files_scanned} files"
        
        return {
            "id": test_id,
            "name": name,
            "requirement": requirement,
            "type": "static",
            "status": status,
            "message": message,
            "assertions": assertions_out,
            "steps": [],
            "duration_ms": dur_ms,
            "files_scanned": files_scanned,
        }

    def _execute_steps(
        self,
        ctx: RunContext,
        runner_cfg: Dict[str, Any],
        test_id: str,
        steps: Any,
        executor,
        timeout_ms: int,
    ) -> Tuple[List[StepResult], Dict[str, Any]]:
        """Execute steps and return (results, saved_values)."""
        if steps is None:
            return [], {}
        if not isinstance(steps, list):
            return [StepResult(ok=False, error_code="type_mismatch", message="steps must be a list")], {}

        out: List[StepResult] = []
        saved: Dict[str, Any] = {}
        
        for s in steps:
            if not isinstance(s, dict):
                out.append(StepResult(ok=False, error_code="type_mismatch", message="step must be an object"))
                continue

            action = s.get("action")
            save_as = s.get("save_as")
            
            if action == "wait":
                seconds = float(s.get("seconds", 0.0))
                time.sleep(max(0.0, seconds))
                res = StepResult(ok=True, value=None, meta={"wait_s": seconds})
                out.append(res)
                if save_as:
                    saved[save_as] = self._step_result_to_dict(res)
                continue

            step = StepSpec(
                action=action,
                with_=s.get("with", {}) or {},
                save_as=save_as,
                method=s.get("method"),
                n=s.get("n"),
                warmup=bool(s.get("warmup", False)),
                command=s.get("command"),
                seconds=s.get("seconds"),
            )

            if not executor.supports(step.action):
                res = StepResult(ok=False, error_code="invalid_action", message=f"Action not supported: {step.action}")
                out.append(res)
                continue

            start = time.time()
            try:
                res = executor.execute_step(ctx, runner_cfg, test_id, step, timeout_ms)
            except Exception as e:
                res = StepResult(ok=False, error_code="executor_exception", message=str(e))
            
            dur_ms = int((time.time() - start) * 1000)
            res.meta = dict(res.meta or {})
            res.meta.setdefault("duration_ms", dur_ms)
            out.append(res)
            
            # Save result if save_as specified (and not warmup)
            if save_as and not step.warmup:
                saved[save_as] = self._step_result_to_dict(res)

        return out, saved

    def _run_static_analyze(
        self,
        ctx: RunContext,
        runner_cfg: Dict[str, Any],
        contract_doc: Dict[str, Any],
        contract_path: Path,
    ) -> Dict[str, Any]:
        """MVP placeholder for static analysis."""
        return {
            "schema_version": "1.0",
            "calls": [],
            "bus_reads": {},
            "source_included": False,
            "parser": runner_cfg.get("parser"),
            "contract_file": str(contract_path),
        }

    def _build_context(
        self,
        contract_doc: Dict[str, Any],
        contract_path: Path,
        artifacts_dir: Path,
        injected_vars: Dict[str, Any],
        tool_version: str,
        project_spec: Optional[str],
    ) -> RunContext:
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        env = {
            "os": self._detect_os(),
            "os_family": self._detect_os_family(),
            "python_major": sys.version_info.major,
            "python_minor": sys.version_info.minor,
            "python_patch": sys.version_info.micro,
        }

        runner = {
            "tool_version": tool_version,
            "require_exact_spec": self.cfg.require_exact_spec,
            "matrix_fail_fast": self.cfg.matrix_fail_fast,
        }

        contract_meta = {
            "contract": contract_doc.get("contract", contract_path.stem),
            "version": contract_doc.get("version"),
            "status": contract_doc.get("status"),
            "path": str(contract_path),
            "project_spec": project_spec,
        }

        vars_ = dict(injected_vars)
        vars_.update(contract_doc.get("vars", {}) or {})

        return RunContext(
            artifacts_dir=artifacts_dir,
            work_dir=contract_path.parent,
            vars=vars_,
            env=env,
            runner=runner,
            contract=contract_meta,
        )

    def _build_assertion_context(
        self,
        ctx: RunContext,
        test: Dict[str, Any],
        step_results: List[StepResult],
        saved: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        steps_out = [self._step_result_to_dict(sr) for sr in step_results]
        ast = ctx.runner.get("ast")

        # Build context with saved values at root level for $.name.value access
        context = {
            "vars": ctx.vars,
            "env": ctx.env,
            "runner": ctx.runner,
            "contract": ctx.contract,
            "steps": steps_out,
            "ast": ast,
        }
        
        # Add saved values to root so $.result.value works
        if saved:
            context.update(saved)
        
        return context

    def _status_from_assertions(self, assertion_results: List[AssertionResult]) -> Tuple[str, str]:
        if any(ar.error for ar in assertion_results):
            first = next(ar for ar in assertion_results if ar.error)
            return "error", f"Assertion error: {first.error}"
        if any(not ar.pass_ for ar in assertion_results):
            return "fail", "One or more assertions failed"
        return "pass", "All assertions passed"

    def _assertion_to_dict(self, ar: AssertionResult) -> Dict[str, Any]:
        d = {
            "op": ar.op,
            "actual": ar.actual,
            "expected": ar.expected,
            "pass": ar.pass_,
            "error": ar.error,
            "details": ar.details or {},
        }
        # Include message if present
        if ar.message:
            d["message"] = ar.message
        return d

    def _step_result_to_dict(self, sr: StepResult) -> Dict[str, Any]:
        stdout_str = sr.stdout or ""
        # Try to parse stdout as int for convenience
        stdout_int = None
        try:
            stdout_int = int(stdout_str.strip())
        except (ValueError, AttributeError):
            pass

        return {
            "ok": sr.ok,
            "value": sr.value,
            "error_code": sr.error_code,
            "message": sr.message,
            "meta": sr.meta or {},
            "stdout": stdout_str,
            "stdout_int": stdout_int,
            "stderr": sr.stderr or "",
            "artifacts": sr.artifacts or [],
        }
    def _test_error(self, test_id: str, requirement: Optional[str], status: str, message: str) -> Dict[str, Any]:
        return {
            "id": test_id,
            "name": "",
            "requirement": requirement,
            "type": None,
            "status": status,
            "message": message,
            "assertions": [],
            "steps": [],
        }

    def _error_report(
        self,
        contract: str,
        run_id: str,
        schema_version: str,
        tool_version: str,
        project_spec: Optional[str],
        warnings: List[Dict[str, str]],
        errors: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        return {
            "schema_version": schema_version,
            "report_type": "single",
            "contract": contract,
            "run_id": run_id,
            "tool_version": tool_version,
            "project_spec": project_spec,
            "started_at": _now_iso(),
            "warnings": warnings,
            "errors": errors,
            "summary": {"passed": 0, "failed": 0, "skipped": 0, "error": 1},
            "results": [self._test_error("VERSION", None, "error", errors[0]["message"])],
            "artifacts_dir": str(self.cfg.artifacts_root / run_id),
        }

    def _detect_os(self) -> str:
        import platform
        return platform.platform()

    def _detect_os_family(self) -> str:
        if sys.platform.startswith("linux"):
            return "linux"
        if sys.platform == "darwin":
            return "darwin"
        if sys.platform.startswith("win"):
            return "windows"
        return "unknown"
