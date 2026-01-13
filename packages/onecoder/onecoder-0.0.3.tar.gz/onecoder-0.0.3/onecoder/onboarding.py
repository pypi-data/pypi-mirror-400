import os
import click
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from .tools.kit_tools import kit_index_tool, kit_file_tree_tool, kit_symbols_tool
from .api_client import get_api_client
from .config_manager import config_manager
from .sync import sync_project_context, ProjectConfig

async def _ensure_project_setup(client, directory: str) -> Optional[str]:
    """
    Ensures a workspace is associated and a project is created on the server.
    Returns the project_id.
    """
    click.secho("\n[Project Setup] Verifying workspace and project association...", fg="cyan", bold=True)
    
    # Load local config
    p_config = ProjectConfig(Path(directory))
    config_data = p_config.load()
    workspace_id = config_data.get("workspace_id")
    project_id = config_data.get("project_id")

    # 1. Ensure Workspace
    if not workspace_id:
        workspaces = await client.get_workspaces()
        if workspaces:
            click.echo("Found available workspaces:")
            for idx, ws in enumerate(workspaces, 1):
                click.echo(f"  {idx}. {ws['name']} ({ws['id']})")
            
            choice = click.prompt("Select a workspace number or type 'new' to create one", default="1")
            if choice.lower() == "new":
                ws_name = click.prompt("Enter new workspace name")
                ws_result = await client.create_workspace(ws_name)
                workspace_id = ws_result["id"]
            else:
                workspace_id = workspaces[int(choice)-1]["id"]
        else:
            click.echo("No workspaces found.")
            ws_name = click.prompt("Create default workspace name", default="Personal")
            ws_result = await client.create_workspace(ws_name)
            workspace_id = ws_result["id"]
        
        # Save workspace ID
        config_data["workspace_id"] = workspace_id
        p_config.save(config_data)
        click.secho(f"✓ Associated with workspace ID: {workspace_id}", fg="green")
    else:
        click.echo(f"✓ Using existing workspace ID: {workspace_id}")

    # 2. Ensure Project
    if not project_id:
        # Check if project exists on server (by name or some other linking? For now just create)
        # We assume if we don't have an ID, we haven't linked it.
        # Use directory name as default project name
        default_name = os.path.basename(os.path.abspath(directory))
        proj_name = click.prompt("Enter project name on server", default=default_name)
        
        try:
            # We try to create. If name collision logic isn't robust in API, this might error.
            # Assuming API handles duplicates or we just handle error.
            # Ideally we check list first, but create is fine.
            new_project = await client.create_project(proj_name, workspace_id)
            project_id = new_project["id"]
            
            config_data["project_id"] = project_id
            p_config.save(config_data)
            click.secho(f"✓ Created/Linked project ID: {project_id}", fg="green")
            
        except Exception as e:
            click.secho(f"Warning: Failed to create project: {e}", fg="yellow")
            # Fallback: maybe list projects and let user select? 
            # For now, proceed without ID (some features might be limited)
            return None
    else:
        click.echo(f"✓ Using existing project ID: {project_id}")

    return project_id

def onboard_project(directory: str = "."):
    """
    Onboards a project into the OneCoder platform.
    """
    directory = os.path.abspath(directory)
    click.secho(f"🚀 Kickstarting OneCoder Onboarding for: {directory}", fg="cyan", bold=True)
    
    # Check for existing .sprint directory
    sprint_dir = os.path.join(directory, ".sprint")
    if not os.path.exists(sprint_dir):
        click.echo("No .sprint directory found. Setting up 'Sprint 000'...")
        os.makedirs(sprint_dir, exist_ok=True)
        with open(os.path.join(sprint_dir, "README.md"), "w") as f:
            f.write("# Sprint 000: Initialization\n\nInitial onboarding and project setup.")

    # --- Sync Preferences ---
    token = config_manager.get_token()
    preferences = {
        "artifacts": {
            "auto_capture": True,
            "destination": "sprint_context",
            "types": ["assessment", "implementation_plan", "task", "walkthrough"]
        },
        "sprint": {
            "auto_close_validation": True,
            "require_walkthrough": True
        }
    }

    if token:
        click.echo("Syncing preferences from API...")
        try:
            client = get_api_client(token)
            api_prefs = asyncio.run(client.get_preferences())
            preferences.update(api_prefs)
            click.echo("✓ Preferences synced successfully.")
        except Exception as e:
            click.secho(f"! Failed to sync preferences: {e}. Aborting.", fg="red")
            return
    else:
        click.secho("Error: No authentication token found. Please run 'onecoder login'.", fg="red")
        return

    # --- Check for Existing Agent/Config Docs (Refinement) ---
    agent_docs = {
        "AGENTS.md": Path(directory) / "AGENTS.md",
        "CLAUDE.md": Path(directory) / "CLAUDE.md",
        "GEMINI.md": Path(directory) / "GEMINI.md",
        ".cursorrules": Path(directory) / ".cursorrules"
    }
    readme_path = Path(directory) / "README.md"
    
    detected_agent_docs = {name: p for name, p in agent_docs.items() if p.exists()}
    
    scan_data = {}
    skip_deep_scan = False

    if detected_agent_docs:
        click.secho("🤖 Agent configuration detected. Optimizing onboarding...", fg="green")
        combined_context = ""
        if readme_path.exists():
            combined_context += f"--- README.md ---\n{readme_path.read_text()}\n\n"
        
        for name, p in detected_agent_docs.items():
            combined_context += f"--- {name} ---\n{p.read_text()}\n\n"
        
        scan_data["focused_context"] = combined_context
        skip_deep_scan = True
    
    # --- Check for Existing Artifacts (Optimization - Legacy Path) ---
    spec_path = Path(directory) / "SPECIFICATION.md"
    gov_path = Path(directory) / "governance.yaml"
    
    if spec_path.exists() and gov_path.exists():
        if click.confirm("\n📋 Existing project artifacts/configuration detected. Skip analysis and sync to remote?", default=True):
            click.echo("Skipping analysis...")
            try:
                # Ensure project setup
                asyncio.run(_ensure_project_setup(client, directory))
                # Invoke Sync
                click.echo("Syncing project context...")
                asyncio.run(sync_project_context())
                return
            except Exception as e:
                click.secho(f"Error during optimized sync: {e}", fg="red")
                return

    # --- Phase 1: Deep Codebase Scan (Skipped if focused context available) ---
    if not skip_deep_scan:
        click.secho("\n[Phase 1] Running deep codebase scan...", fg="yellow")
        
        index_json = kit_index_tool(directory)
        file_tree = kit_file_tree_tool(directory)
        symbols = kit_symbols_tool(directory)
        
        scan_data.update({
            "index_summary": index_json[:2000] + "..." if len(index_json) > 2000 else index_json,
            "file_tree": file_tree,
            "symbols_summary": symbols[:2000] + "..." if len(symbols) > 2000 else symbols
        })
    else:
        click.secho("\n[Phase 1] Skipping deep codebase scan (Agent Docs found).", fg="yellow")

    # --- Phase 2: Agent Insight Generation (Server-Side) ---
    click.secho("[Phase 2] Analyzing codebase insights (Server-Side)...", fg="yellow")
    
    try:
        results = asyncio.run(client.analyze_project(scan_data))
        insights = results.get("insights", {})
        click.echo(f"Insights generated. Architecture detected: {insights.get('architecture', 'Unknown')}")
    except Exception as e:
        click.secho(f"❌ Analysis failed: {e}", fg="red")
        return

    # --- Phase 2.5: Workspace & Project Setup ---
    # Used same helper as optimization path
    try:
        asyncio.run(_ensure_project_setup(client, directory))
    except Exception as e:
         click.secho(f"! Project setup failed: {e}", fg="yellow")
         # Continue locally? Or abort? 
         # We continue to allow local artifact generation even if sync setup invalid.

    # --- Phase 3: Clarification Interview ---
    click.secho("\n[Phase 3] Clarification Interview", fg="magenta", bold=True)
    click.echo("The agent has some clarifying questions based on the scan:")
    
    user_feedback = _conduct_interview(insights.get("clarifications", []))

    # --- Phase 4: Artifact Finalization (Server-Side) ---
    click.secho("\n[Phase 4] Finalizing Artifacts...", fg="yellow")
    
    try:
        feedback_str = json.dumps(user_feedback)
        final_results = asyncio.run(client.analyze_project(scan_data, user_feedback=feedback_str))
        final_specs = final_results.get("artifacts", {})
        
        if not final_specs:
             click.secho("⚠️ Server returned no artifacts. Using fallbacks.", fg="yellow")
             final_specs = {}

        _write_project_artifacts(directory, final_specs)
        update_agents_md(directory, insights.get("summary", "Project initialized."))
        
        click.secho("\n✅ Onboarding complete!", fg="green", bold=True)
        click.echo("Review SPECIFICATION.md and governance.yaml.")
        
        # Auto-Sync after successful onboarding
        if click.confirm("Sync generated artifacts to remote?", default=True):
             asyncio.run(sync_project_context())
        
    except Exception as e:
        click.secho(f"❌ Artifact generation failed: {e}", fg="red")

def _conduct_interview(questions: list) -> Dict[str, str]:
    """Interactive CLI interview."""
    responses = {}
    for i, q in enumerate(questions, 1):
        click.echo(f"\nQ{i}: {q}")
        response = click.prompt("Answer", type=str)
        responses[q] = response
    return responses

def _write_project_artifacts(directory: str, artifacts: Dict):
    """Writes the final artifacts to disk."""
    spec_path = os.path.join(directory, "SPECIFICATION.md")
    gov_path = os.path.join(directory, "governance.yaml")
    
    with open(spec_path, "w") as f:
        f.write(artifacts.get("specification_md", ""))
    click.echo(f"Created {spec_path}")
    
    with open(gov_path, "w") as f:
        f.write(artifacts.get("governance_yaml", ""))
    click.echo(f"Created {gov_path}")

def update_agents_md(directory: str, summary: str):
    """Updates AGENTS.md."""
    agents_path = os.path.join(directory, "AGENTS.md")
    content = f"# Agent Guidelines\n\n## Summary\n{summary}\n\n## Rules\n1. Follow specs.\n2. Adhere to governance.yaml."
    with open(agents_path, "w") as f:
        f.write(content)
    click.echo(f"Updated {agents_path}")
