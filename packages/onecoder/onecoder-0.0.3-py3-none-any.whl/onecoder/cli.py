import click
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
# env_path = Path(__file__).resolve().parent.parent / ".env"
# load_dotenv(env_path)

from .commands.auth import login, logout, whoami
from .commands.server import serve, web, tui
from .commands.issue import issue
from .commands.logs import logs
from .commands.project import (
    init, status, knowledge, distill, sync, alignment, sprint_suggest
)
from .commands.delegate import (
    delegate, delegate_list, delegate_status, delegate_validate, delegate_finish, jules_sessions
)
from .commands.doctor import doctor
from .commands.ci import ci
from .review import CodeReviewer

from .logger import configure_logging

@click.group()
@click.version_option(version="0.0.3", prog_name="onecoder")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def cli(verbose):
    """OneCoder: Unified Agent Architecture."""
    configure_logging(verbose=verbose)

def main():
    """Main entry point with telemetry wrapper."""
    try:
        cli()
    except Exception as e:
        # Don't capture Click-internal exit exceptions as failures
        if isinstance(e, (click.exceptions.Exit, click.exceptions.Abort, click.exceptions.ClickException)):
            raise e
            
        try:    
            from ai_sprint.telemetry import FailureModeCapture
            capture = FailureModeCapture()
            capture.capture(e, context={"command_args": sys.argv[1:]})
        except ImportError:
            # Telemetry not available, just re-raise
            pass
        raise e

# Register Commands
def is_internal_features_enabled():
    """Check if internal features should be enabled."""
    return os.getenv("ONECODER_INTERNAL", "false").lower() == "true" or \
           os.getenv("ONE_CODER_DEV", "false").lower() == "true"

# Register Commands
cli.add_command(login)
cli.add_command(logout)
cli.add_command(whoami)

cli.add_command(serve)
cli.add_command(web)
cli.add_command(tui)

cli.add_command(issue)
cli.add_command(logs)
cli.add_command(doctor)

cli.add_command(init)
cli.add_command(status)
cli.add_command(knowledge)
cli.add_command(distill)
cli.add_command(sync)
cli.add_command(alignment)
cli.add_command(ci)

if is_internal_features_enabled():
    cli.add_command(delegate)
    cli.add_command(delegate_list)
    cli.add_command(delegate_status)
    cli.add_command(delegate_validate)
    cli.add_command(delegate_finish)
    cli.add_command(jules_sessions)

@cli.command()
@click.argument("pr_id", required=False)
@click.option("--local", is_flag=True, help="Review local changes against main")
def review(pr_id, local):
    """Run a policy-grounded AI review on a PR or local code."""
    reviewer = CodeReviewer()
    reviewer.review(pr_id=pr_id, local=local)

# Sprint Group Integration
# Sprint Group Integration
try:
    from ai_sprint.cli import main as sprint_main
    # Attempt to add the command to the existing group
    if sprint_suggest not in sprint_main.commands.values():
         sprint_main.add_command(sprint_suggest)
    cli.add_command(sprint_main, name="sprint")
except ImportError:
    @cli.group(name="sprint")
    def sprint_group():
        """Sprint management commands."""
        pass
    sprint_group.add_command(sprint_suggest)
    cli.add_command(sprint_group)

if __name__ == "__main__":
    cli()
