import os
import shutil
import pytest
from pathlib import Path
from onecoder.worktree import WorktreeManager

def test_worktree_lifecycle():
    mgr = WorktreeManager()
    task_id = "test-task-wt"
    
    # 1. Create worktree
    wt_path = mgr.create_worktree(task_id)
    assert wt_path.exists()
    assert (wt_path / ".git").exists() or (mgr.project_root / ".git").exists() # Worktree has a .git file pointing to main repo
    
    # Verify it's in the list
    wts = mgr.list_worktrees()
    assert any(str(wt_path) in wt.get("worktree", "") for wt in wts)
    
    # 2. Cleanup
    mgr.remove_worktree(task_id, delete_branch=True)
    assert not wt_path.exists()
    
    # Verify it's gone from the list
    wts = mgr.list_worktrees()
    assert not any(str(wt_path) in wt.get("worktree", "") for wt in wts)

if __name__ == "__main__":
    try:
        test_worktree_lifecycle()
        print("Worktree lifecycle test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
