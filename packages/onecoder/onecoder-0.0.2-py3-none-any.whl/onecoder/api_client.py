import httpx
import os
import json
from typing import Optional, Dict, Any, List

class OneCoderAPIClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def set_token(self, token: str):
        """Update the client's token."""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"

    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Internal helper for API requests."""
        url = f"{self.base_url}/api/v1{path}"
        if path.startswith("/api/v1"):
            url = f"{self.base_url}{path}"
            
        import logging
        logging.debug(f"Making request to: {url}")
            
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def login_with_github(self, code: str) -> Dict[str, Any]:
        """Exchange GitHub OAuth code for a JWT token."""
        data = await self._request("POST", "/auth/github", json={"code": code})
        if "token" not in data:
            raise ValueError(f"Invalid API response: Missing 'token' field. Got keys: {list(data.keys())}")
        self.set_token(data["token"])
        return data

    async def get_preferences(self) -> Dict[str, Any]:
        """Fetch user preferences from the API."""
        return await self._request("GET", "/users/me/preferences")

    async def update_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences via the API."""
        return await self._request("PUT", "/users/me/preferences", json=preferences)

    async def get_me(self) -> Dict[str, Any]:
        """Get current user information."""
        url = f"{self.base_url}/api/v1/users/me"
        # Since /api/v1/users/me is not explicitly implemented in my last edit, 
        # I'll use /api/v1/auth/me or similar if I implement it, or just stick to what exists.
        # Actually, let's implement /api/v1/users/me in the API later or use the token payload.
        pass

    async def sync_project(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync project durable context (specs, metadata) to the API."""
        url = f"{self.base_url}/api/v1/projects/{project_id}/sync"
        return await self._request("POST", f"/projects/{project_id}/sync", json=data)

    async def sync_sprint(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync sprint state (tasks, status) to the API."""
        return await self._request("POST", "/sprints/sync", json=data)

    async def sync_issues(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Syncs issue data."""
        return await self._request("POST", "/issues/sync", json=data)

    async def get_workspaces(self) -> List[Dict[str, Any]]:
        """Fetch list of available workspaces."""
        data = await self._request("GET", "/workspaces")
        return data.get("workspaces", [])

    async def create_workspace(self, name: str) -> Dict[str, Any]:
        """Create a new workspace."""
        data = await self._request("POST", "/workspaces", json={"name": name})
        return data.get("workspace", {})

    async def create_project(self, name: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new project."""
        payload = {"name": name}
        if workspace_id:
            payload["workspaceId"] = workspace_id
        data = await self._request("POST", "/projects", json=payload)
        return data.get("project", {})

    async def join_workspace(self, workspace_id: str, project_id: str) -> Dict[str, Any]:
        """Associate a project with a workspace."""
        return await self._request("POST", f"/workspaces/{workspace_id}/projects", json={"projectId": project_id})

    async def upload_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a single failure mode to the API."""
        return await self._request("POST", "/failure-modes", json=failure_data)

    async def analyze_project(self, scan_data: Dict[str, Any], user_feedback: Optional[str] = None) -> Dict[str, Any]:
        """Request server-side analysis of a project."""
        payload = {"scanData": scan_data}
        if user_feedback:
            payload["userFeedback"] = user_feedback
            
        # Increase timeout for analysis as it involves LLM processing
        return await self._request("POST", "/projects/analyze", json=payload, timeout=60.0)

from .constants import ONECODER_API_URL

def get_api_client(token: Optional[str] = None) -> OneCoderAPIClient:
    base_url = ONECODER_API_URL
    return OneCoderAPIClient(base_url, token)
