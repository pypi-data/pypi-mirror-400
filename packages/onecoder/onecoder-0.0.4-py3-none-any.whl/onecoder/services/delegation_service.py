import logging
import os
from typing import List, Optional
from pathlib import Path

from ..models.delegation import DelegationSession
from ..worktree import WorktreeManager
from ..tmux import TmuxManager
from ..blackboard import BlackboardMemory
from ..backends.base import BaseBackend
from ..backends.local_tui import LocalTUIBackend

logger = logging.getLogger(__name__)

class DelegationService:
    """
    Orchestrates delegated tasks using WorktreeManager and TmuxManager.
    """

    def __init__(self, blackboard: Optional[BlackboardMemory] = None):
        self.worktree_mgr = WorktreeManager()
        self.tmux_mgr = TmuxManager()
        self.blackboard = blackboard or BlackboardMemory()
        self.sessions_namespace = "delegation_sessions"
        self.backends: Dict[str, BaseBackend] = {
            "local-tui": LocalTUIBackend(self)
        }

    def create_session(self, task_id: str, backend: str = "local-tui", command: Optional[str] = None, external_id: Optional[str] = None) -> DelegationSession:
        """Creates and persists a new delegation session."""
        parent_branch = self.worktree_mgr.get_current_branch()
        active_sprint_id = os.environ.get("ACTIVE_SPRINT_ID")
        
        # Try to find spec_id from knowledge
        spec_id = None
        try:
            from ..knowledge import ProjectKnowledge
            pk = ProjectKnowledge()
            knowledge = pk.get_l1_context()
            if knowledge:
                # Usually spec_id is in the goal or active task metadata in some implementations
                # but for now we look for SPEC- prefix in active task title or goal
                goal = knowledge.get("goal", "")
                active_task = knowledge.get("active_task", {})
                
                import re
                spec_match = re.search(r"(SPEC-[A-Z0-9.-]+)", goal + " " + active_task.get("title", ""))
                if spec_match:
                    spec_id = spec_match.group(1)
        except Exception:
            pass

        session = DelegationSession(
            task_id=task_id,
            backend=backend,
            command=command,
            parent_branch=parent_branch,
            sprint_id=active_sprint_id,
            spec_id=spec_id,
            external_id=external_id
        )
        self._save_session(session)
        return session

    def _save_session(self, session: DelegationSession):
        """Persists session to blackboard memory."""
        self.blackboard.set(
            key=session.id,
            value=session.model_dump(mode='json'),
            scope="global",
            namespace=self.sessions_namespace
        )

    def get_session(self, session_id: str) -> Optional[DelegationSession]:
        """Retrieves a session from blackboard."""
        data = self.blackboard.get(
            key=session_id,
            scope="global",
            namespace=self.sessions_namespace
        )
        if data:
            return DelegationSession(**data)
        return None

    def list_sessions(self) -> List[DelegationSession]:
        """Lists all active delegation sessions."""
        all_data = self.blackboard.get_all(scope="global", namespace=self.sessions_namespace)
        return [DelegationSession(**data) for data in all_data.values()]

    async def start_session(self, session: DelegationSession, context_metadata: Optional[str] = None) -> str:
        """
        Starts a delegation session using the appropriate backend.
        """
        backend = self.backends.get(session.backend)
        if not backend:
            raise ValueError(f"Unknown backend: {session.backend}")
            
        return await backend.spawn(session)

    def stop_session(self, session_id: str, cleanup: bool = True):
        """Stops a session and optionally cleans up resources."""
        session = self.get_session(session_id)
        if not session:
            return

        if session.tmux_session:
            self.tmux_mgr.kill_session(session.tmux_session)
        
        if cleanup and session.worktree_path:
            self.worktree_mgr.remove_worktree(session.id, delete_branch=True)

        session.status = "stopped"
        self._save_session(session)

    def register_task_in_sprint(self, title: str, repo_root: Path) -> tuple[Optional[str], Optional[str]]:
        """
        Registers a new task in the active sprint's TODO.md and returns the generated ID.
        Returns: (sprint_id, task_id)
        """
        try:
            from ai_sprint.state import SprintStateManager
        except ImportError:
            logger.warning("ai_sprint SDK not available. Cannot register task.")
            return None, None

        sprint_dir = repo_root / ".sprint"
        if not sprint_dir.exists():
            return None, None

        # 1. Detect Active Sprint
        # Priority: ACTIVE_SPRINT_ID env > First Active Sprint found
        active_sprint_id = os.environ.get("ACTIVE_SPRINT_ID")
        
        if not active_sprint_id:
            # Simple discovery: Find first dir with .status containing "Active" or missing .status
            for item in sorted(sprint_dir.iterdir()):
                if item.is_dir() and item.name[0].isdigit(): # basic check for sprint dir
                    status_file = item / ".status"
                    if not status_file.exists() or status_file.read_text().strip() == "Active":
                        active_sprint_id = item.name
                        break
        
        if not active_sprint_id:
            return None, None

        target_sprint_dir = sprint_dir / active_sprint_id
        todo_file = target_sprint_dir / "TODO.md"
        
        if not todo_file.exists():
            return None, None

        # 2. Append to TODO.md
        # specific format: "- [ ] {title}"
        try:
            with open(todo_file, "a") as f:
                f.write(f"\n- [ ] {title}\n")
            
            # 3. Sync and Retrieve ID
            state_mgr = SprintStateManager(target_sprint_dir)
            state_mgr.sync_from_files()
            task_id = state_mgr.get_task_id_by_title(title)
            
            return active_sprint_id, task_id
            
        except Exception as e:
            logger.error(f"Failed to register task in sprint: {e}")
            return None, None

    def _inject_context(self, wt_path: Path, session: DelegationSession, metadata: Optional[str] = None):
        """Writes a BOOTSTRAP.md to the worktree to reduce agent TTU."""
        bootstrap_path = wt_path / "BOOTSTRAP.md"
        content = f"# Task: {session.task_id}\n\n"
        content += f"## Branch Context\nParent Branch: `{session.parent_branch}`\n"
        if session.sprint_id:
            content += f"Active Sprint: `{session.sprint_id}`\n"
        if session.spec_id:
            content += f"Spec ID: `{session.spec_id}`\n"
            
        content += f"\n## Instructions\n{session.command or 'No command provided.'}\n\n"
        content += "## Repository Context\n"
        
        # Try to gather automated knowledge
        try:
            from ..knowledge import ProjectKnowledge
            pk = ProjectKnowledge()
            knowledge = pk.get_rag_ready_output()
            content += knowledge
        except Exception:
            content += "Automated context gathering failed.\n"

        # Inject Mitigation Notes from recent review
        try:
            # Assume we are running from project root or can find it
            review_state_path = Path(".onecoder/review_state.json")
            if review_state_path.exists():
                import json
                state = json.loads(review_state_path.read_text())
                mitigation_notes = state.get("mitigation_notes")
                if mitigation_notes:
                    content += f"\n## Mitigation Notes (Recent Review)\n{mitigation_notes}\n"
        except Exception as e:
            logger.warning(f"Failed to inject review notes: {e}")

        if metadata:
            content += f"\n## Additional Metadata\n{metadata}\n"

        with open(bootstrap_path, "w") as f:
            f.write(content)
        logger.info(f"Injected context at {bootstrap_path}")
