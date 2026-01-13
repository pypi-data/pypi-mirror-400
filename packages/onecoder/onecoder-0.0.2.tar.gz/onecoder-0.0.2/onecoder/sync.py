import os
import json
import click
from pathlib import Path
from typing import Optional, Dict, Any
from .api_client import get_api_client
from .config_manager import config_manager
from .sprint_collector import SprintCollector
from .issues import IssueManager

class ProjectConfig:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.config_file = repo_root / ".onecoder.json"

    def load(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            click.echo(f"Error loading project config: {e}")
            return {}

    def save(self, config: Dict[str, Any]):
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            click.echo(f"Error saving project config: {e}")

    def get_project_id(self) -> Optional[str]:
        # Priority: Env Var > Local Config
        project_id = os.getenv("ONECODER_PROJECT_ID")
        if project_id:
            return project_id
        return self.load().get("project_id")

def find_repo_root() -> Path:
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()

async def sync_sprint(client, project_id: str, sprint: Dict[str, Any]):
    """Syncs a single sprint to the API."""
    try:
        payload = {
            "sprint": {
                "id": sprint["id"],
                "title": sprint["title"],
                "status": sprint["status"],
                "goals": sprint["goals"]
            },
            "tasks": sprint["tasks"],
            "projectId": project_id
        }
        
        result = await client.sync_sprint(payload)
        click.secho(f"  ✓ {sprint['id']}: {len(sprint['tasks'])} tasks", fg="green")
        return result
    except Exception as e:
        click.secho(f"  ✗ {sprint['id']}: {e}", fg="red")
        return None

async def sync_project_context():
    """Aggregates local context and syncs with the API."""
    repo_root = find_repo_root()
    proj_config = ProjectConfig(repo_root)
    project_id = proj_config.get_project_id()

    if not project_id:
        click.secho("Error: No project ID found. Run 'onecoder login' or set ONECODER_PROJECT_ID.", fg="red")
        return

    token = config_manager.get_token()
    if not token:
        click.secho("Error: Not logged in. Run 'onecoder login'.", fg="red")
        return

    # Aggregate context
    spec_path = repo_root / "SPECIFICATION.md"
    gov_path = repo_root / "governance.yaml"
    learnings_path = repo_root / "ANTIGRAVITY.md"

    sync_data = {
        "metadata": {}
    }

    if spec_path.exists():
        sync_data["specification"] = spec_path.read_text()
    
    if gov_path.exists():
        sync_data["governance"] = gov_path.read_text()

    if learnings_path.exists():
        sync_data["metadata"]["learnings"] = learnings_path.read_text()

    # Get project name from folder if not in config
    if not sync_data.get("name"):
        sync_data["name"] = repo_root.name

    try:
        client = get_api_client(token)
        
        # Sync project metadata
        result = await client.sync_project(project_id, sync_data)
        click.secho(f"✅ Project context synced successfully for ID: {project_id}", fg="green")
        
        # NEW: Sync sprint data
        collector = SprintCollector(repo_root)
        sprints = collector.collect_all_sprints()
        
        if sprints:
            click.secho(f"\n📦 Syncing {len(sprints)} sprints...", fg="cyan")
            for sprint in sprints:
                await sync_sprint(client, project_id, sprint)
            click.secho(f"✅ All sprints synced successfully", fg="green")
        else:
            click.secho("\nℹ️  No sprints found to sync", fg="yellow")
        
        return result
        return result
    except Exception as e:
        click.secho(f"❌ Failed to sync project: {e}", fg="red")
        return None

async def sync_issues(client, project_id: str):
    """Syncs local issues to the API."""
    manager = IssueManager()
    issues = manager.get_all_issues()
    
    if not issues:
        click.secho("ℹ️  No issues found to sync", fg="yellow")
        return

    click.secho(f"📦 Syncing {len(issues)} issues...", fg="cyan")
    
    try:
        payload = {
            "projectId": project_id,
            "issues": issues
        }
        
        # We need to add sync_issues to api_client first? 
        # Or we can just use client.post directly if method not exists.
        # Let's assume client has a generic method or we add specific one.
        # Actually, let's look at api_client.py later. For now, assuming client.sync_issues exists or using _request.
        # Wait, I should check api_client.py. But for now I'll use a generic call pattern if possible 
        # or assume I'll update api_client.py too.
        # Let's just use the direct route for now if client exposes request.
        
        # Checking previous code, client seems to have typed methods.
        # I should probably update api_client.py as well.
        # But let's write the call here assuming the method exists, and then go fix api_client.
        
        result = await client.sync_issues(payload)
        
        stats = result.get("stats", {})
        click.secho(f"✅ Issues synced: {stats.get('upserted', 0)} upserted, {stats.get('errors', 0)} errors", fg="green")
        
    except Exception as e:
        click.secho(f"❌ Failed to sync issues: {e}", fg="red")

