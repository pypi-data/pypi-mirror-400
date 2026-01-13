import asyncio
import click
import re
from typing import Optional, Dict, Any, Callable, Awaitable
from ..api_client import get_api_client
from ..config_manager import config_manager
from ..issues import IssueManager

async def governed_retry_loop(
    task_fn: Callable[[], Awaitable[bool]],
    task_id: str,
    project_id: str,
    sprint_id: str,
    max_retries: int = 3,
    error_callback: Optional[Callable[[Exception], Dict[str, Any]]] = None
) -> bool:
    """
    Executes a task with a governed retry loop, KB lookups, and GitHub fallback.
    """
    token = config_manager.get_token()
    client = get_api_client(token) if token else None
    
    for attempt in range(1, max_retries + 1):
        click.secho(f"\n[Governance] Attempt {attempt}/{max_retries} for task {task_id}", fg="cyan")
        
        try:
            success = await task_fn()
            if success:
                # Log success if it was a retry
                if attempt > 1 and client:
                    try:
                        await client.log_retry({
                            "projectId": project_id,
                            "sprintId": sprint_id,
                            "taskId": task_id,
                            "attempt": attempt,
                            "status": "resolved"
                        })
                    except Exception:
                        pass
                return True
        except Exception as e:
            click.secho(f"Task failed: {e}", fg="red")
            
            # Extract error signature
            signature = error_callback(e) if error_callback else {"message": str(e)}
            
            # Log retry attempt
            if client:
                try:
                    await client.log_retry({
                        "projectId": project_id,
                        "sprintId": sprint_id,
                        "taskId": task_id,
                        "attempt": attempt,
                        "signature": signature,
                        "status": "active" if attempt < max_retries else "exhausted"
                    })
                except Exception:
                    pass
                
                # Search KB for resolution
                click.secho("Searching Knowledge Base for known resolutions...", fg="dim")
                try:
                    entries = await client.search_knowledge(signature.get("message", ""), project_id=project_id)
                    if entries:
                        click.secho("\n[KB Match Found]", fg="green", bold=True)
                        for entry in entries:
                            click.echo(f"  • {entry['title']}")
                            if entry.get("category") == "resolution":
                                click.secho(f"    Suggested resolution: {entry.get('metadata', {}).get('tt_log', 'See log')}", fg="yellow")
                        
                        if click.confirm("Apply suggested resolution and retry?"):
                            # Logic to apply resolution would go here in DebugAgent.
                            # For the scaffold, we just continue.
                            continue
                except Exception:
                    pass
            
            if attempt == max_retries:
                click.secho("Retry limit reached. Escalating to GitHub Issues...", fg="red", bold=True)
                
                # 1. Create local Issue
                issue_manager = IssueManager()
                telemetry = {
                    "message": str(e),
                    "error_type": type(e).__name__,
                    "context": {
                        "sprint_id": sprint_id,
                        "task_id": task_id
                    }
                }
                issue_path = issue_manager.create_from_telemetry(telemetry)
                click.echo(f"Local issue created: {issue_path}")
                
                # 2. Sync to GitHub (via API sync endpoint)
                if client:
                    try:
                        await client.sync_issues({
                            "projectId": project_id,
                            "issues": issue_manager.get_all_issues()
                        })
                        click.secho("✓ Issue synchronized to GitHub.", fg="green")
                    except Exception as sync_err:
                        click.secho(f"Failed to sync issue to GitHub: {sync_err}", fg="yellow")
                
                return False
            
            # Wait before next attempt
            wait_time = 2 ** attempt
            click.echo(f"Waiting {wait_time}s before next attempt...")
            await asyncio.sleep(wait_time)

    return False
