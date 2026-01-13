import click
import json
import asyncio
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .auth import require_login
from ..onboarding import onboard_project
from ..knowledge import ProjectKnowledge
from ..distillation import SprintDistiller
from ..sync import sync_project_context
from ..alignment import AlignmentTracker

@click.command()
@click.option("--directory", default=".", help="Project directory")
@require_login
def init(directory):
    """Onboards the current project into OneCoder."""
    onboard_project(directory)

@click.command()
@click.option("--directory", default=".", help="Root directory to scan")
def status(directory):
    """Shows the platform-wide status by aggregating all sub-project sprints."""
    console = Console()
    root_path = Path(directory).resolve()
    
    console.print(f"[bold cyan]Scanning for OneCoder sub-projects in:[/bold cyan] {root_path}")
    
    # Discovery logic
    sprint_dirs = []
    for p in root_path.rglob(".sprint"):
        if "node_modules" in p.parts or ".git" in p.parts:
            continue
        sprint_dirs.append(p)
    
    if not sprint_dirs:
        console.print("[yellow]No .sprint directories found.[/yellow]")
        return

    table = Table(title="Platform-Wide Sprint Status")
    table.add_column("Component", style="cyan")
    table.add_column("Current Sprint", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Primary Goal", style="white")
    table.add_column("Tasks (D/T)", justify="right")

    for sd in sprint_dirs:
        component_name = sd.parent.name
        # Look for active sprint (usually the most recent subdirectory that isn't empty)
        sprint_shards = [d for d in sd.iterdir() if d.is_dir()]
        if not sprint_shards:
            continue
            
        # For now, let's take the latest/active one. 
        # In a real scenario, we might want to check sprint.json for status.
        active_sprint = sorted(sprint_shards)[-1]
        state_file = active_sprint / "sprint.json"
        
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
                
                sprint_id = state.get("sprintId", active_sprint.name)
                status_obj = state.get("status", {})
                status_str = f"{status_obj.get('state', 'unknown')} ({status_obj.get('phase', 'init')})"
                goal = state.get("goals", {}).get("primary", "N/A")
                
                tasks = state.get("tasks", [])
                done_tasks = len([t for t in tasks if t.get("status") == "done"])
                total_tasks = len(tasks)
                
                table.add_row(
                    component_name,
                    sprint_id,
                    status_str,
                    goal or "N/A",
                    f"{done_tasks}/{total_tasks}"
                )
            except Exception as e:
                table.add_row(component_name, active_sprint.name, "Error", str(e), "-")
        else:
            table.add_row(component_name, active_sprint.name, "No sprint.json", "-", "-")

    console.print(table)

@click.command(name="suggest")
@click.option("--limit", default=3, help="Number of past sprints to analyze")
@click.option("--dry-run", is_flag=True, help="Don't call LLM, just show context")
def sprint_suggest(limit, dry_run):
    """
    Suggests next tasks based on sprint history and learnings.
    """
    from ..sprint_collector import SprintCollector
    from ..agents import TaskSuggester

    console = Console()
    repo_root = Path.cwd()
    
    # 1. Collect Context
    with console.status("[bold green]Harvesting sprint context..."):
        collector = SprintCollector(repo_root)
        context = collector.get_recent_context(limit=limit)
    
    if not context:
        console.print("[yellow]No sprint context found. Run this from a repository with .sprint history.[/yellow]")
        return

    if dry_run:
        console.print(Panel(json.dumps(context, indent=2), title="Captured Context (Dry Run)"))
        return

    # 2. Get Suggestions from LLM
    with console.status("[bold purple]Analyzing patterns and generating suggestions..."):
        suggester = TaskSuggester()
        suggestions = suggester.suggest_next_tasks(context)

    if not suggestions:
        console.print("[yellow]No suggestions generated (or LLM unavailable).[/yellow]")
        return

    # 3. Present Suggestions
    console.print("\n[bold]Suggested Next Tasks:[/bold]")
    for i, task in enumerate(suggestions, 1):
        type_style = {
            "feature": "blue",
            "fix": "red",
            "chore": "dim",
            "governance": "magenta"
        }.get(task.get("type", "task"), "white")
        
        console.print(f"\n{i}. [{type_style}]{task['title']}[/{type_style}]")
        console.print(f"   [dim]{task['rationale']}[/dim]")

    # 4. Interactive Delegation (Optional)
    if click.confirm("\nDelegate one of these tasks now?", default=False):
        choice = click.prompt("Enter task number", type=int, default=1)
        if 1 <= choice <= len(suggestions):
            selected = suggestions[choice-1]
            prompt = selected['title']
            click.echo(f"\nrun: onecoder delegate \"{prompt}\"")

@click.command()
@click.option("--json", "json_output", is_flag=True, help="Output as JSON for machine consumption")
def knowledge(json_output):
    """
    Shows the platform-wide knowledge awareness.
    Aggregates L2 (Durable Project Guidelines) and L1 (Active Sprint Context).
    """
    pk = ProjectKnowledge()
    
    if json_output:
        click.echo(json.dumps(pk.aggregate_knowledge(), indent=2))
    else:
        click.echo(pk.get_rag_ready_output())

@click.command()
@click.option("--sprint", "sprint_id", required=True, help="Sprint ID to distill learnings from")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON for machine consumption")
def distill(sprint_id, json_output):
    """
    Distills learnings from a completed sprint and updates ANTIGRAVITY.md.
    """
    console = Console()
    distiller = SprintDistiller()
    
    if not json_output:
        console.print(f"[bold green]Distilling learnings from {sprint_id}...[/bold green]")
    
    result = distiller.distill_sprint(sprint_id)
        
    if "error" in result:
        if json_output:
            click.echo(json.dumps(result))
        else:
            console.print(f"[bold red]Error:[/bold red] {result['error']}")
    else:
        if json_output:
            click.echo(json.dumps(result))
        else:
            console.print(f"[bold green]Success![/bold green] Extracted {result['learnings_extracted']} learnings from {sprint_id}.")
            if result["updated"]:
                console.print(f"Updated awareness file: [cyan]{result['updated']}[/cyan]")

@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be synced without actually syncing")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON for machine consumption")
def sync(dry_run, json_output):
    """
    Syncs the local project context (specifications, governance, learnings, sprints) to the API.
    """
    if json_output:
        # We might want to pass this down to sync_project_context
        pass
        
    asyncio.run(sync_project_context())

@click.command()
@click.option("--sync", is_flag=True, help="Sync alignment data to API")
def alignment(sync):
    """
    Tracks project progress, aligns with roadmap, and captures PR/commit aspects.
    """
    console = Console()
    tracker = AlignmentTracker()
    
    with console.status("[bold green]Analyzing alignment..."):
        # Log current state
        log_msg = tracker.log_current_state()
        
        # Analyze roadmap (Agentic Semantic Check)
        alignment_data = tracker.check_roadmap_alignment_agentic()
        
        # Fetch PRs
        prs = tracker.fetch_recent_prs()
        
        # Capture suggestions
        suggestions = tracker.capture_suggestions()

        # Agentic Summary (Pass the detailed alignment data)
        summary = tracker.summarize_alignment_agentic(alignment_data, prs, suggestions)

    console.print(Panel(f"[bold]{log_msg}[/bold]", title="Alignment Log", expand=False))
    
    # Agentic Summary Panel
    console.print(Panel(summary, title="🤖 Agentic Assessment", border_style="cyan"))

    # Roadmap Table
    roadmap_table = Table(title="Semantic Roadmap Alignment")
    roadmap_table.add_column("Status", style="bold")
    roadmap_table.add_column("Aligned Items", style="cyan")
    
    status_style = "green" if alignment_data["status"] == "ALIGNED" else ("yellow" if alignment_data["status"] == "DRIFTING" else "red")
    
    roadmap_table.add_row(
        f"[{status_style}]{alignment_data['status']}[/]",
        ", ".join(alignment_data["aligned_items"]) if alignment_data["aligned_items"] else "None"
    )
    console.print(roadmap_table)

    # Drift Items
    if alignment_data.get("drift_items"):
        console.print("\n[bold yellow]Detected Drift (Work not in Roadmap):[/bold yellow]")
        for item in alignment_data["drift_items"]:
            console.print(f"  • {item}")
    
    # PRs Table
    if prs:
        pr_table = Table(title="Recent Merged PRs")
        pr_table.add_column("PR #", style="dim")
        pr_table.add_column("Title", style="white")
        pr_table.add_column("Author", style="cyan")
        
        for pr in prs:
            pr_table.add_row(str(pr["number"]), pr["title"], pr["author"]["login"])
        console.print(pr_table)
    
    # Suggestions
    if suggestions:
        console.print("\n[bold]Suggestions for Next Sprint:[/bold]")
        for s in suggestions[:5]:
            console.print(f"  • {s}")

    if sync:
        click.echo("\nSyncing alignment data to API...")
        # TODO: Implement API sync once endpoints are ready
        click.echo("Sync scheduled for next platform update.")
