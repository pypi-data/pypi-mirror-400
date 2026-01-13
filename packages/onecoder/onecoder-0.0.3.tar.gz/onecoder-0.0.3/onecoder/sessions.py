import os
import json
import time
import copy
import logging
from typing import Any, Optional, Dict, List
from pathlib import Path
from pydantic import BaseModel

from google.adk.sessions.base_session_service import BaseSessionService, GetSessionConfig, ListSessionsResponse
from google.adk.sessions.session import Session
from google.adk.events.event import Event
from google.adk.sessions.state import State
from google.adk.sessions import _session_util

logger = logging.getLogger(__name__)

class DurableSessionService(BaseSessionService):
    """
    A filesystem-backed session service for OneCoder.
    Persists sessions, app state, and user state as JSON files.
    """

    def __init__(self, storage_dir: str = ".adk/sessions"):
        self.storage_dir = Path(storage_dir)
        self.sessions_dir = self.storage_dir / "sessions"
        self.app_state_dir = self.storage_dir / "apps"
        self.user_state_dir = self.storage_dir / "users"
        
        # Ensure directories exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.app_state_dir.mkdir(parents=True, exist_ok=True)
        self.user_state_dir.mkdir(parents=True, exist_ok=True)

    def _get_session_path(self, app_name: str, user_id: str, session_id: str) -> Path:
        return self.sessions_dir / app_name / user_id / f"{session_id}.json"

    def _get_app_state_path(self, app_name: str) -> Path:
        return self.app_state_dir / f"{app_name}.json"

    def _get_user_state_path(self, app_name: str, user_id: str) -> Path:
        return self.user_state_dir / app_name / f"{user_id}.json"

    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            if isinstance(data, BaseModel):
                f.write(data.model_dump_json(by_alias=True, indent=2))
            else:
                json.dump(data, f, indent=2)

    def _load_json(self, path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        with open(path, "r") as f:
            return json.load(f)

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=state or {},
            last_update_time=time.time()
        )
        
        self._save_json(self._get_session_path(app_name, user_id, session_id), session)
        return session

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        path = self._get_session_path(app_name, user_id, session_id)
        data = self._load_json(path)
        if not data:
            return None
            
        session = Session.model_validate(data)
        
        # Filtering events based on config
        if config:
            if config.num_recent_events:
                session.events = session.events[-config.num_recent_events:]
            if config.after_timestamp:
                session.events = [e for e in session.events if e.timestamp >= config.after_timestamp]
        
        return self._merge_state(app_name, user_id, session)

    def _merge_state(self, app_name: str, user_id: str, session: Session) -> Session:
        # Load and merge app state
        app_state = self._load_json(self._get_app_state_path(app_name)) or {}
        for key, value in app_state.items():
            session.state[State.APP_PREFIX + key] = value
            
        # Load and merge user state
        user_state = self._load_json(self._get_user_state_path(app_name, user_id)) or {}
        for key, value in user_state.items():
            session.state[State.USER_PREFIX + key] = value
            
        return session

    async def list_sessions(
        self, *, app_name: str, user_id: Optional[str] = None
    ) -> ListSessionsResponse:
        sessions = []
        app_path = self.sessions_dir / app_name
        if not app_path.exists():
            return ListSessionsResponse(sessions=[])
            
        user_ids = [user_id] if user_id else [u.name for u in app_path.iterdir() if u.is_dir()]
        
        for uid in user_ids:
            user_path = app_path / uid
            if not user_path.exists():
                continue
            for session_file in user_path.glob("*.json"):
                data = self._load_json(session_file)
                if data:
                    s = Session.model_validate(data)
                    s.events = [] # Following list_sessions contract (no events)
                    sessions.append(self._merge_state(app_name, uid, s))
                    
        return ListSessionsResponse(sessions=sessions)

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        path = self._get_session_path(app_name, user_id, session_id)
        if path.exists():
            path.unlink()

    async def append_event(self, session: Session, event: Event) -> Event:
        if event.partial:
            return event
            
        # Update session object in memory (handles state delta too)
        await super().append_event(session, event)
        session.last_update_time = event.timestamp
        
        # Load the stored session to apply events and state deltas
        path = self._get_session_path(session.app_name, session.user_id, session.id)
        data = self._load_json(path)
        if not data:
            logger.warning(f"Session file not found during append_event: {path}")
            # If it's missing, we still save the passed session as a recovery
            self._save_json(path, session)
            return event
            
        storage_session = Session.model_validate(data)
        storage_session.events.append(event)
        storage_session.last_update_time = event.timestamp
        
        # Apply state deltas to persistent state files
        if event.actions and event.actions.state_delta:
            deltas = _session_util.extract_state_delta(event.actions.state_delta)
            
            if deltas["app"]:
                app_state = self._load_json(self._get_app_state_path(session.app_name)) or {}
                app_state.update(deltas["app"])
                self._save_json(self._get_app_state_path(session.app_name), app_state)
                
            if deltas["user"]:
                user_state = self._load_json(self._get_user_state_path(session.app_name, session.user_id)) or {}
                user_state.update(deltas["user"])
                self._save_json(self._get_user_state_path(session.app_name, session.user_id), user_state)
                
            if deltas["session"]:
                storage_session.state.update(deltas["session"])
                
        self._save_json(path, storage_session)
        return event
