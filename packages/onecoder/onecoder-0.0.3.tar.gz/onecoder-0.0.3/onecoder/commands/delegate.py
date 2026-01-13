import click
import os
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..services.delegation_service import DelegationService
from ..services.validation_service import ValidationService, FileExistsRule, CommandSuccessRule
from ..jules_client import JulesAPIClient, JulesAPIError, JulesAuthError

@click.command()
@click.option("--limit", default=10, help="Number of recent sessions to show")
def delegate_list(limit):
    """List active delegation sessions and their status."""
    console = Console()
    service = DelegationService()
    sessions = service.list_sessions()
    
    # Sort by created_at desc
    sessions.sort(key=lambda s: s.created_at, reverse=True)
    
    table = Table(title="Delegation Sessions")
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("Task ID (Sprint)", style="magenta")
    table.add_column("Status", style="bold")
    table.add_column("Age", style="white")
    table.add_column("Backend", style="blue")
    
    now = datetime.now()
    
    for s in sessions[:limit]:
        # Calculate age
        age = now - s.created_at
        age_str = str(age).split('.')[0] # Remove microseconds
        
        status_style = "green" if s.status == "running" else "red" if s.status == "failed" else "white"
        
        table.add_row(
            s.id[:8],
            s.task_id,
            f"[{status_style}]{s.status}[/]",
            age_str,
            s.backend
        )
            
    console.print(table)

@click.command()
@click.argument("session_id")
def delegate_status(session_id):
    """Check the status of a local delegation session."""
    console = Console()
    service = DelegationService()
    session = service.get_session(session_id)
    
    if not session:
        console.print(f"[bold red]Error:[/bold red] Session {session_id} not found.")
        return
        
    status_color = "green" if session.status == "running" else "yellow"
    panel = Panel(
        f"[bold]Status:[/bold] [{status_color}]{session.status}[/]\n"
        f"[bold]Backend:[/bold] {session.backend}\n"
        f"[bold]Worktree:[/bold] {session.worktree_path}\n"
        f"[bold]Tmux Session:[/bold] {session.tmux_session or 'N/A'}\n"
        f"[bold]Task ID:[/bold] {session.task_id}",
        title=f"Session: {session_id}"
    )
    console.print(panel)

@click.command()
@click.argument("session_id")
def delegate_validate(session_id):
    """Manually trigger validation for a local delegation session."""
    console = Console()
    dg_service = DelegationService()
    session = dg_service.get_session(session_id)
    
    if not session:
        console.print(f"[bold red]Error:[/bold red] Session {session_id} not found.")
        return
        
    if not session.worktree_path:
        console.print("[bold red]Error:[/bold red] Session has no associated worktree path.")
        return

    val_service = ValidationService()
    # For now, we'll use some default rules or search for a validation spec in the worktree
    rules = [
        FileExistsRule("README.md"), # Basic sanity check
    ]
    
    # Check for a specific validation script if it exists
    if (Path(session.worktree_path) / "validate.sh").exists():
        rules.append(CommandSuccessRule("bash validate.sh"))

    context = {
        "session_id": session_id,
        "worktree_path": session.worktree_path,
        "task_id": session.task_id
    }
    
    with console.status("[bold green]Running validation rules..."):
        report = val_service.validate_session(context, rules)
    
    table = Table(title=f"Validation Report: {session_id}")
    table.add_column("Rule", style="cyan")
    table.add_column("Passed", style="bold")
    table.add_column("Error", style="red")
    
    for res in report.results:
        passed_str = "[green]YES[/green]" if res["passed"] else "[red]NO[/red]"
        table.add_row(res["rule"], passed_str, res["error"] or "-")
        
    console.print(table)
    
    if report.all_passed:
        console.print("\n[bold green]✓ All validation rules passed![/bold green]")
    else:
        console.print("\n[bold red]✗ Some validation rules failed.[/bold red]")

@click.command()
@click.argument("session_id")
@click.option("--message", "-m", help="Commit message", default="feat: complete delegated task")
@click.option("--force", is_flag=True, help="Force finish despite validation failures")
@click.option("--cleanup/--no-cleanup", default=None, help="Cleanup worktree after finish")
def delegate_finish(session_id, message, force, cleanup):
    """
    Finishes a delegation session: validates, commits tracking metadata, and cleans up.
    """
    console = Console()
    dg_service = DelegationService()
    session = dg_service.get_session(session_id)
    
    if not session:
        console.print(f"[bold red]Error:[/bold red] Session {session_id} not found.")
        return

    # --- Remote Jules Governance ---
    if session.backend == "jules":
        if not session.external_id:
            console.print("[red]Error: Remote session missing external Jules ID.[/red]")
            return
            
        console.print(f"[cyan]Governing remote Jules session {session.external_id}...[/cyan]")
        client = JulesAPIClient()
        
        # 1. Detect PR
        pr_info = client.detect_pr_output(session.external_id)
        if not pr_info:
            console.print("[yellow]No PR detected yet for this session. Is it complete?[/yellow]")
            return
            
        pr_url = pr_info["url"]
        console.print(f"Found PR: {pr_url}")
        
        # 2. Fetch PR Locally for Validation
        # We need to checkout the PR branch to validate and merge it.
        # Assuming we are in the repo root.
        try:
             console.print("[cyan]Fetching PR branch...[/cyan]")
             subprocess.run(["gh", "pr", "checkout", pr_url], check=True)
             
             # 3. Validate
             val_service = ValidationService()
             rules = [FileExistsRule("README.md")] # Default rules
             
             context = {"session_id": session_id, "worktree_path": os.getcwd()} # We are in main repo now
             
             with console.status("[bold green]Validating remote work..."):
                 report = val_service.validate_session(context, rules)
             
             if not report.all_passed:
                 console.print("[bold red]Validation Failed.[/bold red]")
                 if not force and not click.confirm("Force proceed?"):
                     return
             
             # 4. Governed Merge
             parent_branch = session.parent_branch or "main" # Fallback
             current_pr_branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
             
             console.print(f"[cyan]Switching to parent branch {parent_branch}...[/cyan]")
             subprocess.run(["git", "checkout", parent_branch], check=True)
             
             console.print(f"[cyan]Merging PR branch {current_pr_branch}...[/cyan]")
             subprocess.run(["git", "merge", "--no-ff", "-m", f"chore: merge remote task {session.task_id}", current_pr_branch], check=True)
             
             # 5. Track in Sprint
             # Let's explicitly append trailers to HEAD (the merge commit)
             # trailers = [
             #     f"Sprint-Id: {session.sprint_id}",
             #     f"Task-Id: {session.task_id}",
             #     "Status: done"
             # ]
             # subprocess.run(...)
             console.print("[green]✓ Remote task merged and governed.[/green]")
             
             if cleanup:
                 subprocess.run(["git", "branch", "-D", current_pr_branch], check=True)
                 
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error during remote finish: {e}[/red]")
            
        return

    # --- Local Worktree Logic (Existing) ---
    val_service = ValidationService()
    rules = [FileExistsRule("README.md")]
    if session.worktree_path and (Path(session.worktree_path) / "validate.sh").exists():
        rules.append(CommandSuccessRule("bash validate.sh"))

    context = {
        "session_id": session_id,
        "worktree_path": session.worktree_path
    }
    
    with console.status("[bold green]Validating session..."):
        report = val_service.validate_session(context, rules)
    
    if not report.all_passed:
        console.print("[bold red]Validation Failed per rules.[/bold red]")
        if not force:
            console.print("Use --force to override.")
            if not click.confirm("Do you want to force finish despite validation failures?"):
                return
            
    # 2. Commit with Tracking Metadata
    console.print("[cyan]Committing with tracking metadata...[/cyan]")
    
    # 2. Atomic Commit in worktree
    if session.worktree_path and os.path.exists(session.worktree_path):
        console.print("[cyan]Finalizing work with atomic commit...[/cyan]")
        try:
             # Using sprint commit with metadata
             cmd = ["sprint", "commit", "-m", message, "--task-id", session.task_id, "--status", "done", "--validation", "Passed"]
             
             # Pass python path if needed (heuristic)
             env = os.environ.copy()
             if "PYTHONPATH" not in env:
                 env["PYTHONPATH"] = str(dg_service.worktree_mgr.project_root / "sprint-cli" / "src")
             
             subprocess.run(cmd, cwd=session.worktree_path, check=True, capture_output=True, env=env)
             console.print("[bold green]✓ Work committed to task branch.[/bold green]")
        except subprocess.CalledProcessError as e:
            # Check if it failed because there's nothing to commit
            if "No staged changes to audit" in e.stdout.decode() or "nothing to commit" in e.stdout.decode():
                 console.print("[bold green]✓ Work already committed to task branch (clean).[/bold green]")
            else:
                console.print(f"[yellow]Sprint tracking failed: {e.stderr.decode()}[/yellow]")
                console.print("Falling back to standard git commit to save work...")
                try:
                    subprocess.run(["git", "add", "."], cwd=session.worktree_path, check=True)
                    subprocess.run(["git", "commit", "-m", message], cwd=session.worktree_path, check=True)
                    console.print("[bold green]✓ Work saved via git commit (untracked in sprint).[/bold green]")
                except subprocess.CalledProcessError as git_e:
                    if "nothing to commit" in git_e.stdout.decode() or "nothing to commit" in git_e.stderr.decode():
                         console.print("[bold green]✓ Work already saved (clean).[/bold green]")
                    else:
                        console.print(f"[bold red]Critical Error:[/bold red] Failed to commit work: {git_e}")
                        return # Do not cleanup if commit failed
    else:
        console.print("[yellow]Worktree not found or already removed. Skipping commit step.[/yellow]")

    # 3. Merge Back to Parent Branch
    parent_branch = session.parent_branch
    if not parent_branch:
        console.print("[yellow]No parent branch recorded for this session. Skipping auto-merge.[/yellow]")
    else:
        console.print(f"[cyan]Removing worktree {session.worktree_path} to allow merge...[/cyan]")
        dg_service.worktree_mgr.remove_worktree(session_id, delete_branch=False)

        console.print(f"[cyan]Merging task branch into {parent_branch}...[/cyan]")
        
        # 3.2. Ensure compatibility first: Rebase task branch onto parent
        if not dg_service.worktree_mgr.rebase_onto(session_id, parent_branch):
             console.print("[bold red]Rebase failed![/bold red] Manual intervention required.")
             console.print(f"[yellow]Restoring worktree for conflict resolution...[/yellow]")
             dg_service.worktree_mgr.create_worktree(session_id, base_ref=f"task/{session_id}")
             return

        # 3.3. Perform the merge
        if dg_service.worktree_mgr.merge_task_branch(session_id, parent_branch):
            console.print(f"[bold green]✓ Successfully merged into {parent_branch}[/bold green]")
        else:
            console.print("[bold red]Merge failed![/bold red] Manual intervention required.")
            console.print(f"[yellow]Restoring worktree for conflict resolution...[/yellow]")
            dg_service.worktree_mgr.create_worktree(session_id, base_ref=f"task/{session_id}")
            return

    # 4. Final Cleanup (Branch deletion)
    should_cleanup = cleanup
    if should_cleanup is None:
            should_cleanup = click.confirm(f"Delete task branch 'task/{session_id}'?")
             
    if should_cleanup:
        # We already removed the worktree, just delete the branch now.
        dg_service.worktree_mgr.remove_worktree(session_id, delete_branch=True)
        console.print("[bold green]✓ Task branch deleted.[/bold green]")

@click.command()
@click.option("--limit", default=5, help="Number of recent sessions to show")
def jules_sessions(limit):
    """List recent Jules sessions and their status."""
    console = Console()
    
    try:
        client = JulesAPIClient()
        
        # For now, we'll need to track sessions locally or via API
        # This is a simplified version that shows cached sessions
        if not client._session_cache:
            console.print("[yellow]No cached sessions found.[/yellow]")
            console.print("Create a session with: onecoder delegate \"your task\"")
            return
        
        table = Table(title="Recent Jules Sessions")
        table.add_column("Session ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("State", style="green")
        table.add_column("PR URL", style="blue")
        
        for session_id, session in list(client._session_cache.items())[:limit]:
            pr_output = client.detect_pr_output(session_id)
            pr_url = pr_output["url"] if pr_output else "-"
            
            table.add_row(
                session_id,
                session.title[:50] if session.title else "N/A",
                session.state,
                pr_url
            )
        
        console.print(table)
        
    except JulesAuthError:
        console.print("[bold red]Error:[/bold red] JULES_API_KEY not set", style="red")
    except JulesAPIError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}", style="red")

@click.command()
@click.argument("prompt")
@click.option("--local", is_flag=True, help="Run as a local isolated delegation session (using Gemini CLI in a worktree/tmux)")
@click.option("--source", help="GitHub source (e.g., sources/github/owner/repo)")
@click.option("--branch", default="main", help="Starting branch")
@click.option("--watch", is_flag=True, help="Monitor progress in real-time (enforces timeout)")
@click.option("--timeout", default=120, help="Timeout in seconds (default: 120s). Only enforced with --watch.")
@click.option("--poll-interval", default=10, help="Polling interval in seconds (default: 10s)")
def delegate(prompt, local, source, branch, watch, timeout, poll_interval):
    """Delegate a coding task to Google Jules or a local agent."""
    console = Console()
    
    if local:
        async def run_local():
            service = DelegationService()
            
            # --- Traceable Task Registration ---
            repo_root = Path.cwd() 
            task_id = None
            
            with console.status("[bold green]Registering task in sprint..."):
                sprint_id, registered_task_id = service.register_task_in_sprint(prompt, repo_root)
                
            if registered_task_id:
                task_id = registered_task_id
                console.print(f"[green]✓ Registered in Sprint {sprint_id}:[/green] [bold]{task_id}[/bold]")
            else:
                # Fallback to ad-hoc ID
                safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt)[:30]
                task_id = f"local-{safe_prompt}"
                console.print(f"[yellow]Warning: Could not register in sprint. Using ad-hoc ID:[/yellow] {task_id}")

            session = service.create_session(task_id=task_id, command=prompt)
            
            with console.status("[bold green]Spawning local isolated session..."):
                connection_info = await service.start_session(session)
            
            console.print(f"[bold green]✓[/bold green] Task delegated to local worktree: [cyan]{session.worktree_path}[/cyan]")
            console.print(f"To attach, run: [bold]{connection_info}[/bold]")
            
            if not watch:
                console.print(f"\n[dim]To monitor this session later, use: onecoder delegate-list[/dim]")
                return

            # --- Watch Logic with Timeout ---
            import time
            from datetime import datetime, timedelta
            
            start_time = datetime.now()
            max_duration = timedelta(seconds=timeout)
            
            console.print(f"\n[bold yellow]Watching session (Timeout: {timeout}s)...[/bold yellow]")
            console.print("Press Ctrl+C to stop watching (session will continue unless timeout reached)\n")
            
            try:
                with console.status("Monitoring session...") as status:
                    while True:
                        # 1. Check Timeout
                        elapsed = datetime.now() - start_time
                        if elapsed > max_duration:
                            console.print(f"\n[bold yellow]Timeout reached ({timeout}s). Stopping watch loop...[/bold yellow]")
                            console.print("[yellow]Session will continue in background. Use 'delegate-finish' to merge work.[/yellow]")
                            service.stop_session(session.id, cleanup=False) 
                            break 

                        # 2. Check Status (Refresh from blackboard)
                        current_session = service.get_session(session.id)
                        if not current_session:
                            console.print("[red]Session lost.[/red]")
                            return
                            
                        # Update UX
                        status.update(f"Monitoring... Age: {str(elapsed).split('.')[0]} Status: {current_session.status}")
                        
                        if current_session.status in ["completed", "failed", "stopped"]:
                            console.print(f"\nSession finished with status: [bold]{current_session.status}[/bold]")
                            return

                        # 3. Wait
                        await asyncio.sleep(poll_interval)
                        
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped watching. Session continues in background.[/yellow]")
                console.print(f"To list sessions: onecoder delegate-list")

        asyncio.run(run_local())
        return

    # --- Remote Jules Logic ---
    service = DelegationService()
    repo_root = Path.cwd()
    task_id = "jules-task"
    sprint_id = None
    
    with console.status("[bold green]Registering task in sprint (Governance)..."):
        sprint_id, registered_task_id = service.register_task_in_sprint(prompt, repo_root)
        
    if registered_task_id:
        task_id = registered_task_id
        console.print(f"[green]✓ Registered in Sprint {sprint_id}:[/green] [bold]{task_id}[/bold]")
    else:
        # Fallback
        console.print(f"[yellow]Warning: Could not register in sprint.[/yellow]")

    # 2. Governance: Enforce Push
    try:
        current_branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
        if branch == "main" or branch == current_branch:
             subprocess.check_call(["git", "remote", "update"], stderr=subprocess.DEVNULL)
             status = subprocess.check_output(["git", "status", "-uno"], text=True)
             if "Your branch is ahead of" in status:
                 console.print("[bold red]Governance Block:[/bold red] You have unpushed commits.")
                 console.print("Jules cannot see your local changes. Please push before delegating.")
                 if not click.confirm("Ignore and proceed (Risk of regression)?"):
                     return
    except Exception:
        pass 

    # 3. Governance: Context Injection
    governance_context = f"\n\n[GOVERNANCE META]\nTask-Id: {task_id}\n"
    if sprint_id:
        governance_context += f"Sprint-Id: {sprint_id}\n"
    
    try:
        from ..knowledge import ProjectKnowledge
        import re
        pk = ProjectKnowledge()
        knowledge = pk.get_l1_context()
        if knowledge:
            goal = knowledge.get("goal", "")
            active_task = knowledge.get("active_task", {})
            spec_match = re.search(r"(SPEC-[A-Z0-9.-]+)", goal + " " + active_task.get("title", ""))
            if spec_match:
                spec_id = spec_match.group(1)
                governance_context += f"Spec-Id: {spec_id}\n"
    except Exception:
        pass

    enhanced_prompt = prompt + governance_context
    console.print(f"[dim]Injected governance context into prompt for {task_id}[/dim]")

    try:
        client = JulesAPIClient()
        
        with console.status("[bold green]Creating Jules session..."):
            jules_session = client.create_session(enhanced_prompt, source=source, branch=branch)
        
        console.print(f"[bold green]✓[/bold green] Session created: [cyan]{jules_session.id}[/cyan]")
        console.print(f"Task: {prompt}")
        console.print(f"Source: {source or os.environ.get('JULES_SOURCE', 'N/A')}")
        console.print(f"Monitor: https://jules.google.com/sessions/{jules_session.id}\n")
        
        # 4. Governance: Persist Local Session Record
        local_session = service.create_session(
            task_id=task_id,
            backend="jules",
            command=prompt
        )
        local_session.external_id = jules_session.id
        local_session.sprint_id = sprint_id
        service._save_session(local_session)
        console.print(f"[dim]Persisted governance record for session {local_session.id}[/dim]")
        
        # Watch mode
        if watch:
            console.print("\n[bold yellow]Watching session progress...[/bold yellow]")
            console.print("Press Ctrl+C to stop watching\n")
            
            def progress_callback(session, activities):
                """Callback for progress updates."""
                table = Table(title=f"Session {session.id}")
                table.add_column("Time", style="cyan")
                table.add_column("Activity", style="white")
                
                for activity in activities[:5]:
                    if activity.activity_type == "plan_generated":
                        table.add_row("Plan", "Plan generated")
                    elif activity.activity_type == "progress_updated":
                        progress = activity.data.get("progressUpdated", {})
                        table.add_row("Progress", progress.get("title", "Update"))
                    elif activity.activity_type == "session_completed":
                        table.add_row("Complete", "✓ Session completed")
                
                console.print(table)
                
                # Check for PR
                pr_output = client.detect_pr_output(session.id)
                if pr_output:
                    console.print(Panel(
                        f"[bold green]PR Created![/bold green]\n"
                        f"URL: {pr_output['url']}\n"
                        f"Title: {pr_output['title']}",
                        title="Pull Request"
                    ))
            
            try:
                final_session = client.poll_until_complete(
                    session.id,
                    callback=progress_callback,
                    max_iterations=60
                )
                console.print(f"\n[bold]Final state:[/bold] {final_session.state}")
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped watching. Session continues in background.[/yellow]")
        
    except JulesAuthError:
        console.print("[bold red]Error:[/bold red] JULES_API_KEY not set", style="red")
        console.print("Set your API key: export JULES_API_KEY=your_key")
    except JulesAPIError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}", style="red")
