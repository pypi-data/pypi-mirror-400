import subprocess
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class TmuxManager:
    """
    Manages tmux sessions and panes for delegated tasks.
    """

    def __init__(self):
        self._check_tmux()

    def _check_tmux(self):
        try:
            subprocess.run(["tmux", "-V"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("tmux is not installed or not available in PATH")

    def _run_tmux(self, args: List[str]) -> str:
        command = ["tmux"] + args
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.debug(f"Tmux command failed: {' '.join(command)}\nError: {result.stderr}")
            raise RuntimeError(f"Tmux error: {result.stderr.strip()}")
        return result.stdout.strip()

    def has_session(self, name: str) -> bool:
        try:
            self._run_tmux(["has-session", "-t", name])
            return True
        except RuntimeError:
            return False

    def create_session(self, name: str, command: Optional[str] = None, cwd: Optional[str] = None) -> None:
        """Creates a new detached tmux session."""
        args = ["new-session", "-d", "-s", name]
        if cwd:
            args += ["-c", cwd]
        if command:
            args.append(command)
        self._run_tmux(args)

    def split_window(self, target_session: str, command: Optional[str] = None, horizontal: bool = True) -> None:
        """Splits the current window of a session."""
        args = ["split-window", "-t", target_session]
        if horizontal:
            args.append("-h")
        else:
            args.append("-v")
        if command:
            args.append(command)
        self._run_tmux(args)

    def kill_session(self, name: str) -> None:
        """Kills a tmux session."""
        if self.has_session(name):
            self._run_tmux(["kill-session", "-t", name])

    def list_sessions(self) -> List[str]:
        """Lists all tmux sessions."""
        try:
            output = self._run_tmux(["list-sessions", "-F", "#S"])
            return output.split("\n")
        except RuntimeError:
            return []

    def send_keys(self, target: str, keys: str, enter: bool = True) -> None:
        """Sends keys to a tmux session/pane."""
        args = ["send-keys", "-t", target, keys]
        if enter:
            args.append("C-m")
        self._run_tmux(args)

if __name__ == "__main__":
    # Quick test
    import time
    mgr = TmuxManager()
    session = "test-session"
    print(f"Creating session: {session}")
    mgr.create_session(session, "top")
    time.sleep(2)
    print(f"Sessions: {mgr.list_sessions()}")
    mgr.kill_session(session)
    print("Session killed.")
