import pytest
import importlib

def test_ai_sprint_importable():
    """Verify that ai_sprint can be imported."""
    try:
        import ai_sprint
        assert ai_sprint is not None
    except ImportError:
        pytest.fail("ai_sprint package could not be imported")

def test_sprint_command_in_cli():
    """Verify that the sprint command is registered in the CLI."""
    import sys
    from unittest.mock import MagicMock
    sys.modules["rank_bm25"] = MagicMock()
    from onecoder.cli import cli
    assert "sprint" in cli.commands
    
def test_ai_sprint_telemetry_import():
     """Verify telemetry module is accessible (used in onecoder/commands/issue.py)."""
     try:
         from ai_sprint.telemetry import FailureModeCapture
         assert FailureModeCapture is not None
     except ImportError:
         pytest.fail("ai_sprint.telemetry could not be imported")
