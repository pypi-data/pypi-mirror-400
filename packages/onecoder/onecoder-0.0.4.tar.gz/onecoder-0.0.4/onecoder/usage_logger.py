import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

class UsageLogger:
    """Captures CLI usage telemetry for self-improvement and diagnostics."""
    
    def __init__(self):
        self.log_dir = Path.home() / ".onecoder" / "logs" / "usage"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_file = self.log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
    def log_command(self, command: str, args: List[str], exit_code: int = 0, metadata: Optional[Dict[str, Any]] = None):
        """Logs a single CLI command execution."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "command": command,
            "args": args,
            "exit_code": exit_code,
            "metadata": metadata or {}
        }
        
        # Append to session markdown file for readability
        with open(self.current_session_file, "a") as f:
            if os.path.getsize(self.current_session_file) == 0:
                f.write(f"# OneCoder CLI Usage Session: {timestamp}\n\n")
            
            f.write(f"## {timestamp} - `{command} {' '.join(args)}`\n")
            f.write(f"- **Exit Code**: {exit_code}\n")
            if metadata:
                f.write(f"- **Metadata**: \n```json\n{json.dumps(metadata, indent=2)}\n```\n")
            f.write("\n---\n\n")
            
    def get_recent_usage(self, limit: int = 5) -> str:
        """Retrieves summary of recent usage for feedback context."""
        try:
            # Simple implementation: read the current session file
            if self.current_session_file.exists():
                with open(self.current_session_file, "r") as f:
                    content = f.read()
                    # Return last few entries (primitive slicing)
                    return content[-2000:] # Return last 2KB
            return "No usage history found."
        except Exception as e:
            return f"Error retrieving usage history: {e}"

# Singleton instance
usage_logger = UsageLogger()
