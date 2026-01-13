import os
import logging
from pathlib import Path
from .base import BaseBackend
from ..models.delegation import DelegationSession
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..services.delegation_service import DelegationService

logger = logging.getLogger(__name__)

class LocalTUIBackend(BaseBackend):
    """
    Spawns a local terminal UI (via tmux) in an isolated worktree.
    """

    def __init__(self, delegation_service: 'DelegationService'):
        self.service = delegation_service

    async def spawn(self, session: DelegationSession) -> str:
        # Use delegation service to handle the heavy lifting
        logger.info(f"Spawning local TUI for session {session.id}")
        
        # 1. Create worktree
        wt_path = self.service.worktree_mgr.create_worktree(session.id)
        
        # 2. Reduce TTU: Inject context
        self.service._inject_context(wt_path, session)
        
        # 3. Define tmux session name
        tmux_name = f"onecoder-{session.id[:8]}"
        
        # 4. Create tmux session
        # Use gemini as default command if available, fallback to shell
        # We also pass the task prompt to a temporary file for the agent to read
        agent_cmd = "gemini"
        
        # Check if gemini is in path
        import shutil
        if not shutil.which("gemini"):
            logger.warning("Gemini CLI not found in PATH, falling back to shell.")
            agent_cmd = "$SHELL"

        cmd = f"cd {wt_path} && export ACTIVE_SPRINT_ID={os.environ.get('ACTIVE_SPRINT_ID', '')} && {agent_cmd}"
        if session.command:
            # Provide the prompt to the agent via a dedicated instruction file
            instruction_path = wt_path / "INSTRUCTIONS.md"
            instruction_path.write_text(f"# Task\n{session.command}")
            # In some agents, we can pass the prompt as an argument
            if agent_cmd == "gemini":
                cmd = f"cd {wt_path} && export ACTIVE_SPRINT_ID={os.environ.get('ACTIVE_SPRINT_ID', '')} && {agent_cmd} 'Review INSTRUCTIONS.md and execute the task.'"
            else:
                cmd = f"cd {wt_path} && echo '# {session.command}' >> BOOTSTRAP.md && {agent_cmd}"

        self.service.tmux_mgr.create_session(tmux_name, cmd, cwd=str(wt_path))
        
        # 5. Update session status
        session.mark_running(tmux_session=tmux_name, worktree_path=str(wt_path))
        self.service._save_session(session)
        
        return f"tmux attach -t {tmux_name}"

    async def cleanup(self, session: DelegationSession):
        self.service.stop_session(session.id)
