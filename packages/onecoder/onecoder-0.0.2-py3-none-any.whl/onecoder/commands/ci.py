import click
import subprocess
import sys
from pathlib import Path

@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def ci(args):
    """Run local CI/CD workflows using OneCoder CI."""
    # Assumption: User runs this from the repo root where `scripts/onecoder-ci.sh` exists.
    # Future improvement: Auto-detect repo root.
    script_path = Path("scripts/onecoder-ci.sh")
    
    if not script_path.exists():
        click.echo("❌ Error: 'scripts/onecoder-ci.sh' not found.")
        click.echo("   Please run this command from the root of the 'platform' repository.")
        sys.exit(1)
        
    # Prepare command: bash scripts/onecoder-ci.sh [args]
    cmd = ["bash", str(script_path)] + list(args)
    
    try:
        # Use subprocess.call or run to stream output directly
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except Exception as e:
        click.echo(f"❌ Error executing OneCoder CI: {str(e)}")
        sys.exit(1)
