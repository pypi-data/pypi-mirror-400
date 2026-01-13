"""Google Jules API Client for OneCoder.

This module provides a robust client for interacting with the Google Jules API,
including session management, activity polling with incremental backoff, and
PR output detection.
"""

import os
import time
import requests
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass


# Custom Exceptions
class JulesAPIError(Exception):
    """Base exception for Jules API errors."""
    pass


class JulesAuthError(JulesAPIError):
    """Authentication error (401/403)."""
    pass


class JulesNotFoundError(JulesAPIError):
    """Resource not found (404)."""
    pass


@dataclass
class JulesSession:
    """Represents a Jules session with metadata."""
    id: str
    title: str
    prompt: str
    state: str
    outputs: List[Dict[str, Any]]
    raw_data: Dict[str, Any]


@dataclass
class JulesActivity:
    """Represents a Jules activity."""
    id: str
    originator: str
    activity_type: str
    data: Dict[str, Any]


class JulesAPIClient:
    """Client for interacting with the Google Jules API.
    
    Features:
    - Incremental backoff for activity polling
    - Transient 404 handling with retry logic
    - Session state caching
    - PR output detection
    """
    
    # Backoff intervals for polling (in seconds)
    BACKOFF_INTERVALS = [2, 5, 10, 30]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://jules.googleapis.com/v1alpha"
    ):
        """Initialize the Jules API client.
        
        Args:
            api_key: Google Jules API key (defaults to JULES_API_KEY env var)
            base_url: API base URL (defaults to production endpoint)
        """
        self.api_key = api_key or os.environ.get("JULES_API_KEY")
        if not self.api_key:
            raise JulesAuthError("JULES_API_KEY not found in environment or parameters")
        
        self.base_url = base_url.rstrip("/")
        self._session_cache: Dict[str, JulesSession] = {}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        return {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions.
        
        Args:
            response: requests Response object
            
        Returns:
            Parsed JSON response
            
        Raises:
            JulesAuthError: For 401/403 errors
            JulesNotFoundError: For 404 errors
            JulesAPIError: For other API errors
        """
        if response.status_code == 401 or response.status_code == 403:
            raise JulesAuthError(f"Authentication failed: {response.status_code}")
        
        if response.status_code == 404:
            raise JulesNotFoundError(f"Resource not found: {response.url}")
        
        if not response.ok:
            raise JulesAPIError(
                f"API request failed: {response.status_code} - {response.text}"
            )
        
        return response.json()
    
    def create_session(
        self,
        prompt: str,
        source: Optional[str] = None,
        branch: str = "main",
        automation_mode: str = "AUTO_CREATE_PR"
    ) -> JulesSession:
        """Create a new Jules session.
        
        Args:
            prompt: The coding task description
            source: GitHub source (e.g., 'sources/github/owner/repo')
            branch: Starting branch (default: 'main')
            automation_mode: Automation mode (default: 'AUTO_CREATE_PR')
            
        Returns:
            JulesSession object with session metadata
            
        Raises:
            JulesAPIError: If session creation fails
        """
        source = source or os.environ.get("JULES_SOURCE")
        if not source:
            raise JulesAPIError("source parameter or JULES_SOURCE env var required")
        
        url = f"{self.base_url}/sessions"
        data = {
            "prompt": prompt,
            "sourceContext": {
                "source": source,
                "githubRepoContext": {
                    "startingBranch": branch
                }
            },
            "automationMode": automation_mode,
            "title": f"OneCoder Task: {prompt[:50]}"
        }
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=data,
            timeout=30
        )
        session_data = self._handle_response(response)
        
        session = JulesSession(
            id=session_data.get("id"),
            title=session_data.get("title", ""),
            prompt=session_data.get("prompt", ""),
            state=session_data.get("state", "UNKNOWN"),
            outputs=session_data.get("outputs", []),
            raw_data=session_data
        )
        
        # Cache the session
        self._session_cache[session.id] = session
        
        return session
    
    def get_session(self, session_id: str, use_cache: bool = False) -> JulesSession:
        """Get session metadata.
        
        Args:
            session_id: The Jules session ID
            use_cache: If True, return cached session if available
            
        Returns:
            JulesSession object
            
        Raises:
            JulesNotFoundError: If session not found
            JulesAPIError: For other API errors
        """
        if use_cache and session_id in self._session_cache:
            return self._session_cache[session_id]
        
        url = f"{self.base_url}/sessions/{session_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        session_data = self._handle_response(response)
        
        session = JulesSession(
            id=session_data.get("id"),
            title=session_data.get("title", ""),
            prompt=session_data.get("prompt", ""),
            state=session_data.get("state", "UNKNOWN"),
            outputs=session_data.get("outputs", []),
            raw_data=session_data
        )
        
        # Update cache
        self._session_cache[session_id] = session
        
        return session
    
    def list_activities(
        self,
        session_id: str,
        page_size: int = 10,
        retry_on_404: bool = True,
        max_retries: int = 3
    ) -> List[JulesActivity]:
        """List activities for a session with retry logic.
        
        Args:
            session_id: The Jules session ID
            page_size: Number of activities to fetch
            retry_on_404: If True, retry on transient 404 errors
            max_retries: Maximum number of retries for 404
            
        Returns:
            List of JulesActivity objects
            
        Raises:
            JulesNotFoundError: If session not found after retries
            JulesAPIError: For other API errors
        """
        url = f"{self.base_url}/sessions/{session_id}/activities"
        params = {"pageSize": page_size}
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=30
                )
                data = self._handle_response(response)
                
                activities = []
                for activity_data in data.get("activities", []):
                    # Determine activity type
                    activity_type = "unknown"
                    if "planGenerated" in activity_data:
                        activity_type = "plan_generated"
                    elif "progressUpdated" in activity_data:
                        activity_type = "progress_updated"
                    elif "sessionCompleted" in activity_data:
                        activity_type = "session_completed"
                    
                    activities.append(JulesActivity(
                        id=activity_data.get("id", ""),
                        originator=activity_data.get("originator", "unknown"),
                        activity_type=activity_type,
                        data=activity_data
                    ))
                
                return activities
                
            except JulesNotFoundError:
                if not retry_on_404 or attempt >= max_retries - 1:
                    raise
                # Transient 404 - wait before retry
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
        
        return []
    
    def poll_until_complete(
        self,
        session_id: str,
        callback: Optional[Callable[[JulesSession, List[JulesActivity]], None]] = None,
        max_iterations: int = 60
    ) -> JulesSession:
        """Poll session until completion with incremental backoff.
        
        Args:
            session_id: The Jules session ID
            callback: Optional callback function called on each poll
            max_iterations: Maximum number of polling iterations
            
        Returns:
            Final JulesSession object
            
        Raises:
            JulesAPIError: If polling fails
        """
        backoff_index = 0
        
        for iteration in range(max_iterations):
            # Get current session state
            session = self.get_session(session_id)
            
            # Get recent activities
            try:
                activities = self.list_activities(session_id, page_size=5)
            except JulesNotFoundError:
                # Activities might not be available yet
                activities = []
            
            # Call callback if provided
            if callback:
                callback(session, activities)
            
            # Check if session is complete
            if session.state in ["COMPLETED", "FAILED", "CANCELLED"]:
                return session
            
            # Incremental backoff
            wait_time = self.BACKOFF_INTERVALS[
                min(backoff_index, len(self.BACKOFF_INTERVALS) - 1)
            ]
            time.sleep(wait_time)
            backoff_index += 1
        
        # Max iterations reached
        return session
    
    def detect_pr_output(self, session_id: str) -> Optional[Dict[str, str]]:
        """Detect PR output from a session.
        
        Args:
            session_id: The Jules session ID
            
        Returns:
            Dict with 'url' and 'title' if PR found, None otherwise
        """
        session = self.get_session(session_id)
        
        for output in session.outputs:
            if "pullRequest" in output:
                pr = output["pullRequest"]
                return {
                    "url": pr.get("url", ""),
                    "title": pr.get("title", "")
                }
        
        return None
