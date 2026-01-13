import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

class ProjectKnowledge:
    """
    Manages L2 (Project Context) by aggregating durable awareness files.
    """
    def __init__(self, directory: str = "."):
        self.directory = self._find_repo_root(Path(directory).absolute())
        self.agents_md = self.directory / "AGENTS.md"
        self.antigravity_md = self.directory / "ANTIGRAVITY.md"

    def _find_repo_root(self, start_path: Path) -> Path:
        """Traverses upwards to find the repository root."""
        curr = start_path
        while curr != curr.parent:
            if (curr / ".sprint").exists() or (curr / ".git").exists():
                return curr
            curr = curr.parent
        return start_path # Fallback to start_path

    def get_durable_context(self) -> Dict[str, str]:
        """Reads and returns the content of durable awareness files."""
        context = {}
        if self.agents_md.exists():
            context["agents_guidelines"] = self.agents_md.read_text()
        if self.antigravity_md.exists():
            context["antigravity_awareness"] = self.antigravity_md.read_text()
        return context

    def get_l1_context(self) -> Optional[Dict[str, Any]]:
        """
        Attempts to fetch L1 context from ai_sprint SDK or sprint-cli fallback.
        """
        sprint_id = os.environ.get("ACTIVE_SPRINT_ID")
        if not sprint_id:
            return None

        # 1. Try SDK-first approach
        try:
            from ai_sprint.state import SprintStateManager
            sprint_dir = self.directory / ".sprint" / sprint_id
            if sprint_dir.exists():
                state_manager = SprintStateManager(sprint_dir)
                return state_manager.get_context_summary()
        except (ImportError, Exception):
            pass

        # 2. Fallback to CLI
        try:
            # We assume 'sprint' is available in the environment or path
            # Using ~/.local/bin/uv run sprint as a safer fallback based on ANTIGRAVITY.md quirks
            uv_path = Path.home() / ".local" / "bin" / "uv"
            if uv_path.exists():
                cmd = [str(uv_path), "run", "sprint", "context", "--json"]
            else:
                cmd = ["sprint", "context", "--json"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return None

    def aggregate_knowledge(self) -> Dict[str, Any]:
        """
        Aggregates L2 durable context and L1 ephemeral context (if available).
        """
        knowledge = {
            "project_root": str(self.directory),
            "durable_context": self.get_durable_context(),
            "ephemeral_context": self.get_l1_context()
        }
        return knowledge

    def get_rag_ready_output(self) -> str:
        """Returns a string representation suitable for agent RAG ingestion."""
        data = self.aggregate_knowledge()
        output = [f"# Project Knowledge: {self.directory.name}\n"]
        
        if data["durable_context"]:
            output.append("## L2: Project Context (Durable)")
            for key, content in data["durable_context"].items():
                output.append(f"### {key.replace('_', ' ').title()}")
                output.append(content)
                output.append("")

        if data["ephemeral_context"] and "error" not in data["ephemeral_context"]:
            output.append("## L1: Task Context (Ephemeral)")
            ctx = data["ephemeral_context"]
            output.append(f"**Sprint**: {ctx.get('sprint_id', 'Unknown')}")
            output.append(f"**Goal**: {ctx.get('goal', 'N/A')}")
            if ctx.get('active_task'):
                t = ctx['active_task']
                output.append(f"**Active Task**: [{t.get('id')}] {t.get('title')}")
            
            if ctx.get('todos'):
                output.append("\n**Active TODOs**:")
                for todo in ctx['todos']:
                    output.append(f"  {todo}")
        
        return "\n".join(output)
