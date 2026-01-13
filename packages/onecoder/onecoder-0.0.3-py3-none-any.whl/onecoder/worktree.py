import os
import subprocess
import shutil
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

class WorktreeManager:
    """
    Manages Git worktrees for isolated task execution.
    """

    def __init__(self, project_root: Optional[str] = None):
        if project_root:
            self.project_root = Path(project_root).absolute()
        else:
            self.project_root = self._find_repo_root(Path.cwd())
            
        self.worktrees_dir = self.project_root / ".adk" / "worktrees"
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)

    def get_current_branch(self) -> str:
        """Returns the name of the current active branch."""
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])

    def _find_repo_root(self, start_path: Path) -> Path:
        """Traverses upwards to find the repository root."""
        curr = start_path
        while curr != curr.parent:
            if (curr / ".git").exists() or (curr / ".sprint").exists():
                return curr
            curr = curr.parent
        return start_path

    def _run_git(self, args: List[str], cwd: Optional[Path] = None) -> str:
        """Helper to run git commands."""
        command = ["git"] + args
        result = subprocess.run(
            command,
            cwd=str(cwd or self.project_root),
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {' '.join(command)}\nError: {result.stderr}")
        return result.stdout.strip()

    def create_worktree(self, task_id: str, base_ref: Optional[str] = None) -> Path:
        """
        Creates a new git worktree for a task.
        Defaults to branching off the current HEAD if base_ref is not provided.
        """
        if base_ref is None:
             base_ref = self.get_current_branch()
             logger.info(f"No base_ref provided, using current branch: {base_ref}")

        task_dir = self.worktrees_dir / task_id
        if task_dir.exists():
            logger.warning(f"Worktree directory already exists: {task_dir}")
            # Try to remove it first if it's stale
            self.remove_worktree(task_id)

        branch_name = f"task/{task_id}"
        
        # Check if branch exists, if so, use it, otherwise create it
        try:
            # Check if branch already exists
            self._run_git(["rev-parse", "--verify", branch_name])
            logger.info(f"Using existing branch: {branch_name}")
            self._run_git(["worktree", "add", str(task_dir), branch_name])
        except RuntimeError:
            logger.info(f"Creating new worktree and branch: {branch_name} from {base_ref}")
            self._run_git(["worktree", "add", "-b", branch_name, str(task_dir), base_ref])

        return task_dir

    def remove_worktree(self, task_id: str, delete_branch: bool = False) -> None:
        """
        Removes a git worktree.
        """
        task_dir = self.worktrees_dir / task_id
        if not task_dir.exists():
            logger.warning(f"Worktree directory does not exist: {task_dir}")
            # Still try to prune just in case
            self._run_git(["worktree", "prune"])
            return

        logger.info(f"Removing worktree: {task_dir}")
        try:
            self._run_git(["worktree", "remove", "--force", str(task_dir)])
        except RuntimeError as e:
            logger.error(f"Failed to remove worktree via git: {e}")
            # Fallback to manual removal if git remove fails
            if task_dir.exists():
                shutil.rmtree(task_dir, ignore_errors=True)
                self._run_git(["worktree", "prune"])

        if delete_branch:
            branch_name = f"task/{task_id}"
            try:
                self._run_git(["branch", "-D", branch_name])
            except RuntimeError:
                pass

    def merge_task_branch(self, task_id: str, target_branch: str) -> bool:
        """
        Merges a task branch into a target branch.
        Uses --no-ff to preserve atomic work history.
        """
        branch_name = f"task/{task_id}"
        logger.info(f"Merging {branch_name} into {target_branch}")
        
        try:
            # 1. Ensure we are on the target branch
            current = self.get_current_branch()
            if current != target_branch:
                self._run_git(["checkout", target_branch])
            
            # 2. Perform merge
            self._run_git(["merge", "--no-ff", "-m", f"chore: merge delegated task {task_id}", branch_name])
            return True
        except RuntimeError as e:
            logger.error(f"Merge failed: {e}")
            # If we were on target branch, try to abort merge if it's stuck
            try:
                self._run_git(["merge", "--abort"])
            except:
                pass
            return False

    def rebase_onto(self, task_id: str, upstream: str) -> bool:
        """Rebases the task branch onto an upstream branch to ensure compatibility."""
        branch_name = f"task/{task_id}"
        logger.info(f"Rebasing {branch_name} onto {upstream}")
        original_branch = self.get_current_branch()
        try:
            # Note: git rebase <upstream> <branch> switches HEAD to <branch>
            self._run_git(["rebase", upstream, branch_name])
            return True
        except RuntimeError as e:
            logger.error(f"Rebase failed: {e}")
            try:
                self._run_git(["rebase", "--abort"])
            except:
                pass
            return False
        finally:
            # Always ensure we return to the original branch
            if self.get_current_branch() != original_branch:
                self._run_git(["checkout", original_branch])

    def list_worktrees(self) -> List[dict]:
        """
        Lists all active worktrees.
        """
        output = self._run_git(["worktree", "list", "--porcelain"])
        worktrees = []
        current_wt = {}
        
        for line in output.split("\n"):
            if not line:
                if current_wt:
                    worktrees.append(current_wt)
                    current_wt = {}
                continue
            
            parts = line.split(" ", 1)
            if len(parts) == 2:
                current_wt[parts[0]] = parts[1]
                
        if current_wt:
            worktrees.append(current_wt)
            
        return worktrees

if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    mgr = WorktreeManager()
    path = mgr.create_worktree("test-task")
    print(f"Worktree created at: {path}")
    mgr.remove_worktree("test-task", delete_branch=True)
    print("Worktree removed.")
