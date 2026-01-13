import click
import json
import os
import re
import subprocess
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any
from .common import console, PROJECT_ROOT, SPRINT_DIR, SprintStateManager, auto_detect_sprint_id
from ..commit import validate_trailers, create_commit_with_trailers
from ..spec_validator import validate_spec_ids
from ..trace import trace_specifications
from ..preflight import SprintPreflight
from ..policy import PolicyEngine

@click.command()
@click.option("--message", "-m", required=True, help="Commit message")
@click.option("--task-id", help="Task identifier")
@click.option("--status", type=click.Choice(["planning", "in-progress", "review", "done"]), help="Task status")
@click.option("--validation", help="Validation status or URI")
@click.option("--sprint-id", help="Override sprint ID")
@click.option("--spec-id", help="Specification ID(s)")
@click.option("--component", help="Component scope")
def commit(message, task_id, status, validation, sprint_id, spec_id, component):
    """Create atomic commit with metadata trailers."""
    trailers = {}
    active_sprint_id = sprint_id or auto_detect_sprint_id()
    if active_sprint_id:
        trailers["Sprint-Id"] = active_sprint_id
        if not component:
            try:
                state_manager = SprintStateManager(SPRINT_DIR / active_sprint_id)
                component = state_manager.get_component()
            except Exception: pass
    if component: trailers["Component"] = component
    
    if task_id:
        if not re.match(r"^task-\d+$", task_id):
            resolved = None
            if active_sprint_id:
                try:
                    state_manager = SprintStateManager(SPRINT_DIR / active_sprint_id)
                    resolved = state_manager.get_task_id_by_title(task_id)
                except Exception: pass
            if not resolved and task_id.isdigit():
                resolved = f"task-{int(task_id):03d}"
            if resolved:
                console.print(f"[dim]Resolved Task ID: {task_id} -> {resolved}[/dim]")
                task_id = resolved
        trailers["Task-Id"] = task_id

    if status:
        if status == "done":
            try:
                result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
                staged_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
                has_impl_changes = any(not (f.startswith(".sprint/") or f in ["TODO.md", "RETRO.md", "README.md", "sprint.json"]) for f in staged_files)
                is_exception = any(x in message.lower() for x in ["docs", "chore", "governance"])
                if not has_impl_changes and not is_exception:
                    console.print("[bold red]Error:[/bold red] Implementation Integrity Violation (SPEC-GOV-008.2)")
                    sys.exit(1)
            except Exception: pass
        trailers["Status"] = status

    if validation: trailers["Validation"] = validation
    if spec_id:
        is_valid, errors = validate_spec_ids(spec_id, PROJECT_ROOT)
        if not is_valid:
            for error in errors: console.print(f"  ❌ {error}")
            sys.exit(1)
        trailers["Spec-Id"] = spec_id

    errors = validate_trailers(trailers)
    if errors:
        for error in errors: console.print(f"  ❌ {error}")
        sys.exit(1)

    from ..submodule import get_unpushed_submodules
    if get_unpushed_submodules(PROJECT_ROOT):
        console.print("[bold red]Error:[/bold red] Unpushed submodule changes detected.")
        sys.exit(1)

    if create_commit_with_trailers(message, trailers):
        console.print("[bold green]Success:[/bold green] Commit created.")
    else:
        sys.exit(1)

@click.command()
@click.option("--sprint-id", help="Override sprint ID")
def verify(sprint_id):
    """Verify sprint for technical debt (Zero Errors/Lint)."""
    active_sprint = sprint_id or auto_detect_sprint_id()
    if not active_sprint:
        console.print("[bold red]Error:[/bold red] No active sprint detected.")
        sys.exit(1)
    target_dir = SPRINT_DIR / active_sprint
    state_manager = SprintStateManager(target_dir)
    component = state_manager.get_component()
    if not component:
        console.print("[yellow]Warning:[/yellow] No component scope defined.")
        return

    console.print(f"[cyan]Verifying component debt for [bold]{component}[/bold]...[/cyan]")
    policy_engine = PolicyEngine(PROJECT_ROOT)
    comp_rules = policy_engine.get_verification_rules().get(component, [])
    
    results = {"errors": 0, "lint_violations": 0, "details": []}
    for check in comp_rules:
        cmd = check if isinstance(check, str) else check['cmd']
        name = check if isinstance(check, str) else check['name']
        res = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT / component, capture_output=True, text=True)
        if res.returncode != 0:
            results["errors" if "lint" not in name.lower() else "lint_violations"] += 1
            console.print(f"  ❌ [bold red]{name} failed[/bold red]")
        else:
            console.print(f"  ✅ [green]{name} passed[/green]")
    
    with open(target_dir / ".verification_results.json", "w") as f:
        json.dump(results, f)
    if results["errors"] > 0 or results["lint_violations"] > 0:
        sys.exit(1)
    console.print("\n[bold green]✓ Zero-Debt Verification Passed.[/bold green]")

@click.command()
@click.option("--fix", is_flag=True, help="Attempt to fix simple issues")
@click.option("--sprint-id", help="Sprint ID to preflight")
def preflight(fix, sprint_id):
    """Validate sprint readiness and governance adherence."""
    active_sprint = sprint_id or auto_detect_sprint_id()
    if not active_sprint:
        console.print("[bold red]Error:[/bold red] No active sprint detected.")
        return
    sprint_dir = SPRINT_DIR / active_sprint
    preflight_engine = SprintPreflight(sprint_dir, PROJECT_ROOT)
    score, results = preflight_engine.run_all()
    for res in results:
        status_icon = "✅" if res["status"] == "passed" else ("❌" if res["status"] == "failed" else "⚠️")
        color = "green" if res["status"] == "passed" else ("red" if res["status"] == "failed" else "yellow")
        console.print(f"  {status_icon} [{color}]{res['name']}[/{color}]: {res['message']}")
    if score < 75: sys.exit(1)

@click.command()
@click.argument("name")
@click.option("--pr/--no-pr", is_flag=True, default=True, help="Create pull request after closing sprint")
@click.option("--apply", is_flag=True, help="Execute the closure (Apply phase)")
@click.option("--plan", is_flag=True, default=True, help="Only show what would be done (Plan phase, default)")
def close(name, pr, apply, plan):
    """Close a sprint if criteria are met (Plan-Apply pattern)."""
    from ..pr_creator import create_pull_request
    from ..visual_generator import generate_visual_assets
    from ..policy import PolicyEngine
    
    is_apply = apply
    target_dir = SPRINT_DIR / name
    if not target_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Sprint {name} does not exist.")
        sys.exit(1)
    
    console.print(f"[cyan]Evaluating governance policy for {name}...[/cyan]")
    policy_engine = PolicyEngine(PROJECT_ROOT)

    visual_policy = policy_engine.get_visual_policy()
    if visual_policy.get("auto_generate_on_close"):
        media_dir = target_dir / "media"
        if is_apply or media_dir.exists() or plan:
             console.print(f"[cyan]Ensuring visual assets for {name}...[/cyan]")
             try:
                 generate_visual_assets(target_dir, name)
             except Exception as e:
                 if "Google IDE" not in str(e):
                     console.print(f"[yellow]Warning:[/yellow] Visual generation issue: {e}")

    closure_rules = policy_engine.get_closure_policy()
    violations = policy_engine.evaluate_closure(target_dir)
    has_debt = any("Zero-Debt" in v or "verification has not been run" in v for v in violations)

    if closure_rules.get("require_zero_debt") and is_apply and has_debt:
        console.print(f"[cyan]Verifying zero-debt status for {name}...[/cyan]")
        try:
            ctx = click.get_current_context()
            ctx.invoke(verify, sprint_id=name)
        except SystemExit as e:
            if e.code != 0:
                console.print("[bold red]Cannot close: Zero-Debt verification failed.[/bold red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Verification could not be run: {e}")

    violations = policy_engine.evaluate_closure(target_dir)
    if violations:
        console.print("[bold red]Cannot close: Governance Policy Violations Detected![/bold red]")
        for v in violations: console.print(f"  ❌ {v}")
        if not is_apply: console.print("\n[dim]Tip: Run with --apply to attempt automatic fixes.[/dim]")
        sys.exit(1)
    
    if not is_apply:
        console.print("\n[bold cyan]--- Sprint Close PLAN ---[/bold cyan]")
        console.print("[dim]Governance: OK[/dim]")
    
    from ..submodule import get_unpushed_submodules
    if get_unpushed_submodules(PROJECT_ROOT):
        console.print("[bold red]Cannot close:[/bold red] Unpushed submodule commits detected.")
        sys.exit(1)

    try:
        # Check for staged changes
        staged = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, cwd=PROJECT_ROOT)
        if staged.returncode == 0 and staged.stdout.strip():
             console.print("[bold red]Cannot close:[/bold red] Found staged changes.")
             sys.exit(1)

        # Check for unstaged changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=PROJECT_ROOT)
        if result.returncode == 0 and result.stdout.strip():
            uncommitted_files = [f for f in result.stdout.strip().split("\n") 
                                if not (f[3:].startswith(".sprint/") or f[3:].endswith(".json") or f[3:] in ["TODO.md", "RETRO.md", "README.md", "sprint.json"])]
            if uncommitted_files:
                console.print(f"[bold red]Cannot close:[/bold red] Found {len(uncommitted_files)} uncommitted implementation changes.")
                sys.exit(1)
    except Exception as e: console.print(f"[yellow]Warning:[/yellow] Git check: {e}")

    # TODO.md check
    todo_file = target_dir / "TODO.md"
    if todo_file.exists():
        with open(todo_file, "r") as f: lines = f.readlines()
        delivery_sections = ["## High Priority", "## Implementation"]
        in_delivery_section = True
        incomplete_tasks = []
        for line in lines:
            if line.startswith("## "):
                section_name = line.strip()
                if section_name in delivery_sections: in_delivery_section = True
                elif section_name in ["## Backlog", "## Future"]: in_delivery_section = False
                else: in_delivery_section = "backlog" not in section_name.lower()
            if in_delivery_section:
                match = re.match(r"-\s*\[\s\]\s*(.+)", line)
                if match and match.group(1).strip(): incomplete_tasks.append(match.group(1).strip())
        if incomplete_tasks:
            console.print(f"[bold red]Cannot close:[/bold red] Found {len(incomplete_tasks)} incomplete tasks.")
            sys.exit(1)

    retro_file = target_dir / "RETRO.md"
    if not retro_file.exists() or retro_file.stat().st_size < 50:
        console.print("[bold red]Cannot close:[/bold red] RETRO.md missing or too short.")
        sys.exit(1)

    # BAKE-IT check
    try:
        trace_map = trace_specifications(PROJECT_ROOT, limit=500)
        sprint_flags = [f for f in trace_map.get("audit", []) if name in str(f.get("message", "")) or name == f.get("id") or (f.get("sprint_id") == name)]
        if sprint_flags:
            console.print("[bold red]Cannot close: BAKE-IT Anti-Patterns Detected![/bold red]")
            sys.exit(1)
    except Exception as e: console.print(f"[yellow]Warning:[/yellow] Audit check skipped: {e}")

    if not is_apply:
        console.print("\n[bold green]Plan phase complete.[/bold green]")
        return

    # Apply phase
    (target_dir / ".status").write_text("Closed")
    try:
        to_add = [a for a in [str(target_dir.relative_to(PROJECT_ROOT)), "TODO.md", "RETRO.md", "README.md", "sprint.json"] if (PROJECT_ROOT / a).exists()]
        if to_add:
            subprocess.run(["git", "add"] + to_add, cwd=PROJECT_ROOT, check=True)
            commit_msg = f"chore(gov): close sprint {name}\n\n[Sprint-Id: {name}]\n[Status: closed]"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
    except Exception as e: console.print(f"[yellow]Warning:[/yellow] Governance commit failed: {e}")

    console.print(f"[bold green]Success:[/bold green] Sprint {name} closed.")
    if pr:
        try:
            create_pull_request(target_dir, name)
            console.print("[green]✓[/green] Pull request created")
        except Exception as e: console.print(f"[bold red]Error:[/bold red] PR failed: {e}")

@click.command()
@click.option("--limit", default=100, help="Number of commits to trace")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def audit(limit, staged):
    """Run a comprehensive audit on current project."""
    # Placeholder for audit logic
    pass

@click.command()
@click.option("--component", help="Filter by component")
@click.option("--category", help="Filter by category")
def backlog(component, category):
    """View consolidated backlog."""
    # Placeholder for backlog logic
    pass
