import os
import json
import subprocess
import fnmatch
from typing import List, Dict, Any, Optional
from pathlib import Path

class HooksManager:
    def __init__(self, config_filename: str = "onecoder.hooks.json"):
        self.config_filename = config_filename
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Loads the configuration from the hooks file in the current directory."""
        # Look for config in current working directory
        config_path = Path.cwd() / self.config_filename
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing {self.config_filename}: {e}")
                return {}
            except Exception as e:
                print(f"Error reading {self.config_filename}: {e}")
                return {}
        return {}

    def _run_command(self, command: str):
        """Runs a shell command."""
        print(f"[Hooks] Running: {command}")
        try:
            # shell=True is used to allow running complex commands like "cargo check"
            # Security note: command comes from a user-defined config file.
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[Hooks] Command failed: {command} (Exit code: {e.returncode})")
        except Exception as e:
            print(f"[Hooks] Error running command {command}: {e}")

    def on_file_edit(self, filepath: str):
        """Triggers hooks configured for file edits."""
        # Reload config to pick up changes without restart
        self.config = self._load_config()

        file_patterns = self.config.get("file_patterns", [])

        # Determine relative path for matching
        try:
            rel_path = os.path.relpath(filepath, os.getcwd())
        except ValueError:
            # If filepath is on a different drive or invalid, use absolute
            rel_path = filepath

        for item in file_patterns:
            pattern = item.get("pattern")
            command = item.get("command")

            if pattern and command:
                if fnmatch.fnmatch(rel_path, pattern):
                    print(f"[Hooks] File {rel_path} matches pattern {pattern}")
                    self._run_command(command)

    def on_stop(self):
        """Triggers hooks configured for session stop."""
        self.config = self._load_config()
        commands = self.config.get("on_stop", [])
        if commands:
            print("[Hooks] Running on_stop hooks...")
            for command in commands:
                self._run_command(command)

# Global instance
hooks_manager = HooksManager()
