"""OneCoder Textual TUI Application."""

import asyncio
import json
import httpx
import os
from typing import Optional, AsyncGenerator

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog
from textual.containers import Vertical, Container
from textual import events
from textual.binding import Binding

from rich.panel import Panel
from rich.markdown import Markdown

from ..ipc_auth import get_token_from_ipc
from .widgets import ChatMessage, ToolCallStatus, ErrorMessage, WelcomeMessage
from .commands import CommandRegistry


class OneCoderApp(App):
    """Modern Textual TUI for OneCoder agent system."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear_log", "Clear Log", show=True),
        Binding("ctrl+s", "toggle_theme", "Toggle Theme", show=True),
        Binding("ctrl+d", "toggle_dark", "Dark Mode"),
    ]

    def __init__(self, api_url: Optional[str] = None):
        super().__init__()
        if api_url:
            self.api_url = api_url
        else:
            self.api_url = os.getenv("ONECODER_API_URL", "http://127.0.0.1:8000")
        self.session_id = "tui-session"
        self.user_id = "local-user"
        self.token = None
        self.is_processing = False
        self.command_registry = CommandRegistry(self)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            RichLog(id="chat-log", markup=True, wrap=True, highlight=True),
            Input(
                placeholder="Type your message... (or 'exit' to quit)", id="user-input"
            ),
            id="main-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.chat_log = self.query_one("#chat-log", RichLog)
        self.input_widget = self.query_one("#user-input", Input)

        await self._initialize_session()

        if self.token:
            self.chat_log.write(WelcomeMessage())
            self.chat_log.write("\n")
            self.input_widget.focus()

    async def _initialize_session(self) -> bool:
        """Initialize TUI and fetch authentication token."""
        self.chat_log.write(
            Panel(
                "[bold blue]OneCoder TUI[/bold blue]",
                title="Initializing secure session...",
                border_style="dim",
            )
        )

        self.token = await get_token_from_ipc()

        if not self.token:
            self.chat_log.write(
                ErrorMessage(
                    "Could not fetch auth token from IPC.\n"
                    "Make sure OneCoder server is running: onecoder serve"
                )
            )
            return False

        self.chat_log.write(
            Panel(
                "[bold green]✓[/bold green] Session initialized successfully!",
                title="Success",
                border_style="bold green",
            )
        )

        return True

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission."""
        if self.is_processing:
            return

        message = event.value.strip()

        if not message:
            return

        # Handle slash commands
        if message.startswith("/"):
            self.input_widget.clear()
            await self.command_registry.handle(message)
            if message.lower() in ["/quit", "/exit"]:
                self.exit()
            return

        if message.lower() in ["exit", "quit"]:
            self.exit()
            return

        self.input_widget.disabled = True
        self.is_processing = True

        await self._process_message(message)

        self.input_widget.disabled = False
        self.is_processing = False
        self.input_widget.focus()
        self.input_widget.clear()

    async def _process_message(self, message: str):
        """Process user message and stream agent response."""
        await self._write_user_message(message)

        current_response = ""
        message_content = []

        async with httpx.AsyncClient(timeout=None) as client:
            params = {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "message": message,
                "token": self.token,
            }

            try:
                async with client.stream(
                    "GET", f"{self.api_url}/stream", params=params
                ) as response:
                    if response.status_code != 200:
                        await self._write_error(f"Error: {response.status_code}")
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])

                                if "text" in data:
                                    current_response += data["text"]
                                elif data.get("type") == "Error":
                                    await self._write_error(
                                        data.get("message", "Unknown error")
                                    )
                                elif "tool_call" in data:
                                    tool_name = data["tool_call"].get("name", "unknown")
                                    await self._show_tool_call(
                                        tool_name, {}, status="running"
                                    )
                                elif "tool_result" in data:
                                    tool_name = data.get("tool_name", "unknown")
                                    await self._show_tool_call(
                                        tool_name, {}, status="success"
                                    )

                            except json.JSONDecodeError:
                                pass

                if current_response:
                    await self._write_agent_message(current_response)

            except httpx.ConnectError:
                await self._write_error(
                    "Could not connect to OneCoder API.\n"
                    "Is the server running?\n"
                    "Run 'onecoder serve' in another terminal."
                )
            except Exception as e:
                await self._write_error(f"Stream Error: {e}")

    async def _write_user_message(self, message: str):
        """Write user message to chat log."""
        panel = Panel(message, title="You", border_style="bold green", padding=(0, 1))
        self.chat_log.write(panel)

    async def _write_agent_message(self, text: str):
        """Write agent message to chat log with markdown support."""
        panel = Panel(
            Markdown(text), title="OneCoder", border_style="bold blue", padding=(0, 1)
        )
        self.chat_log.write(panel)

    async def _show_tool_call(
        self, tool_name: str, tool_args: dict, status: str = "running"
    ):
        """Show tool call status in chat log."""
        if status == "running":
            content = f"Running [bold]{tool_name}[/bold]..."
            border_style = "bold yellow"
        elif status == "success":
            content = f"[green]✓[/green] [bold]{tool_name}[/bold] finished."
            border_style = "bold green"
        else:
            content = f"[red]✗[/red] [bold]{tool_name}[/bold] failed."
            border_style = "bold red"

        panel = Panel(
            content, title="Tool Call", border_style=border_style, padding=(0, 1)
        )
        self.chat_log.write(panel)

    async def _write_error(self, message: str):
        """Write error message to chat log."""
        panel = Panel(
            f"Error: {message}",
            title="Error",
            border_style="bold red",
            style="red",
            padding=(0, 1),
        )
        self.chat_log.write(panel)

    async def action_clear_log(self) -> None:
        """Clear chat log."""
        self.chat_log.clear()

    async def action_toggle_theme(self) -> None:
        """Toggle between dark and light theme."""
        if "light" in self.theme:
            self.theme = "textual-dark"
        else:
            self.theme = "textual-light"

        self.chat_log.write(
            Panel(
                f"Theme switched to: {self.theme}",
                title="Theme",
                border_style="dim",
                padding=(0, 1),
            )
        )



def main():
    """Entry point for running OneCoder TUI."""
    app = OneCoderApp()
    app.run()


if __name__ == "__main__":
    main()
