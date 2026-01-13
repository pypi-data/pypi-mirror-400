import click
import asyncio
import threading
import uvicorn
import webbrowser
import signal
import sys
import socket
from ..ipc_auth import IPCAuthServer, get_token_from_ipc

# Global flag for graceful shutdown
shutdown_event = asyncio.Event()

def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False

async def check_servers_running() -> bool:
    """Check if OneCoder servers are running."""
    try:
        token = await get_token_from_ipc()
        return token is not None
    except:
        return False

def run_api_server(port: int = 8000):
    """Runs the FastAPI server."""
    from ..api import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

async def run_servers_async(port: int = 8000):
    """Run both API and IPC servers concurrently."""
    # Start API server in a thread
    api_thread = threading.Thread(target=run_api_server, args=(port,), daemon=True)
    api_thread.start()

    # Give API server time to start
    await asyncio.sleep(1)

    # Start IPC server in main async loop
    ipc_server = IPCAuthServer()
    try:
        await ipc_server.start()
    except asyncio.CancelledError:
        click.echo("Shutting down gracefully...")

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    click.echo("\nReceived shutdown signal. Cleaning up...")
    sys.exit(0)

@click.command()
@click.option("--port", default=8000, help="API server port")
def serve(port):
    """Starts the Agent API and IPC Auth servers."""
    # Check if port is available
    if not check_port_available(port):
        click.echo(f"Error: Port {port} is already in use.")
        click.echo(f"Check for running processes: lsof -i :{port}")
        return

    click.echo(f"Starting OneCoder servers on port {port}...")
    click.echo("Press Ctrl+C to stop.")

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run servers
    try:
        asyncio.run(run_servers_async(port))
    except KeyboardInterrupt:
        click.echo("\nShutting down...")

@click.command()
@click.option("--auto-start", is_flag=True, help="Auto-start servers if not running")
def web(auto_start):
    """Launches the secure Web UI."""

    async def launch():
        # Check if servers are running
        servers_running = await check_servers_running()

        if not servers_running:
            if auto_start:
                click.echo("Servers not running. Starting in background...")
                # Start servers in background thread
                server_thread = threading.Thread(
                    target=lambda: asyncio.run(run_servers_async()), daemon=True
                )
                server_thread.start()
                # Wait for servers to be ready
                await asyncio.sleep(2)

                # Verify they started
                if not await check_servers_running():
                    click.echo("Error: Failed to start servers automatically.")
                    return
            else:
                click.echo("Error: Servers not running.")
                click.echo(
                    "Run 'onecoder serve' in another terminal or use --auto-start"
                )
                return

        # Fetch token
        token = await get_token_from_ipc()
        if not token:
            click.echo("Error: Could not fetch authentication token.")
            return

        # Launch browser
        url = f"http://127.0.0.1:8000/?token={token}"
        click.echo(f"Launching Web UI: {url}")
        webbrowser.open(url)

        if auto_start:
            click.echo("\nServers running in background. Press Ctrl+C to stop.")
            try:
                # Keep running if we auto-started
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                click.echo("\nShutting down...")

    asyncio.run(launch())

@click.command()
@click.option("--auto-start", is_flag=True, help="Auto-start servers if not running")
@click.option("--api-url", help="Override the API URL")
def tui(auto_start, api_url):
    """Launches the modern Textual TUI."""

    async def launch():
        # Check if servers are running
        servers_running = await check_servers_running()

        if not servers_running:
            if auto_start:
                click.echo("Servers not running. Starting in background...")
                # Start servers in background thread
                server_thread = threading.Thread(
                    target=lambda: asyncio.run(run_servers_async()), daemon=True
                )
                server_thread.start()
                # Wait for servers to be ready
                await asyncio.sleep(2)

                # Verify they started
                if not await check_servers_running():
                    click.echo("Error: Failed to start servers automatically.")
                    return
            else:
                click.echo("Error: Servers not running.")
                click.echo(
                    "Run 'onecoder serve' in another terminal or use --auto-start"
                )
                return

        # Launch Textual TUI
        from ..tui.app import OneCoderApp

        app = OneCoderApp(api_url=api_url)
        await app.run_async()

    asyncio.run(launch())
