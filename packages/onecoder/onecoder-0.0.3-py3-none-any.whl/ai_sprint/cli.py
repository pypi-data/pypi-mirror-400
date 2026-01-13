import click
import sys
from .commands import common, sprint, task, governance, utility

@click.group()
@click.version_option(version="0.1.4")
def main():
    """ai-sprint: Standardize your development sprints."""
    pass

def run():
    """Main entry point with telemetry wrapper."""
    try:
        main()
    except Exception as e:
        if isinstance(e, (click.exceptions.Exit, click.exceptions.Abort, click.exceptions.ClickException)):
            raise e
        from .telemetry import FailureModeCapture
        capture = FailureModeCapture(common.PROJECT_ROOT)
        capture.capture(e, context={"command_args": sys.argv[1:]})
        raise e

# Register commands
main.add_command(sprint.init)
main.add_command(sprint.update)
main.add_command(sprint.status)
main.add_command(task.start)
main.add_command(task.finish)
main.add_command(governance.commit)
main.add_command(governance.verify)
main.add_command(governance.preflight)
main.add_command(governance.close)
main.add_command(utility.trace)
main.add_command(utility.audit)
main.add_command(utility.backlog)
main.add_command(utility.check_submodules, name="check-submodules")
main.add_command(utility.install_hooks, name="install-hooks")

if __name__ == "__main__":
    main()
