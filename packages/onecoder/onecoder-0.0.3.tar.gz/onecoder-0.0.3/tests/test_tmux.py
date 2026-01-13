import os
import time
import pytest
from onecoder.tmux import TmuxManager

def test_tmux_lifecycle():
    try:
        mgr = TmuxManager()
    except RuntimeError as e:
        pytest.skip(f"tmux not available: {e}")
        return

    session_name = "test-session-multiplex"
    
    # Ensure clean start
    mgr.kill_session(session_name)
    
    # 1. Create session
    mgr.create_session(session_name, "sleep 10")
    assert mgr.has_session(session_name)
    
    # 2. List sessions
    sessions = mgr.list_sessions()
    assert session_name in sessions
    
    # 3. Split window (create pane)
    mgr.split_window(session_name, "sleep 5")
    
    # 4. Cleanup
    mgr.kill_session(session_name)
    assert not mgr.has_session(session_name)

if __name__ == "__main__":
    try:
        test_tmux_lifecycle()
        print("Tmux lifecycle test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
