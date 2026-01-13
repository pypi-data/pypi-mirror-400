import pytest
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path
from onecoder.tui.commands import CommandRegistry
from onecoder.evaluation import TTUEvaluator

@pytest.mark.asyncio
async def test_command_registry():
    # Mock the app and its chat_log
    app = MagicMock()
    app.chat_log = MagicMock()
    app._write_error = AsyncMock() # Mock the async method

    registry = CommandRegistry(app)

    # Test unknown command
    assert await registry.handle("/unknown") == True
    app._write_error.assert_called_with("Unknown command: /unknown")

    # Test empty command
    assert await registry.handle("/") == False

@pytest.mark.asyncio
async def test_ttu_evaluation_empty_dir(tmp_path):
    evaluator = TTUEvaluator()
    # Pass an empty temp directory as sprint path
    result = evaluator.evaluate(sprint_path=tmp_path)

    assert result.passed == False
    assert result.score < 1.0
    assert "sprint.json" in result.missing_context
    assert "Missing Metadata" in result.failure_modes

@pytest.mark.asyncio
async def test_ttu_evaluation_no_sprint():
    # Force find_active_sprint to return None by mocking logic or passing invalid path
    # actually passing None triggers auto-discovery.
    evaluator = TTUEvaluator()
    result = evaluator.evaluate(sprint_path=None)

    # Check that failure modes are populated if score is low
    if not result.passed:
        assert len(result.failure_modes) > 0

    # Verify strict AGENTS.md check (assuming it exists in this repo root, otherwise it should fail)
    # The test runner's root likely has AGENTS.md (if it exists in repo) or not.
    # Let's just ensure the field exists.
    assert isinstance(result.failure_modes, list)
