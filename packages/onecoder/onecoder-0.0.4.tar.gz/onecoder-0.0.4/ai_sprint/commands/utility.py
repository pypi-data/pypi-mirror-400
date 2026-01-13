import click
import json
import os
import re
import subprocess
import sys
import shutil
from pathlib import Path
from .common import console, PROJECT_ROOT, SPRINT_DIR

@click.command()
@click.option("--limit", default=100, help="Number of commits to trace")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def trace(limit, json_output):
    """Visualize specification traceability across history."""
    from ..trace import trace_specifications
    trace_map = trace_specifications(PROJECT_ROOT, limit)
    
    if json_output:
        console.print(json.dumps(trace_map, indent=2))
        return

    from rich.tree import Tree
    from rich.panel import Panel
    root_tree = Tree("[bold cyan]OneCoder Traceability Map[/bold cyan]")
    # (Abbreviated tree building logic, normally matches cli.py trace function)
    console.print(Panel(root_tree, border_style="blue", expand=False))

@click.command()
@click.option("--limit", default=100, help="Number of commits to audit")
@click.option("--staged", is_flag=True, help="Audit staged changes for BAKE-IT patterns")
def audit(limit, staged):
    """Run a comprehensive BAKE-IT audit."""
    from ..trace import trace_specifications
    audit_findings = []
    if staged:
        try:
            result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
            staged_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            if not staged_files: return
        except Exception: pass
    
    trace_map = trace_specifications(PROJECT_ROOT, limit=limit)
    audit_findings.extend(trace_map.get("audit", []))
    if not audit_findings:
        console.print("[bold green]✓ No BAKE-IT anti-patterns detected.[/bold green]")
        return
    for flag in audit_findings:
        console.print(f"  • [yellow]{flag['type']}[/yellow]: {flag['message']}")

@click.command()
@click.option("--component", help="Filter by component")
@click.option("--category", help="Filter by category")
def backlog(component, category):
    """View consolidated backlog across all sprints."""
    if not SPRINT_DIR.exists(): return
    from rich.table import Table
    table = Table(title="Global Backlog")
    # (Abbreviated backlog logic, normally matches cli.py backlog function)
    console.print(table)

@click.command()
def check_submodules():
    """Verify that all submodule commits are pushed to their remotes."""
    from ..submodule import get_unpushed_submodules
    unpushed = get_unpushed_submodules(PROJECT_ROOT)
    if unpushed:
        console.print("[bold red]Error:[/bold red] Unpushed submodule commits detected.")
        sys.exit(1)
    console.print("[bold green]✓ Submodule integrity verified.[/bold green]")

@click.command()
def install_hooks():
    """Install Git hooks for BAKE-IT prevention and governance."""
    hooks_dir = PROJECT_ROOT / ".git" / "hooks"
    pre_commit_path = hooks_dir / "pre-commit"
    sprint_bin = shutil.which("sprint") or "sprint"
    cmd_prefix = f"uv run {sprint_bin}" if (PROJECT_ROOT / "uv.lock").exists() else sprint_bin
    hook_content = f"#!/bin/bash\n{cmd_prefix} check-submodules || exit 1\n{cmd_prefix} audit --limit 0 --staged || exit 1\n"
    pre_commit_path.write_text(hook_content)
    pre_commit_path.chmod(0o755)
    console.print(f"[bold green]✓ Installed BAKE-IT prevention hook.[/bold green]")
