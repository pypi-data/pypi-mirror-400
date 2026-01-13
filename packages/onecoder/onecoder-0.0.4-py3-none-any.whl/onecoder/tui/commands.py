from typing import Dict, Any, Callable, Awaitable
from rich.panel import Panel
from rich.markdown import Markdown
from ..evaluation import TTUEvaluator

class CommandRegistry:
    def __init__(self, app):
        self.app = app
        self.commands: Dict[str, Callable] = {}
        self._register_default_commands()

    def _register_default_commands(self):
        self.register("help", self.cmd_help, "Show available commands")
        self.register("clear", self.cmd_clear, "Clear the chat log")
        self.register("status", self.cmd_status, "Show platform-wide sprint status")
        self.register("ttu", self.cmd_ttu, "Evaluate Task Technical Understanding (TTU) for current context")
        self.register("delegate", self.cmd_delegate, "Delegate a task to a local isolated agent. Usage: /delegate <task description>")

    def register(self, name: str, handler: Callable, description: str):
        self.commands[name] = {"handler": handler, "description": description}

    async def handle(self, command_str: str) -> bool:
        """
        Handles a command string (e.g., "/help").
        Returns True if handled, False if command not found.
        """
        parts = command_str.lstrip("/").split()
        if not parts:
            return False

        cmd_name = parts[0].lower()
        args = parts[1:]

        if cmd_name in self.commands:
            try:
                await self.commands[cmd_name]["handler"](args)
            except Exception as e:
                await self.app._write_error(f"Command error: {str(e)}")
            return True
        else:
            await self.app._write_error(f"Unknown command: /{cmd_name}")
            return True

    async def cmd_help(self, args):
        lines = ["[bold]Available Commands:[/bold]"]
        for name, data in self.commands.items():
            lines.append(f"• [cyan]/{name}[/cyan]: {data['description']}")

        panel = Panel("\n".join(lines), title="Help", border_style="blue")
        self.app.chat_log.write(panel)

    async def cmd_clear(self, args):
        self.app.chat_log.clear()

    async def cmd_status(self, args):
        # We can implement a simple status check here, possibly calling the same logic as CLI status
        # For now, let's mock or use basic discovery
        from pathlib import Path
        import json

        root_path = Path(".").resolve() # Or configure root
        sprint_dirs = []
        for p in root_path.rglob(".sprint"):
             if "node_modules" in p.parts or ".git" in p.parts:
                continue
             sprint_dirs.append(p)

        if not sprint_dirs:
            self.app.chat_log.write(Panel("No active sprints found.", title="Status", border_style="yellow"))
            return

        status_lines = []
        for sd in sprint_dirs:
            component = sd.parent.name
            subdirs = sorted([d for d in sd.iterdir() if d.is_dir()])
            if subdirs:
                active = subdirs[-1]
                sprint_json = active / "sprint.json"
                state_str = "Unknown"
                if sprint_json.exists():
                    try:
                        with open(sprint_json) as f:
                            data = json.load(f)
                            state_str = data.get("status", {}).get("state", "unknown")
                    except:
                        pass
                status_lines.append(f"• [bold]{component}[/bold] -> {active.name}: [green]{state_str}[/green]")

        self.app.chat_log.write(Panel("\n".join(status_lines), title="Platform Status", border_style="blue"))

    async def cmd_ttu(self, args):
        evaluator = TTUEvaluator()
        result = evaluator.evaluate()

        color = "green" if result.passed else "red"
        icon = "✓" if result.passed else "✗"

        lines = [
            f"**Score:** {result.score:.2f} / 1.0",
            "",
            "**Context Found:**",
            *[f"- {c}" for c in result.context_found],
        ]

        if result.failure_modes:
            lines.append("")
            lines.append("**Potential Failure Modes:**")
            lines.extend([f"- [red]{m}[/red]" for m in result.failure_modes])

        if result.missing_context:
            lines.append("")
            lines.append("**Missing Context:**")
            lines.extend([f"- {c}" for c in result.missing_context])

        if result.recommendations:
            lines.append("")
            lines.append("**Recommendations:**")
            lines.extend([f"- {r}" for r in result.recommendations])

        panel = Panel(
            Markdown("\n".join(lines)),
            title=f"{icon} TTU Evaluation",
            border_style=f"bold {color}"
        )
        self.app.chat_log.write(panel)
    async def cmd_delegate(self, args):
        if not args:
            await self.app._write_error("Usage: /delegate <task description>")
            return

        task_desc = " ".join(args)
        self.app.chat_log.write(Panel(f"Delegating task: [bold]{task_desc}[/bold]", title="Delegation", border_style="yellow"))

        try:
            from ..services.delegation_service import DelegationService
            service = DelegationService()
            session = service.create_session(task_id=f"delegate-{task_desc[:10]}", command=task_desc)
            
            # Start the session (async)
            connection_info = await service.start_session(session)
            
            self.app.chat_log.write(Panel(
                f"Delegated successfully!\n\n"
                f"**Backend:** local-tui\n"
                f"**Worktree:** {session.worktree_path}\n"
                f"**To Attach:** [cyan]{connection_info}[/cyan]",
                title="Success", border_style="bold green"
            ))
        except Exception as e:
            await self.app._write_error(f"Delegation failed: {str(e)}")
