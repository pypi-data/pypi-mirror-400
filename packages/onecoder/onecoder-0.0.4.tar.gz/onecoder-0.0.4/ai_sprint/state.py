import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from jsonschema import validate, ValidationError
from .sync_engine import sync_artifacts, sync_tasks_from_todo

SCHEMA_PATH = Path(__file__).parent.parent.parent / "schemas" / "sprint.schema.json"

class SprintStateManager:
    """Manage sprint.json state file."""
    def __init__(self, sprint_dir: Path):
        self.sprint_dir = sprint_dir
        self.state_file = sprint_dir / "sprint.json"
        self._schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        if not SCHEMA_PATH.exists(): return {}
        with open(SCHEMA_PATH) as f: return json.load(f)

    def load(self) -> Dict[str, Any]:
        if not self.state_file.exists(): return {}
        with open(self.state_file) as f: data = json.load(f)
        if self._schema:
            try: validate(instance=data, schema=self._schema)
            except ValidationError as e: raise ValueError(f"Invalid sprint.json: {e.message}")
        return data

    def save(self, state: Dict[str, Any]) -> None:
        if self._schema:
            try: validate(instance=state, schema=self._schema)
            except ValidationError as e: raise ValueError(f"Invalid sprint.json: {e.message}")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f: json.dump(state, f, indent=2)

    def update(self, updates: Dict[str, Any]) -> None:
        state = self.load() or updates
        if state != updates: state = self._deep_merge(state, updates)
        self._update_metadata(state)
        self.save(state)

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else: result[key] = value
        return result

    def _update_metadata(self, state: Dict[str, Any]) -> None:
        state.setdefault("metadata", {})["updatedAt"] = datetime.now().isoformat()

    def sync_from_files(self) -> None:
        state = self.load()
        if not state: return
        state = sync_artifacts(self.sprint_dir, state)
        state = sync_tasks_from_todo(self.sprint_dir, state)
        self._update_metadata(state)
        self.save(state)

    def create_initial_state(self, name: str, title: str = None, component: str = None) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        return {
            "$schema": "https://onecoder.dev/schemas/sprint.json", "version": "1.0.0",
            "sprintId": name, "name": name, "title": title or name,
            "status": {"phase": "init", "state": "active", "message": None},
            "metadata": {"createdAt": now, "updatedAt": now, "createdBy": None, "parentComponent": component, "gitBranch": None, "labels": []},
            "goals": {"primary": None, "secondary": []}, "tasks": [], "artifacts": {},
            "git": {"branch": None, "lastCommit": None, "hasUncommittedChanges": False},
            "hooks": {"onInit": [], "onTaskStart": [], "onTaskComplete": [], "onSprintClose": []},
        }

    def get_active_task(self) -> Optional[Dict[str, Any]]:
        state = self.load()
        for task in state.get("tasks", []):
            if task.get("status") in ["in_progress", "started", "in-progress"]: return task
        return None

    def mark_done(self, task_id_or_title: str) -> bool:
        return self._update_todo_status(task_id_or_title, "[x]")

    def start_task(self, task_id_or_title: str) -> bool:
        return self._update_todo_status(task_id_or_title, "[/]")

    def _update_todo_status(self, task_id_or_title: str, marker: str) -> bool:
        todo_file = self.sprint_dir / "TODO.md"
        if not todo_file.exists(): return False
        content = todo_file.read_text()
        target = task_id_or_title
        if re.match(r"task-\d+", task_id_or_title):
            for t in self.load().get("tasks", []):
                if t.get("id") == task_id_or_title: target = t.get("title"); break
        pattern = rf"\[(\s|x|/)\]\s*.*{re.escape(target)}"
        if re.search(pattern, content, re.I):
            new_content = re.sub(rf"\[(\s|x|/)\](\s*.*{re.escape(target)})", rf"{marker}\2", content, flags=re.I)
            todo_file.write_text(new_content)
            self.sync_from_files()
            return True
        return False

    def get_task_id_by_title(self, title: str) -> Optional[str]:
        state = self.load()
        if not state.get("tasks"): self.sync_from_files(); state = self.load()
        for t in state.get("tasks", []):
            if t.get("title").strip().lower() == title.strip().lower(): return t.get("id")
        return None

    def get_component(self) -> Optional[str]:
        return self.load().get("metadata", {}).get("parentComponent")

    def set_component(self, component: str) -> None:
        state = self.load()
        if not state: return
        state.setdefault("metadata", {})["parentComponent"] = component
        self._update_metadata(state)
        self.save(state)
