import click
import re
from datetime import datetime
from pathlib import Path
from ..issues import IssueManager
from ..config_manager import config_manager
try:
    from ai_sprint.telemetry import FailureModeCapture
except ImportError:
    FailureModeCapture = None

@click.group()
def issue():
    """Manage platform governance issues."""
    pass

@issue.command(name="create")
@click.option("--from-telemetry", is_flag=True, help="Create issue from latest telemetry failure")
@click.option("--title", help="Manual title for the issue")
def issue_create(from_telemetry, title):
    """Create a new governance issue."""
    from rich.console import Console
    console = Console()
    
    manager = IssueManager()
    
    if from_telemetry:
        if FailureModeCapture is None:
            console.print("[red]Error: Telemetry features not available in this installation.[/red]")
            return

        capture = FailureModeCapture()
        failures = capture.get_failures(limit=1)
        if not failures:
            console.print("[yellow]No recent failures found in telemetry.[/yellow]")
            return
            
        failure = failures[0]
        issue_path = manager.create_from_telemetry(failure, title=title)
        console.print(f"[bold green]✓ Issue created from telemetry:[/bold green] {issue_path.name}")
    else:
        # Future: manual issue creation wizard
        console.print("[yellow]Manual issue creation not yet implemented. Use --from-telemetry.[/yellow]")

@issue.command(name="resolve")
@click.argument("issue_id")
@click.option("--message", "-m", help="Resolution message")
@click.option("--pr", help="Pull Request URL")
def issue_resolve(issue_id, message, pr):
    """Mark an issue as resolved."""
    from rich.console import Console
    import subprocess
    
    console = Console()
    manager = IssueManager()
    
    # 1. Get Resolution Metadata
    resolution_meta = {
        "user": config_manager.get_user(),
        "resolved_at": datetime.now().isoformat(),
        "pr_url": pr
    }
    
    # Get Current Commit
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        resolution_meta["commit_sha"] = commit
    except Exception:
        resolution_meta["commit_sha"] = "unknown"
        
    # 2. Update Status
    success = manager.update_status(issue_id, "resolved", resolution_meta)
    
    if success:
        console.print(f"[bold green]✓ Issue {issue_id} marked as resolved.[/bold green]")
        console.print(msg="Resolution metadata captured.", style="dim")
    else:
        console.print(f"[bold red]Error:[/bold red] Issue {issue_id} not found.")

@issue.command(name="sync")
@click.option("--input", "-i", type=click.Path(exists=True), help="Input issue file/directory (optional)")
def issue_sync(input):
    """Sync local governance issues to the OneCoder API."""
    import asyncio
    from ..sync import sync_issues, ProjectConfig
    from ..api_client import get_api_client
    
    # Setup
    token = config_manager.get_token()
    if not token:
        click.secho("Error: Not logged in.", fg="red")
        return

    repo_root = Path.cwd() # Should use find_repo_root from sync.py really, importing locally
    proj_config = ProjectConfig(repo_root)
    project_id = proj_config.get_project_id()
    
    if not project_id:
        click.secho("Error: Project ID not found.", fg="red")
        return

    client = get_api_client(token)
    
    # Run Sync
    asyncio.run(sync_issues(client, project_id))

@issue.command(name="list")
def issue_list():
    """List all local governance issues."""
    from rich.console import Console
    from rich.table import Table
    console = Console()
    
    manager = IssueManager()
    issues_dir = manager.issues_dir
    if not issues_dir.exists():
        console.print("[yellow]No .issues directory found.[/yellow]")
        return
        
    table = Table(title="Local Governance Issues")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="magenta")
    
    for item in sorted(issues_dir.iterdir()):
        if item.is_file() and item.suffix == ".md" and item.name != "README.md":
            match = re.match(r"^(\d{3})-(.+)\.md$", item.name)
            if match:
                issue_id = match.group(1)
                issue_title = match.group(2).replace("-", " ").capitalize()
                
                # Try to parse status from file
                content = item.read_text()
                if any(x in content for x in ["Resolved", "🟢 Resolved", "🟢 **Resolved**"]):
                    status = "[green]Resolved[/green]"
                elif any(x in content for x in ["Open", "🔴 Open", "🔴 **Open**"]):
                    status = "[red]Open[/red]"
                else:
                    status = "[yellow]Unknown[/yellow]"
                    
                table.add_row(issue_id, issue_title, status)
                
    console.print(table)
