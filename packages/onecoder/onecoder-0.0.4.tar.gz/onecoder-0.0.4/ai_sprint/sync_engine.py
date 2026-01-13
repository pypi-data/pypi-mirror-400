import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

def sync_artifacts(sprint_dir: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    """Sync artifact files from sprint directory."""
    artifacts = state.setdefault("artifacts", {})
    for artifact in ["README.md", "RETRO.md", "WALKTHROUGH.md", "FEATURES.md"]:
        if (sprint_dir / artifact).exists():
            key = artifact.lower().replace(".md", "")
            artifacts[key] = artifact

    media_dir = sprint_dir / "media"
    if media_dir.exists():
        media_items = []
        for f in media_dir.glob("*"):
            if f.is_file():
                suffix = f.suffix.lower()
                media_type = "screenshot" if suffix in [".png", ".jpg", ".jpeg", ".svg", ".gif"] else ("log" if suffix in [".log", ".txt"] else "document")
                media_items.append({"type": media_type, "path": f.name, "description": ""})
        artifacts["media"] = media_items
    state["artifacts"] = artifacts
    return sync_retro_content(sprint_dir, state)

def sync_retro_content(sprint_dir: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    """Parse RETRO.md and update sprint.json retro object."""
    retro_file = sprint_dir / "RETRO.md"
    if not retro_file.exists(): return state
    content = retro_file.read_text()
    retro_data = {"summary": "", "actionItems": []}
    
    summary_match = re.search(r"^##\s+(?:Executive\s+)?Summary\s*$(.*?)(?=^##|\Z)", content, re.MULTILINE | re.DOTALL)
    if summary_match: retro_data["summary"] = summary_match.group(1).strip()

    action_items_match = re.search(r"^##\s+Action Items\s*$(.*?)(?=^##|\Z)", content, re.MULTILINE | re.DOTALL)
    if action_items_match:
        items = re.findall(r"-\s*\[(\s|x)\]\s*(.+)", action_items_match.group(1))
        retro_data["actionItems"] = [it[1].strip() for it in items]

    if retro_data["summary"] or retro_data["actionItems"]: state["retro"] = retro_data
    return state

def sync_tasks_from_todo(sprint_dir: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    """Sync tasks from TODO.md."""
    todo_file = sprint_dir / "TODO.md"
    if not todo_file.exists(): return state
    content = todo_file.read_text()
    tasks = []
    task_counter = 1
    existing_tasks = {t["title"]: t for t in state.get("tasks", [])}

    for line in content.split("\n"):
        match = re.match(r"-\s*\[(x|/|\s)\]\s*(.+)", line)
        if match:
            marker, task_title = match.group(1), match.group(2).strip()
            task_id = f"task-{task_counter:03d}"
            task_counter += 1
            existing = existing_tasks.get(task_title, {})
            status = "done" if marker == "x" else ("in-progress" if marker == "/" else "todo")
            
            started_at = existing.get("startedAt")
            if marker == "/" and not started_at: started_at = datetime.now().isoformat()
            
            completed_at = existing.get("completedAt")
            if marker == "x" and not completed_at: completed_at = datetime.now().isoformat()

            tasks.append({
                "id": task_id, "title": task_title, "status": status,
                "type": existing.get("type", "implementation"),
                "priority": existing.get("priority", "medium"),
                "startedAt": started_at, "completedAt": completed_at,
            })
    state["tasks"] = tasks
    return state
