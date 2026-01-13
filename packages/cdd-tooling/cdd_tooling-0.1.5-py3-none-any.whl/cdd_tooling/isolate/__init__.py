"""
CDD Isolate - Execute a single contract in a clean, isolated workspace.

Implements CDD_ISOLATE_SPEC.md v1.0

Exit codes:
    0: Paths passed and (if run) tests passed
    1: One or more tests failed
    2: Path verification failed
    3: Contract parse error (including unsupported extends in v1)
    4: Project root not found
    5: Source path invalid or link root missing
"""

from __future__ import annotations

import hashlib
import os
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, Dict, Any

import yaml

if TYPE_CHECKING:
    from typing import Optional, Set, List


# Exit code constants
EXIT_SUCCESS = 0
EXIT_TEST_FAILURE = 1
EXIT_PATH_FAILURE = 2
EXIT_PARSE_ERROR = 3
EXIT_NO_PROJECT_ROOT = 4
EXIT_INVALID_PATH = 5


class IsolateContext(NamedTuple):
    """Context for an isolate run."""
    contract_path: Path
    project_root: Path
    work_dir: Path
    link_roots: Set[str]
    marker_token: str
    verbose: bool
    dry_run: bool
    keep: bool
    keep_on_fail: bool
    paths_only: bool


def detect_project_root(contract_path: Path, explicit_project: Optional[Path] = None) -> Optional[Path]:
    """
    Detect the project root by walking upwards from contract_path.
    
    Precedence (highest to lowest):
    1. Directory contains .cdd/ AND contracts/
    2. Directory contains .git/ AND contracts/
    3. Directory contains contracts/ AND src/
    """
    if explicit_project:
        explicit = Path(explicit_project).resolve()
        if explicit.is_dir():
            return explicit
        return None
    
    current = contract_path.resolve().parent
    candidates: List[tuple[int, Path]] = []
    
    while current != current.parent:
        has_cdd = (current / ".cdd").is_dir()
        has_git = (current / ".git").is_dir()
        has_contracts = (current / "contracts").is_dir()
        has_src = (current / "src").is_dir()
        
        if has_cdd and has_contracts:
            return current
        elif has_git and has_contracts:
            candidates.append((2, current))
        elif has_contracts and has_src:
            candidates.append((3, current))
        
        current = current.parent
    
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    
    return None


def parse_contract(contract_path: Path) -> dict:
    """Parse a contract YAML file."""
    try:
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Contract parse error: {e}")
    except FileNotFoundError:
        raise ValueError(f"Contract not found: {contract_path}")
    except Exception as e:
        raise ValueError(f"Failed to read contract: {e}")
    
    if not isinstance(contract, dict):
        raise ValueError("Contract must be a YAML mapping")
    
    if 'extends' in contract:
        raise ValueError("extends not supported by cdd isolate v1.0")
    
    return contract


def extract_referenced_paths(contract: dict) -> Set[str]:
    """Extract all file paths referenced in the contract."""
    paths: Set[str] = set()
    
    tests = contract.get('tests', [])
    for test in tests:
        files = test.get('files')
        if files:
            if isinstance(files, list):
                paths.update(f for f in files if isinstance(f, str))
            elif isinstance(files, str):
                paths.add(files)
        
        steps = test.get('steps', [])
        for step in steps:
            if isinstance(step, dict):
                step_file = step.get('file')
                if isinstance(step_file, str):
                    paths.add(step_file)
                
                command = step.get('command', [])
                if isinstance(command, list):
                    for arg in command:
                        if isinstance(arg, str) and ('/' in arg or arg.startswith('..')):
                            paths.add(arg)
    
    return paths


def get_link_roots(paths: Set[str], project_root: Path, contract_dir: Path) -> Set[str]:
    """Compute link roots from referenced paths."""
    link_roots: Set[str] = set()
    
    for path_str in paths:
        if not path_str.startswith('..'):
            continue
        
        resolved = (contract_dir / path_str).resolve()
        
        try:
            rel_to_project = resolved.relative_to(project_root)
        except ValueError:
            raise ValueError(
                f"Path '{path_str}' resolves outside project root.\n"
                f"  Resolved: {resolved}\n"
                f"  Project:  {project_root}\n"
                f"Consider using --project to specify correct root."
            )
        
        parts = rel_to_project.parts
        if parts:
            link_roots.add(parts[0])
    
    return link_roots


def compute_work_dir(contract_path: Path, custom_work_dir: Optional[Path] = None) -> Path:
    """Compute the work directory path."""
    if custom_work_dir:
        return Path(custom_work_dir).resolve()
    
    abs_path = str(contract_path.resolve())
    path_hash = hashlib.sha256(abs_path.encode()).hexdigest()[:8]
    pid = os.getpid()
    
    return Path(f"/tmp/cdd-isolate-{path_hash}-{pid}")


def create_marker(work_dir: Path) -> str:
    """Create the marker file for cleanup safety."""
    token = secrets.token_hex(16)
    created = datetime.now(timezone.utc).isoformat()
    pid = os.getpid()
    
    marker_path = work_dir / ".cdd-isolate-marker"
    marker_content = f"token={token}\ncreated={created}\npid={pid}\n"
    marker_path.write_text(marker_content)
    
    return token


def read_marker_token(work_dir: Path) -> Optional[str]:
    """Read the marker token from work directory."""
    marker_path = work_dir / ".cdd-isolate-marker"
    if not marker_path.exists():
        return None
    
    try:
        content = marker_path.read_text()
        for line in content.splitlines():
            if line.startswith("token="):
                return line[6:]
    except Exception:
        pass
    
    return None


def is_safe_to_cleanup(work_dir: Path, expected_token: str, project_root: Path) -> bool:
    """Check if it's safe to cleanup the work directory."""
    forbidden = {
        Path("/"),
        Path.home(),
        project_root.resolve(),
    }
    
    resolved_work = work_dir.resolve()
    if resolved_work in forbidden:
        return False
    
    actual_token = read_marker_token(work_dir)
    if actual_token != expected_token:
        return False
    
    return True


def setup_work_dir(ctx: IsolateContext, console) -> str:
    """Create and set up the work directory. Returns actual marker token."""
    work_dir = ctx.work_dir
    
    if work_dir.exists():
        if ctx.verbose:
            console.print(f"  [dim]rm -rf {work_dir}[/dim]")
        shutil.rmtree(work_dir)
    
    contracts_dir = work_dir / "contracts"
    if ctx.verbose:
        console.print(f"  [dim]mkdir -p {contracts_dir}[/dim]")
    contracts_dir.mkdir(parents=True)
    
    if ctx.verbose:
        console.print(f"  [dim]touch {work_dir / '.cdd-isolate-marker'}[/dim]")
    token = create_marker(work_dir)
    
    dest = contracts_dir / ctx.contract_path.name
    if ctx.verbose:
        console.print(f"  [dim]cp {ctx.contract_path} {dest}[/dim]")
    shutil.copy2(ctx.contract_path, dest)
    
    for link_root in ctx.link_roots:
        source = ctx.project_root / link_root
        target = work_dir / link_root
        
        if not source.is_dir():
            raise ValueError(f"Link root '{link_root}' does not exist: {source}")
        
        if ctx.verbose:
            console.print(f"  [dim]ln -s {source} {target}[/dim]")
        target.symlink_to(source)
    
    return token


def cleanup_work_dir(ctx: IsolateContext, exit_code: int, console) -> bool:
    """Clean up the work directory based on options and exit code."""
    should_keep = ctx.keep or (ctx.keep_on_fail and exit_code != 0)
    
    if should_keep:
        return False
    
    if not is_safe_to_cleanup(ctx.work_dir, ctx.marker_token, ctx.project_root):
        console.print(f"[yellow]Warning: Refusing to cleanup {ctx.work_dir} (safety check failed)[/yellow]")
        return False
    
    if ctx.verbose:
        console.print(f"  [dim]rm -rf {ctx.work_dir}[/dim]")
    
    shutil.rmtree(ctx.work_dir)
    return True


def run_isolate(
    contract_path: str,
    project: Optional[str] = None,
    keep: bool = False,
    keep_on_fail: bool = False,
    work_dir: Optional[str] = None,
    verbose: bool = False,
    paths_only: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Execute a single contract in isolation.
    
    Returns dict with 'exit_code' and 'result' keys.
    """
    from cdd_tooling.paths import verify_paths
    from cdd_tooling.runner import ContractRunner
    
    contract_path_obj = Path(contract_path).resolve()
    
    # Parse contract
    try:
        contract = parse_contract(contract_path_obj)
    except ValueError as e:
        return {"exit_code": EXIT_PARSE_ERROR, "error": str(e)}
    
    # Detect project root
    project_root = detect_project_root(
        contract_path_obj,
        Path(project) if project else None
    )
    
    if not project_root:
        return {
            "exit_code": EXIT_NO_PROJECT_ROOT,
            "error": "Could not detect project root. Use --project to specify."
        }
    
    # Extract paths and compute link roots
    try:
        ref_paths = extract_referenced_paths(contract)
        link_roots = get_link_roots(ref_paths, project_root, contract_path_obj.parent)
    except ValueError as e:
        return {"exit_code": EXIT_INVALID_PATH, "error": str(e)}
    
    # Compute work directory
    work_dir_path = compute_work_dir(
        contract_path_obj,
        Path(work_dir) if work_dir else None
    )
    
    # Build context
    ctx = IsolateContext(
        contract_path=contract_path_obj,
        project_root=project_root,
        work_dir=work_dir_path,
        link_roots=link_roots,
        marker_token="",  # Set after setup
        verbose=verbose,
        dry_run=dry_run,
        keep=keep,
        keep_on_fail=keep_on_fail,
        paths_only=paths_only,
    )
    
    return {
        "exit_code": EXIT_SUCCESS,
        "context": ctx,
        "contract_name": contract.get("contract", contract_path_obj.stem),
    }
