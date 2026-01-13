"""
Sprint data collection module.

Scans .sprint/ directories and extracts sprint and task data for syncing to the API.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from ai_sprint.state import SprintStateManager
    HAS_SPRINT_SDK = True
except ImportError:
    HAS_SPRINT_SDK = False

logger = logging.getLogger(__name__)


class SprintCollector:
    """Collects sprint data from .sprint/ directories or via SDK."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.sprint_dir = repo_root / ".sprint"
        self.state_manager = None
        if HAS_SPRINT_SDK:
            try:
                self.state_manager = SprintStateManager(self.sprint_dir)
            except Exception as e:
                logger.warning(f"Could not initialize SprintStateManager: {e}")
    
    def collect_all_sprints(self) -> List[Dict[str, Any]]:
        """Scans .sprint/ and returns list of sprint data."""
        sprints = []
        
        if not self.sprint_dir.exists():
            return sprints
        
        for sprint_path in self.sprint_dir.iterdir():
            if not sprint_path.is_dir():
                continue
            
            # Skip hidden directories
            if sprint_path.name.startswith('.'):
                continue
            
            sprint_data = self._parse_sprint(sprint_path)
            if sprint_data:
                sprints.append(sprint_data)
        
        return sprints
    
    def _parse_sprint(self, sprint_path: Path) -> Optional[Dict[str, Any]]:
        """Parses a single sprint directory."""
        readme = sprint_path / "README.md"
        todo = sprint_path / "TODO.md"
        retro = sprint_path / "RETRO.md"
        
        sprint_id = sprint_path.name
        
        # Extract goal from README
        goal = ""
        title = sprint_id.replace("-", " ").title()
        
        if readme.exists():
            content = readme.read_text()
            
            # Extract title from first heading
            title_match = re.search(r'^#\s+Sprint:\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            
            # Extract goal from ## Goal section
            goal_match = re.search(r'##\s+Goal\s*\n+(.+?)(?:\n\n|\n##|$)', content, re.DOTALL)
            if goal_match:
                goal = goal_match.group(1).strip()
        
        # Extract tasks from TODO.md
        tasks = []
        if todo.exists():
            tasks = self._parse_todo(todo, sprint_id)
        
        # Determine status
        status = "closed" if retro.exists() else "active"
        
        # Extract learnings from RETRO.md if available
        learnings = []
        if retro.exists():
            learnings = self._parse_retro(retro)

        return {
            "id": sprint_id,
            "title": title,
            "status": status,
            "goals": goal,
            "tasks": tasks,
            "learnings": learnings
        }

    def get_recent_context(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Returns context from the most recent sprints."""
        all_sprints = self.collect_all_sprints()
        # Sort by sprint ID (assuming lexicographical order roughly matches chronological or use metadata if available)
        # Using simple string sort on ID for now, assuming format '000-name'
        sorted_sprints = sorted(all_sprints, key=lambda x: x['id'], reverse=True)
        return sorted_sprints[:limit]

    def _parse_retro(self, retro_path: Path) -> List[str]:
        """Mechanically extracts learnings from RETRO.md."""
        learnings = []
        content = retro_path.read_text()
        capture = False
        for line in content.split("\n"):
            line_stripped = line.strip()
            # Start capturing after these headers
            if line_stripped.startswith("## ") and any(x in line_stripped for x in ["Learnings", "Learning", "Went Well", "To Improve", "Could Be Improved", "Action Items"]):
                capture = True
                continue
            elif line_stripped.startswith("## "):
                capture = False
            
            if capture:
                if line_stripped.startswith("- "):
                    learnings.append(line_stripped[2:].strip())
                elif re.match(r'^\d+\.\s+', line_stripped):
                     learnings.append(re.sub(r'^\d+\.\s+', '', line_stripped).strip())
        return learnings
    
    def _parse_todo(self, todo_path: Path, sprint_id: str) -> List[Dict[str, Any]]:
        """Parses TODO.md and extracts tasks."""
        tasks = []
        content = todo_path.read_text()
        
        task_counter = 1
        for line in content.split("\n"):
            line_stripped = line.strip()
            
            # Match task lines: - [ ], - [x], - [/]
            if re.match(r'^-\s+\[.\]', line_stripped):
                # Extract checkbox status
                is_done = re.match(r'^-\s+\[x\]', line_stripped, re.IGNORECASE)
                is_in_progress = re.match(r'^-\s+\[/\]', line_stripped)
                
                # Extract task title (everything after the checkbox)
                title_match = re.search(r'^-\s+\[.\]\s+(.+)$', line_stripped)
                if not title_match:
                    continue
                
                title = title_match.group(1).strip()
                
                # Generate task ID
                task_id = f"{sprint_id}-task-{task_counter:03d}"
                
                tasks.append({
                    "id": task_id,
                    "title": title,
                    "status": "done" if is_done else ("in-progress" if is_in_progress else "todo"),
                    "metadata": {}
                })
                
                task_counter += 1
        
        return tasks
