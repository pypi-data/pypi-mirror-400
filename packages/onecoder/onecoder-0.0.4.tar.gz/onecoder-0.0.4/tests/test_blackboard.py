import os
import pytest
from onecoder.blackboard import BlackboardMemory

def test_blackboard_lifecycle():
    db_path = "test_blackboard_lifecycle.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    bb = BlackboardMemory(db_path=db_path)
    
    # 1. Set and Get global
    bb.set("plan", {"step": 1})
    assert bb.get("plan") == {"step": 1}
    
    # 2. Scoping
    bb.set("step", 2, scope="task-1")
    assert bb.get("step", scope="task-1") == 2
    assert bb.get("step") is None # Global should be empty
    
    # 3. Namespace
    bb.set("secret", "xyz", namespace="private")
    assert bb.get("secret", namespace="private") == "xyz"
    assert bb.get("secret") is None
    
    # 4. List keys
    keys = bb.list_keys()
    assert any(k["key"] == "plan" for k in keys)
    assert any(k["scope"] == "task-1" for k in keys)
    
    # 5. Get all
    bb.set("a", 1, scope="bulk")
    bb.set("b", 2, scope="bulk")
    all_vals = bb.get_all(scope="bulk")
    assert all_vals == {"a": 1, "b": 2}
    
    # 6. Cleanup
    bb.delete("plan")
    assert bb.get("plan") is None
    
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    try:
        test_blackboard_lifecycle()
        print("Blackboard lifecycle test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
