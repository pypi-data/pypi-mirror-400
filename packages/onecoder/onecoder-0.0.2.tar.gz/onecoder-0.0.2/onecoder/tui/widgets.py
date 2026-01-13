"""Custom widgets for OneCoder TUI."""

from textual.widgets import Static, LoadingIndicator
from rich.panel import Panel
from rich.markdown import Markdown
from typing import Optional


class ChatMessage(Static):
    """Widget for displaying chat messages with markdown support."""

    def __init__(self, message: str, role: str = "user", **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.role = role

    def render(self):
        if self.role == "user":
            panel = Panel(
                self.message, title="You", border_style="bold blue", padding=(0, 1)
            )
            return panel
        else:
            panel = Panel(
                Markdown(self.message),
                title="OneCoder",
                border_style="bold green",
                padding=(0, 1),
            )
            return panel


class ToolCallStatus(Static):
    """Widget for displaying tool call status."""

    def __init__(self, tool_name: str, status: str = "running", **kwargs):
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.status = status

    def render(self):
        if self.status == "running":
            content = f"Running {self.tool_name}..."
            border_style = "bold yellow"
        elif self.status == "success":
            content = f"✓ {self.tool_name} finished"
            border_style = "bold green"
        else:
            content = f"✗ {self.tool_name} failed"
            border_style = "bold red"

        panel = Panel(
            content, title="Tool Call", border_style=border_style, padding=(0, 1)
        )
        return panel


class ErrorMessage(Static):
    """Widget for displaying error messages."""

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def render(self):
        panel = Panel(
            self.message,
            title="Error",
            border_style="bold red",
            style="red",
            padding=(0, 1),
        )
        return panel


class WelcomeMessage(Static):
    """Widget for displaying welcome message on startup."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render(self):
        from rich.text import Text
        from rich.console import Group

        title = Text("OneCoder TUI", style="bold blue")
        subtitle = Text(
            "Modern terminal interface for AI-powered coding assistance", style="dim"
        )

        panel = Panel(Group(title, "", subtitle), border_style="blue", padding=(1, 2))
        return panel
