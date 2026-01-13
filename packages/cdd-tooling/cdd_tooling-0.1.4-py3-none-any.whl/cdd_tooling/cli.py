# src/cdd/cli.py
"""CDD command-line interface."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cdd_tooling.coverage import compute_coverage
from cdd_tooling.executors.registry import ExecutorRegistry
from cdd_tooling.lint import lint_contracts
from cdd_tooling.runner import ContractRunner
from cdd_tooling.spec import get_tool_version, load_spec_text
from cdd_tooling.analyze import analyze_source
from cdd_tooling.paths import verify_paths
from cdd_tooling.isolate import (
    run_isolate, setup_work_dir, cleanup_work_dir,
    EXIT_SUCCESS, EXIT_TEST_FAILURE, EXIT_PATH_FAILURE,
    EXIT_PARSE_ERROR, EXIT_NO_PROJECT_ROOT, EXIT_INVALID_PATH,
    IsolateContext, read_marker_token
)

console = Console()


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(prog="cdd", description="Contract-Driven Development tooling")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # cdd spec
    p_spec = sub.add_parser("spec", help="Print the embedded spec/version")
    p_spec.add_argument("--print", dest="do_print", action="store_true", help="Print spec text")
    p_spec.add_argument("--version", action="store_true", help="Print tool/spec version")

    # cdd lint
    p_lint = sub.add_parser("lint", help="Lint contract files (schema + coverage gates)")
    p_lint.add_argument("path", nargs="?", default="contracts", help="Contracts directory or file")
    p_lint.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    p_lint.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    # cdd test
    p_test = sub.add_parser("test", help="Run contract tests")
    p_test.add_argument("path", nargs="?", default="contracts", help="Contracts directory or file")
    p_test.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    p_test.add_argument("--artifacts", default="artifacts", help="Artifacts output root")
    p_test.add_argument("--require-exact-spec", action="store_true", help="Error unless exact spec match")
    p_test.add_argument("--var", action="append", default=[], help="Inject variable (key=value). Repeatable.")
    p_test.add_argument("--matrix-fail-fast", action="store_true", help="Stop on first failing target")
    p_test.add_argument("--only", action="append", default=[], help="Run only matching test ids (repeatable)")

    # cdd coverage
    p_cov = sub.add_parser("coverage", help="Requirement coverage report")
    p_cov.add_argument("path", nargs="?", default="contracts", help="Contracts directory or file")
    p_cov.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    p_cov.add_argument("--strict", action="store_true", help="Exit non-zero if uncovered requirements exist")

    # cdd analyze (NEW - Source-First CDD)
    p_analyze = sub.add_parser("analyze", help="Analyze source artifacts for evidence-based contracts")
    p_analyze.add_argument("source", help="Source file to analyze (PDF, image)")
    p_analyze.add_argument("--output", "-o", default="analysis/", help="Output directory for analysis artifacts")
    p_analyze.add_argument("--json", action="store_true", help="Emit machine-readable JSON summary")

    # cdd compare (NEW - Compare two analyses)
    p_compare = sub.add_parser("compare", help="Compare two analyses (PDF or HTML)")
    p_compare.add_argument("original", help="Original analysis directory or structure.json")
    p_compare.add_argument("generated", help="Generated analysis directory or structure.json")
    p_compare.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    # cdd paths
    p_paths = sub.add_parser("paths", help="Verify all file paths in contracts resolve")
    p_paths.add_argument("path", nargs="?", default="contracts", help="Contracts directory or file")
    p_paths.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    # cdd isolate
    p_isolate = sub.add_parser("isolate", help="Execute single contract in isolated workspace")
    p_isolate.add_argument("contract", help="Path to contract YAML file")
    p_isolate.add_argument("--project", "-p", help="Project root directory")
    p_isolate.add_argument("--keep", "-k", action="store_true", help="Keep work directory after run")
    p_isolate.add_argument("--keep-on-fail", action="store_true", help="Keep work dir only on failure")
    p_isolate.add_argument("--work-dir", "-w", help="Custom work directory")
    p_isolate.add_argument("--verbose", "-v", action="store_true", help="Show detailed operations")
    p_isolate.add_argument("--paths-only", action="store_true", help="Only run path verification")
    p_isolate.add_argument("--dry-run", action="store_true", help="Print plan and exit")

    args = parser.parse_args(argv)

    if args.cmd == "spec":
        return cmd_spec(args)
    if args.cmd == "lint":
        return cmd_lint(args)
    if args.cmd == "test":
        return cmd_test(args)
    if args.cmd == "coverage":
        return cmd_coverage(args)
    if args.cmd == "analyze":
        return cmd_analyze(args)
    if args.cmd == "compare":
        return cmd_compare(args)
    if args.cmd == "paths":
        return cmd_paths(args)
    if args.cmd == "isolate":
        return cmd_isolate(args)

    parser.print_help()
    return 2


# Console-script entrypoints
def contract_lint() -> None:
    raise SystemExit(main(["lint", *sys.argv[1:]]))


def contract_test() -> None:
    raise SystemExit(main(["test", *sys.argv[1:]]))


def contract_coverage() -> None:
    raise SystemExit(main(["coverage", *sys.argv[1:]]))


def cmd_spec(args: argparse.Namespace) -> int:
    if args.version:
        console.print(get_tool_version())
        return 0
    if args.do_print:
        console.print(load_spec_text())
        return 0
    console.print(get_tool_version())
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    contracts_path = Path(args.path)
    res = lint_contracts(contracts_path, strict=args.strict)

    if args.json:
        console.print_json(json.dumps(res))
    else:
        _print_lint(res)

    return 0 if res["ok"] else 1


def cmd_coverage(args: argparse.Namespace) -> int:
    contracts_path = Path(args.path)
    cov = compute_coverage(contracts_path)

    if args.json:
        console.print_json(json.dumps(cov))
    else:
        _print_coverage(cov)

    if args.strict and cov["uncovered_count"] > 0:
        return 1
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyze source artifacts for evidence-based contracts."""
    source_path = Path(args.source)
    output_dir = Path(args.output)
    
    if not source_path.exists():
        console.print(f"[red]Error: Source not found: {source_path}[/red]")
        return 1
    
    try:
        console.print(f"Analyzing: [bold]{source_path}[/bold]")
        result = analyze_source(source_path, output_dir)
        
        if args.json:
            console.print_json(json.dumps(result))
        else:
            _print_analysis(result)
        
        return 0
    except ImportError as e:
        console.print(f"[red]Missing dependency: {e}[/red]")
        console.print("Install with: pip install pymupdf")
        return 1
    except Exception as e:
        console.print(f"[red]Analysis failed: {e}[/red]")
        return 1


def cmd_compare(args: argparse.Namespace) -> int:
    """Compare two analyses (PDF, HTML, or source reference)."""
    
    def load_analysis(path_str: str) -> Dict[str, Any]:
        p = Path(path_str)
        if p.is_dir():
            p = p / "structure.json"
        if not p.exists():
            raise FileNotFoundError(f"Not found: {p}")
        return json.loads(p.read_text())
    
    try:
        original = load_analysis(args.original)
        generated = load_analysis(args.generated)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1
    
    # Route based on analysis type
    orig_type = original.get("type", "pdf")
    gen_type = generated.get("type", "pdf")
    
    if orig_type != gen_type:
        console.print(f"[red]Error: Cannot compare {orig_type} with {gen_type}[/red]")
        return 1
    
    if orig_type == "html":
        from cdd_tooling.analyze.html import compare_html_analyses
        diff = compare_html_analyses(original, generated)
        if args.json:
            console.print_json(json.dumps(diff))
        else:
            _print_html_comparison(diff, original, generated)
        # Check for issues
        has_issues = not diff.get("required_elements_match", True) or any(
            not v["match"] for v in diff.get("element_counts", {}).values()
        )
    elif orig_type == "source_reference":
        from cdd_tooling.analyze.source import compare_source_analyses
        diff = compare_source_analyses(original, generated)
        if args.json:
            console.print_json(json.dumps(diff))
        else:
            _print_source_comparison(diff)
        # Check for issues - source references only match if hash matches
        has_issues = not diff.get("match", False)
    else:
        from cdd_tooling.analyze.pdf import compare_analyses
        diff = compare_analyses(original, generated)
        if args.json:
            console.print_json(json.dumps(diff))
        else:
            _print_comparison(diff, original, generated)
        # Check for issues
        has_issues = not diff.get("page_size_match", True) or any(
            not v["match"] for v in diff.get("element_counts", {}).values()
        )
    
    return 1 if has_issues else 0


def _print_comparison(diff: Dict[str, Any], original: Dict[str, Any], generated: Dict[str, Any]) -> None:
    """Print PDF comparison results."""
    console.print(Panel("[bold]PDF Comparison: Original vs Generated[/bold]"))
    
    # Page size
    if diff["page_size_match"]:
        console.print("[green]✓[/green] Page size matches")
    else:
        ps = diff.get("page_size_diff", {})
        console.print(f"[red]✗[/red] Page size mismatch: {ps.get('original')} vs {ps.get('generated')}")
    
    # Element counts
    t = Table(title="Element Counts")
    t.add_column("Type")
    t.add_column("Original", justify="right")
    t.add_column("Generated", justify="right")
    t.add_column("Match")
    
    for el_type, counts in diff["element_counts"].items():
        status = "[green]✓[/green]" if counts["match"] else "[red]✗[/red]"
        t.add_row(
            el_type,
            str(counts["original"]),
            str(counts["generated"]),
            status
        )
    console.print(t)
    
    # Layout summary
    if "layout" in original:
        orig_fields = len(original.get("layout", {}).get("form_fields", []))
        gen_fields = len(generated.get("layout", {}).get("form_fields", []))
        console.print(f"\nForm fields detected: Original={orig_fields}, Generated={gen_fields}")


def _print_html_comparison(diff: Dict[str, Any], original: Dict[str, Any], generated: Dict[str, Any]) -> None:
    """Print HTML comparison results."""
    console.print(Panel("[bold]HTML Comparison: Original vs Generated[/bold]"))
    
    # Required elements
    if diff.get("required_elements_match", True):
        console.print("[green]✓[/green] Required elements match")
    else:
        console.print("[red]✗[/red] Required elements mismatch:")
        for key, vals in diff.get("required_elements_diff", {}).items():
            console.print(f"    {key}: original={vals['original']}, generated={vals['generated']}")
    
    # Element counts
    t = Table(title="Element Counts")
    t.add_column("Tag")
    t.add_column("Original", justify="right")
    t.add_column("Generated", justify="right")
    t.add_column("Match")
    
    for tag, counts in diff.get("element_counts", {}).items():
        status = "[green]✓[/green]" if counts["match"] else "[red]✗[/red]"
        t.add_row(
            tag,
            str(counts["original"]),
            str(counts["generated"]),
            status
        )
    console.print(t)
    
    # CSS class changes
    added = diff.get("classes_added", [])
    removed = diff.get("classes_removed", [])
    if added:
        console.print(f"\n[yellow]Classes added:[/yellow] {', '.join(added[:10])}" + 
                      (f" (+{len(added)-10} more)" if len(added) > 10 else ""))
    if removed:
        console.print(f"[yellow]Classes removed:[/yellow] {', '.join(removed[:10])}" +
                      (f" (+{len(removed)-10} more)" if len(removed) > 10 else ""))


def cmd_test(args: argparse.Namespace) -> int:
    contracts_path = Path(args.path)
    artifacts_root = Path(args.artifacts)

    injected_vars = _parse_vars(args.var)

    registry = ExecutorRegistry.discover()
    runner = ContractRunner(
        executors=registry,
        artifacts_root=artifacts_root,
        require_exact_spec=args.require_exact_spec,
        matrix_fail_fast=args.matrix_fail_fast,
    )

    report = runner.run(contracts_path, injected_vars=injected_vars, only_test_ids=args.only or None)

    if args.json:
        console.print_json(json.dumps(report))
    else:
        _print_report(report)

    summary = report.get("summary", {})
    has_failures = summary.get("failed", 0) > 0 or summary.get("error", 0) > 0
    return 1 if has_failures else 0


def _parse_vars(kvs: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for kv in kvs:
        if "=" not in kv:
            raise SystemExit(f"--var must be key=value, got: {kv}")
        k, v = kv.split("=", 1)
        out[k.strip()] = v
    return out


def _print_lint(res: Dict[str, Any]) -> None:
    status = "[green]PASS[/green]" if res["ok"] else "[red]FAIL[/red]"
    body = Table(show_header=False, box=None)
    body.add_row("Status", status)
    body.add_row("Contracts", str(res.get("contracts_checked", 0)))
    body.add_row("Errors", str(len(res.get("errors", []))))
    body.add_row("Warnings", str(len(res.get("warnings", []))))
    console.print(Panel(body, title="CDD Lint"))

    if res.get("errors"):
        t = Table(title="Errors")
        t.add_column("Code")
        t.add_column("Message")
        for e in res["errors"]:
            t.add_row(e.get("code", ""), e.get("message", ""))
        console.print(t)

    if res.get("warnings"):
        t = Table(title="Warnings")
        t.add_column("Code")
        t.add_column("Message")
        for w in res["warnings"]:
            t.add_row(w.get("code", ""), w.get("message", ""))
        console.print(t)


def _print_coverage(cov: Dict[str, Any]) -> None:
    t = Table(title="CDD Coverage")
    t.add_column("Requirement")
    t.add_column("Linked tests", justify="right")
    t.add_column("Status")
    for r in cov["requirements"]:
        ok = r["linked_tests"] > 0
        t.add_row(
            r["id"],
            str(r["linked_tests"]),
            "[green]covered[/green]" if ok else "[red]UNcovered[/red]",
        )
    console.print(t)
    console.print(f"Uncovered: {cov['uncovered_count']}")


def _print_analysis(result: Dict[str, Any]) -> None:
    """Print analysis results in human-readable format."""
    analysis_type = result.get("type", "pdf")
    
    # Source reference has different output structure
    if analysis_type == "source_reference":
        _print_source_analysis(result)
        return
    
    # PDF/HTML analysis output
    summary = result.get("summary", {})
    
    body = Table(show_header=False, box=None)
    body.add_row("Source", result.get("source_name", ""))
    body.add_row("Type", result.get("type", ""))
    body.add_row("Pages", str(result.get("page_count", 0)))
    body.add_row("Total elements", str(summary.get("total_elements", 0)))
    body.add_row("  Rectangles", str(summary.get("rectangles", 0)))
    body.add_row("  Lines", str(summary.get("lines", 0)))
    body.add_row("  Text blocks", str(summary.get("text_blocks", 0)))
    body.add_row("Output", result.get("output_dir", ""))
    console.print(Panel(body, title="[bold green]CDD Analyze[/bold green]"))
    
    # Show pages with element counts
    for page in result.get("pages", []):
        elements = page.get("elements", [])
        rects = sum(1 for e in elements if e["type"] == "rectangle")
        texts = sum(1 for e in elements if e["type"] == "text")
        console.print(f"  Page {page['page']}: {len(elements)} elements ({rects} rects, {texts} text)")
    
    # Show layout issues if any
    layout = result.get("layout", {})
    overlaps = layout.get("overlaps", [])
    if overlaps:
        console.print()
        console.print(f"[bold yellow]⚠️  {len(overlaps)} layout issue(s) detected:[/bold yellow]")
        for o in overlaps[:5]:  # Show first 5
            severity_color = "red" if o["severity"] == "error" else "yellow"
            console.print(f"  [{severity_color}]• Page {o['page']}: {o['description']}[/{severity_color}]")
        if len(overlaps) > 5:
            console.print(f"  [dim]... and {len(overlaps) - 5} more (see layout.md)[/dim]")
    
    # Hint for next steps
    console.print()
    console.print("[dim]Next steps:[/dim]")
    console.print(f"  1. Review [bold]{result.get('output_dir')}/elements.md[/bold] for element catalog")
    if overlaps:
        console.print(f"  2. Review [bold]{result.get('output_dir')}/layout.md[/bold] for issue details")
        console.print(f"  3. Fix layout issues and re-analyze")
    else:
        console.print(f"  2. Reference elements in contracts with [bold]source_ref: SRC001#element_id[/bold]")
        console.print(f"  3. Run [bold]cdd validate[/bold] to check source references")


def _print_source_analysis(result: Dict[str, Any]) -> None:
    """Print source reference analysis results."""
    body = Table(show_header=False, box=None)
    body.add_row("Source", result.get("source_name", ""))
    body.add_row("Type", result.get("file_type", ""))
    body.add_row("Lines", str(result.get("line_count", 0)))
    body.add_row("Size", f"{result.get('size_bytes', 0)} bytes")
    body.add_row("Hash", f"{result.get('hash', '')[:12]}...")
    body.add_row("Output", result.get("output_dir", ""))
    console.print(Panel(body, title="[bold green]CDD Analyze - Source Reference[/bold green]"))
    
    console.print()
    console.print("[dim]Files created:[/dim]")
    for f in result.get("files", []):
        console.print(f"  • {f}")
    
    console.print()
    console.print("[dim]Next steps:[/dim]")
    console.print(f"  1. Review [bold]{result.get('output_dir')}/source{_get_ext(result)}[/bold] to understand the reference")
    console.print(f"  2. Fill in [bold]{result.get('output_dir')}/PATTERNS.md[/bold] with patterns to preserve")
    console.print(f"  3. Write contract based on documented patterns")
    console.print(f"  4. Implement against contract")


def _get_ext(result: Dict[str, Any]) -> str:
    """Get file extension from result."""
    files = result.get("files", [])
    for f in files:
        if f.startswith("source"):
            return f[6:]  # Remove "source" prefix
    return ""


def _print_source_comparison(diff: Dict[str, Any]) -> None:
    """Print source reference comparison results."""
    console.print(Panel("[bold]Source Reference Comparison[/bold]"))
    
    if diff.get("match"):
        console.print("[green]✓[/green] Files are identical")
    else:
        console.print("[yellow]✗[/yellow] Files differ")
        console.print(f"  Original hash:  {diff.get('original_hash', '')[:12]}...")
        console.print(f"  Generated hash: {diff.get('generated_hash', '')[:12]}...")
        console.print(f"  Original lines:  {diff.get('original_lines', 0)}")
        console.print(f"  Generated lines: {diff.get('generated_lines', 0)}")
    
    if not diff.get("file_type_match"):
        console.print(f"[red]✗[/red] File type mismatch: {diff.get('original_type')} vs {diff.get('generated_type')}")
    
    console.print()
    console.print(f"[dim]{diff.get('summary', '')}[/dim]")


def _print_report(report: Dict[str, Any]) -> None:
    summ = report.get("summary", {})
    header = Table(show_header=False, box=None)
    header.add_row("contract", str(report.get("contract", "")))
    header.add_row("run_id", str(report.get("run_id", "")))
    header.add_row("passed", str(summ.get("passed", 0)))
    header.add_row("failed", str(summ.get("failed", 0)))
    header.add_row("skipped", str(summ.get("skipped", 0)))
    header.add_row("error", str(summ.get("error", 0)))
    console.print(Panel(header, title="CDD Test Report"))

    # Warnings
    warnings = report.get("warnings", [])
    if warnings:
        for w in warnings:
            console.print(f"[yellow]⚠ {w.get('code')}: {w.get('message')}[/yellow]")

    results = report.get("results", [])
    if not results:
        return

    t = Table(title="Results")
    t.add_column("Test")
    t.add_column("Status")
    t.add_column("Requirement")
    t.add_column("Message")
    for r in results:
        status = r.get("status", "")
        color = {
            "pass": "green",
            "fail": "red",
            "skipped": "yellow",
            "error": "magenta",
        }.get(status, "white")
        t.add_row(
            r.get("id", ""),
            f"[{color}]{status}[/{color}]",
            r.get("requirement", "") or "",
            (r.get("message", "") or "")[:120],
        )
    console.print(t)


def cmd_paths(args: argparse.Namespace) -> int:
    """Verify all file paths in contracts resolve correctly."""
    contracts_path = Path(args.path)

    if not contracts_path.exists():
        console.print(f"[red]Error: Path not found: {contracts_path}[/red]")
        return 1

    result = verify_paths(contracts_path)

    if args.json:
        console.print_json(json.dumps(result))
    else:
        _print_paths(result)

    return 0 if result["ok"] else 1


def _print_paths(result: Dict[str, Any]) -> None:
    """Print path verification results."""
    for contract_result in result["results"]:
        console.print()
        console.print("═" * 60)
        console.print(f"  Path Verification: [bold]{contract_result['contract']}[/bold]")
        console.print(f"  Contract: {contract_result['contract_path']}")
        console.print("═" * 60)

        passed = contract_result["passed"]
        failed = contract_result["failed"]

        if passed:
            console.print(f"\n  [green]✓ {len(passed)} paths OK:[/green]")
            for p in passed:
                console.print(f"    [green]✓[/green] {p}")

        if failed:
            console.print(f"\n  [red]✗ {len(failed)} paths FAILED:[/red]")
            for f in failed:
                console.print(f"    [red]✗[/red] {f['path']}")
                if f.get("suggestion"):
                    console.print(f"      └─ Did you mean: [yellow]{f['suggestion']}[/yellow] ?")

        console.print()
        if contract_result["ok"]:
            console.print(f"  RESULT: [green]PASS[/green] ({len(passed)} files)")
        else:
            console.print(f"  RESULT: [red]FAIL[/red] ({len(failed)} missing, {len(passed)} found)")

    console.print()
    if result["ok"]:
        console.print("═" * 60)
        console.print("  [green]ALL CONTRACTS PASSED PATH VERIFICATION[/green]")
        console.print("═" * 60)
    else:
        console.print("═" * 60)
        console.print("  [red]PATH VERIFICATION FAILED[/red] - Fix paths before running cdd test")
        console.print("═" * 60)


def cmd_isolate(args: argparse.Namespace) -> int:
    """Execute a single contract in an isolated workspace."""
    import os

    # Initialize
    result = run_isolate(
        contract_path=args.contract,
        project=args.project,
        keep=args.keep,
        keep_on_fail=getattr(args, 'keep_on_fail', False),
        work_dir=args.work_dir,
        verbose=args.verbose,
        paths_only=args.paths_only,
        dry_run=args.dry_run,
    )

    if result["exit_code"] != EXIT_SUCCESS:
        console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
        return result["exit_code"]

    ctx = result["context"]
    contract_name = result["contract_name"]

    # Print header
    console.print()
    console.print("=" * 45)
    console.print(f"CDD Isolate: [bold]{ctx.contract_path.name}[/bold]")
    console.print(f"Project: {ctx.project_root}")
    console.print(f"Work:    {ctx.work_dir}")
    links_str = ", ".join(sorted(ctx.link_roots)) if ctx.link_roots else "(none)"
    console.print(f"Links:   {links_str}")
    console.print("=" * 45)

    # Dry run - just show plan
    if args.dry_run:
        console.print()
        console.print("[dim]Dry run - no changes made[/dim]")
        return EXIT_SUCCESS

    # Setup work directory
    try:
        if args.verbose:
            console.print("\n[dim]Setting up work directory:[/dim]")
        marker_token = setup_work_dir(ctx, console)
        ctx = ctx._replace(marker_token=marker_token)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return EXIT_INVALID_PATH
    except Exception as e:
        console.print(f"[red]Error setting up work directory: {e}[/red]")
        return EXIT_INVALID_PATH

    exit_code = EXIT_SUCCESS
    original_cwd = Path.cwd()

    try:
        # Change to work directory
        os.chdir(ctx.work_dir)

        # Run path verification
        console.print()
        paths_result = verify_paths(Path("contracts"))

        if not paths_result["ok"]:
            _print_paths(paths_result)
            exit_code = EXIT_PATH_FAILURE
        elif args.paths_only:
            _print_paths(paths_result)
            console.print("[green]✓ Path verification passed[/green]")
        else:
            # Run tests
            console.print()
            contracts_path = Path("contracts")

            registry = ExecutorRegistry.discover()
            runner = ContractRunner(
                executors=registry,
                artifacts_root=Path("artifacts"),
            )
            report = runner.run(contracts_path)
            _print_report(report)

            summ = report.get("summary", {})
            if summ.get("failed", 0) > 0 or summ.get("error", 0) > 0:
                exit_code = EXIT_TEST_FAILURE

    except Exception as e:
        console.print(f"[red]Error during execution: {e}[/red]")
        exit_code = EXIT_TEST_FAILURE

    finally:
        # Restore original directory
        os.chdir(original_cwd)

        # Cleanup
        cleaned = cleanup_work_dir(ctx, exit_code, console)

        # Print footer
        console.print()
        console.print("=" * 45)
        result_str = "[green]PASS[/green]" if exit_code == 0 else "[red]FAIL[/red]"
        console.print(f"Result: {result_str}")
        if cleaned:
            console.print(f"Cleaned: {ctx.work_dir}")
        else:
            console.print(f"Kept: {ctx.work_dir}")
        console.print("=" * 45)

    return exit_code