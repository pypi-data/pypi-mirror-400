import os
import pytest
from pathlib import Path
from onecoder.services.validation_service import ValidationService, FileExistsRule, CommandSuccessRule

def test_validation_rules(tmp_path):
    # Setup mock worktree
    wt_path = tmp_path / "mock_wt"
    wt_path.mkdir()
    (wt_path / "result.txt").write_text("success")
    
    service = ValidationService()
    context = {"worktree_path": str(wt_path)}
    
    # 1. Test FileExistsRule
    rule1 = FileExistsRule("result.txt")
    rule2 = FileExistsRule("missing.txt")
    
    assert rule1.validate(context) == True
    assert rule2.validate(context) == False
    
    # 2. Test CommandSuccessRule
    rule3 = CommandSuccessRule("grep success result.txt")
    rule4 = CommandSuccessRule("grep failure result.txt")
    
    assert rule3.validate(context) == True
    assert rule4.validate(context) == False
    
    # 3. Test ValidationService aggregation
    report = service.validate_session(context, [rule1, rule3])
    assert report["all_passed"] == True
    assert len(report["results"]) == 2
    
    report_fail = service.validate_session(context, [rule1, rule2, rule3])
    assert report_fail["all_passed"] == False

if __name__ == "__main__":
    # Manual run if needed
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_validation_rules(Path(tmp))
        print("Validation service tests passed!")
