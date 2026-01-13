import click
import re
import subprocess
from pathlib import Path
from .common import console, PROJECT_ROOT, SPRINT_DIR, SprintStateManager, auto_detect_sprint_id

def create_sprint_structure(target_dir: Path, name: str, exist_ok: bool = False):
    target_dir.mkdir(parents=True, exist_ok=exist_ok)
    (target_dir / "planning").mkdir(exist_ok=True)
    (target_dir / "logs").mkdir(exist_ok=True)
    (target_dir / "context").mkdir(exist_ok=True)
    (target_dir / "media").mkdir(exist_ok=True)

    readme_file = target_dir / "README.md"
    if not readme_file.exists():
        with open(readme_file, "w") as f:
            f.write(f"# Sprint: {name}\n\n## Goal\nDescribe the goal of this sprint.\n")

    tasks_file = target_dir / "planning" / "tasks.md"
    if not tasks_file.exists():
        with open(tasks_file, "w") as f:
            f.write("# Tasks\n\n- [ ] Initial Task\n")

    todo_file = target_dir / "TODO.md"
    if not todo_file.exists():
        with open(todo_file, "w") as f:
            f.write("# Sprint TODO\n\n## High Priority\n- [ ] \n\n## Backlog\n- [ ] \n")

    retro_file = target_dir / "RETRO.md"
    if not retro_file.exists():
        with open(retro_file, "w") as f:
            f.write(
                "# Retrospective\n\n"
                "## Went Well\n\n"
                "## To Improve\n\n"
                "## Action Items\n\n"
                "## Visual Assets\n"
                "<!-- Generated diagrams and flowcharts will be referenced here -->\n"
            )

@click.command()
@click.argument("name", required=False)
@click.option("--name", "name_option", help="Name of the sprint directory")
@click.option("--branch/--no-branch", default=True, help="Automatically create and switch to a git branch")
@click.option("--component", help="Component scope for this sprint")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
def init(name, name_option, branch, component, yes):
    """Initialize a new sprint directory structure."""
    if not name:
        name = name_option
    if not name:
        name = click.prompt("Sprint Name")

    if not yes and not click.confirm("Have you reviewed the pending .issues/ and backlog?"):
        console.print("[bold yellow]Aborted.[/bold yellow]")
        return

    if not re.match(r"^\d{3}-", name):
        max_num = 0
        if SPRINT_DIR.exists():
            for item in SPRINT_DIR.iterdir():
                if item.is_dir():
                    match = re.match(r"^(\d{3})-", item.name)
                    if match:
                        num = int(match.group(1))
                        if num > max_num:
                            max_num = num
        next_num = max_num + 1
        name = f"{next_num:03d}-{name}"

    target_dir = SPRINT_DIR / name
    if target_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Directory {target_dir} already exists.")
        return

    try:
        create_sprint_structure(target_dir, name)
        state_manager = SprintStateManager(target_dir)
        initial_state = state_manager.create_initial_state(name, name, component)
        state_manager.save(initial_state)
        console.print(f"[bold green]Success:[/bold green] Initialized sprint at [cyan]{target_dir}[/cyan]")

        if branch:
            branch_name = f"sprint/{name}"
            subprocess.run(["git", "checkout", "-b", branch_name], check=True, capture_output=True)
            console.print(f"[bold green]Success:[/bold green] Created branch [cyan]{branch_name}[/cyan]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to initialize: {e}")
        return

    console.print("\n[cyan]Running sprint preflight check...[/cyan]")
    from ..preflight import SprintPreflight
    preflight = SprintPreflight(target_dir, PROJECT_ROOT)
    score, results = preflight.run_all()
    
    for res in results:
        status_icon = "✅" if res["status"] == "passed" else ("❌" if res["status"] == "failed" else "⚠️")
        color = "green" if res["status"] == "passed" else ("red" if res["status"] == "failed" else "yellow")
        console.print(f"  {status_icon} [{color}]{res['name']}[/{color}]: {res['message']}")
        
    if score >= 75:
        console.print(f"\n[bold green]Preflight Passed![/bold green] Score: {score}/100")
    else:
        console.print(f"\n[bold red]Preflight Failed![/bold red] Score: {score}/100")

@click.command()
@click.argument("name")
def update(name):
    """Update an existing sprint with missing templates."""
    target_dir = SPRINT_DIR / name
    if not target_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Sprint {name} does not exist.")
        return
    try:
        create_sprint_structure(target_dir, name, exist_ok=True)
        console.print(f"[bold green]Success:[/bold green] Updated sprint at {target_dir}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to update: {e}")

@click.command()
def status():
    """Show the current status of the sprint."""
    if not SPRINT_DIR.exists():
        console.print("[yellow]No .sprint directory found.[/yellow]")
        return

    from rich.table import Table
    table = Table(title="Available Sprints")
    table.add_column("Sprint Name", style="cyan")
    table.add_column("Status", style="magenta")

    for item in sorted(SPRINT_DIR.iterdir()):
        if item.is_dir():
            status_file = item / ".status"
            state = "Active"
            if status_file.exists():
                with open(status_file, "r") as f:
                    state = f.read().strip()
            color = "green" if state == "Active" else "dim white"
            table.add_row(item.name, f"[{color}]{state}[/{color}]")
    console.print(table)
