from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class DelegationSession(BaseModel):
    """
    Represents a delegated task session.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    backend: str  # local-tui, jules, browser, etc.
    status: str = "pending"  # pending, running, completed, failed
    
    # Context
    worktree_path: Optional[str] = None
    tmux_session: Optional[str] = None
    command: Optional[str] = None
    parent_branch: Optional[str] = None
    sprint_id: Optional[str] = None
    spec_id: Optional[str] = None
    external_id: Optional[str] = None # For remote sessions (e.g. Jules ID)
    
    # Results
    result: Optional[str] = None
    error: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def mark_running(self, tmux_session: Optional[str] = None, worktree_path: Optional[str] = None):
        self.status = "running"
        self.tmux_session = tmux_session
        self.worktree_path = worktree_path
        self.updated_at = datetime.now()

    def mark_completed(self, result: str):
        self.status = "completed"
        self.result = result
        self.updated_at = datetime.now()

    def mark_failed(self, error: str):
        self.status = "failed"
        self.error = error
        self.updated_at = datetime.now()
