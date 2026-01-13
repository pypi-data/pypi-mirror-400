"""Jules API integration tool for OneCoder.

This module provides tool functions that wrap the JulesAPIClient for use
in the ADK tool registry and backward compatibility with existing tests.
"""

import os
import requests
from typing import Union
from ..jules_client import JulesAPIClient, JulesAPIError, JulesAuthError, JulesNotFoundError


def jules_delegate_tool(prompt: str, source: Union[str, None] = None) -> str:
    """Delegate a coding task to Google Jules.
    
    Args:
        prompt: The coding task description
        source: GitHub source (e.g., 'sources/github/owner/repo'). 
                Defaults to JULES_SOURCE env var.
    
    Returns:
        Status message with session ID and initial response
    """
    try:
        # Initialize client
        client = JulesAPIClient()
        
        # Create session
        session = client.create_session(prompt, source=source)
        
        # Get initial activities
        try:
            activities = client.list_activities(session.id, page_size=5)
        except JulesNotFoundError:
            # Activities might not be available yet
            activities = []
        
        # Format response
        result = f"✓ Jules session created: {session.id}\n"
        result += f"Task: {prompt}\n"
        result += f"Source: {source or os.environ.get('JULES_SOURCE')}\n\n"
        
        if activities:
            result += "Initial Activities:\n"
            for activity in activities[:3]:
                if activity.activity_type == "plan_generated":
                    plan = activity.data.get("planGenerated", {}).get("plan", {})
                    steps = len(plan.get("steps", []))
                    result += f"- Plan generated with {steps} steps\n"
                elif activity.activity_type == "progress_updated":
                    progress = activity.data.get("progressUpdated", {})
                    result += f"- {progress.get('title', 'Progress update')}\n"
        
        result += f"\nMonitor progress at: https://jules.google.com/sessions/{session.id}"
        return result
        
    except JulesAuthError as e:
        return f"Error: JULES_API_KEY environment variable not set"
    except JulesAPIError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def jules_status_tool(session_id: str) -> str:
    """Check the status of a Jules session.
    
    Args:
        session_id: The Jules session ID
    
    Returns:
        Current status and recent activities
    """
    try:
        # Initialize client
        client = JulesAPIClient()
        
        # Get session info
        session = client.get_session(session_id)
        
        # Get recent activities
        try:
            activities = client.list_activities(session_id, page_size=10)
        except JulesNotFoundError:
            activities = []
        
        # Format response
        result = f"Session: {session_id}\n"
        result += f"Title: {session.title or 'N/A'}\n"
        result += f"Prompt: {session.prompt or 'N/A'}\n\n"
        
        # Check for PR output
        pr_output = client.detect_pr_output(session_id)
        if pr_output:
            result += "Outputs:\n"
            result += f"- PR: {pr_output['url']}\n"
            result += f"  Title: {pr_output['title']}\n"
        
        # Show recent activities
        if activities:
            result += "\nRecent Activities:\n"
            for activity in activities[:5]:
                if activity.activity_type == "plan_generated":
                    result += f"- [{activity.originator}] Plan generated\n"
                elif activity.activity_type == "progress_updated":
                    progress = activity.data.get("progressUpdated", {})
                    result += f"- [{activity.originator}] {progress.get('title', 'Progress')}\n"
                elif activity.activity_type == "session_completed":
                    result += f"- [{activity.originator}] Session completed ✓\n"
        
        return result
        
    except JulesNotFoundError:
        return f"Jules session with ID '{session_id}' not found."
    except JulesAuthError:
        return "Error: JULES_API_KEY environment variable not set"
    except JulesAPIError as e:
        return f"Error communicating with Jules API: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Jules API: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
