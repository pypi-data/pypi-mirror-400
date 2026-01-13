import os
import sys
from pathlib import Path

class LazyConsole:
    def __init__(self):
        self._console = None

    @property
    def inner(self):
        if self._console is None:
            from rich.console import Console
            self._console = Console()
        return self._console

    def print(self, *args, **kwargs):
        self.inner.print(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.inner, name)

console = LazyConsole()

def find_project_root():
    """Find the project root directory (containing .git)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()

PROJECT_ROOT = find_project_root()
SPRINT_DIR = PROJECT_ROOT / ".sprint"

from ..state import SprintStateManager
from ..commit import auto_detect_sprint_id
