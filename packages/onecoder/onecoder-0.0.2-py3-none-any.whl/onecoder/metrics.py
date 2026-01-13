import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

def find_repo_root() -> Path:
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()

class TTUMetrics:
    _instance = None
    _first_tool_called = False

    def __init__(self):
        self.repo_root = find_repo_root()
        self.sprint_dir = self.repo_root / ".sprint"

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def track_first_tool_call(self):
        """Called by tools or agent to mark the first actual action."""
        if self._first_tool_called:
            return
        
        self._first_tool_called = True
        self._record_ttu()

    def _record_ttu(self):
        """Finds the active task and records TTU if not already set."""
        if not self.sprint_dir.exists():
            return

        # 1. Find the active sprint
        active_sprint_id = os.environ.get("ACTIVE_SPRINT_ID")
        if not active_sprint_id:
             # Try to find an active sprint directory
             sprint_dirs = [d for d in self.sprint_dir.iterdir() if d.is_dir() and d.name[0].isdigit()]
             if not sprint_dirs:
                 return
             # Heuristic: the one with the highest number is likely active
             active_sprint_dir = sorted(sprint_dirs)[-1]
        else:
            active_sprint_dir = self.sprint_dir / active_sprint_id

        if not active_sprint_dir.exists():
            return

        sprint_json_path = active_sprint_dir / "sprint.json"
        if not sprint_json_path.exists():
            return

        try:
            with open(sprint_json_path, 'r') as f:
                state = json.load(f)

            # 2. Find in-progress task
            tasks = state.get("tasks", [])
            active_task = None
            for task in tasks:
                if task.get("status") == "in-progress":
                    active_task = task
                    break
            
            if not active_task:
                 # Fallback: check if any tasks were started but not completed
                for task in tasks:
                    if task.get("startedAt") and not task.get("completedAt"):
                        active_task = task
                        break

            if not active_task:
                return

            # 3. Check if TTU already recorded
            if active_task.get("ttuSeconds") is not None:
                return

            # 4. Calculate TTU
            started_at_str = active_task.get("startedAt")
            if not started_at_str:
                return

            # Handle ISO format (might have 'Z' or offset)
            try:
                started_at = datetime.fromisoformat(started_at_str.replace('Z', '+00:00'))
            except ValueError:
                # Fallback for older formats or varying ISO implementations
                return

            now = datetime.now().astimezone() # Ensure timezone awareness if started_at has it
            
            # If started_at is naive, make now naive too
            if started_at.tzinfo is None:
                now = datetime.now()
            else:
                # started_at has tz, ensuring now has the same or comparable tz
                pass

            diff = now - started_at
            ttu_seconds = int(diff.total_seconds())

            # Don't record negative TTU (clock skew or start after first call?)
            if ttu_seconds < 0:
                ttu_seconds = 0

            # 5. Update state and save
            active_task["ttuSeconds"] = ttu_seconds

            with open(sprint_json_path, 'w') as f:
                json.dump(state, f, indent=2)

            # Passive logging
            log_dir = active_sprint_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            with open(log_dir / "metrics.log", "a") as log:
                log.write(f"[{datetime.now().isoformat()}] TTU: {ttu_seconds}s for task {active_task.get('id')}\n")

        except Exception:
            # Passive tracking should never crash the main flow
            pass
