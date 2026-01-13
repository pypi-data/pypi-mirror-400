import click
from pathlib import Path
import sys

@click.command()
@click.option("--n", default=50, help="Number of lines to show (default 50).")
@click.option("--follow", "-f", is_flag=True, help="Follow log output that updates.")
def logs(n, follow):
    """View recent OneCoder logs."""
    log_file = Path.home() / ".onecoder" / "logs" / "onecoder.log"
    
    if not log_file.exists():
        click.echo(f"No log file found at {log_file}")
        return

    click.secho(f"Reading logs from {log_file}...", dim=True)
    
    try:
        from collections import deque
        with open(log_file, 'r') as f:
            if follow:
                # Print last n lines first
                lines = deque(f, maxlen=n)
                for line in lines:
                    sys.stdout.write(line)
                
                # Follow loop
                import time
                while True:
                    line = f.readline()
                    if line:
                        sys.stdout.write(line)
                    else:
                        time.sleep(0.1)
            else:
                # Just print last n lines
                 lines = deque(f, maxlen=n)
                 for line in lines:
                     sys.stdout.write(line)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        click.report_exception(e)  # Keep traceback if needed
        click.secho(f"Error reading logs: {e}", fg="red")
