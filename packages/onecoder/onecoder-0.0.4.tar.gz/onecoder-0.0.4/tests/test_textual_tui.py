"""Tests for new Textual TUI."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from textual.widgets import RichLog, Input

from onecoder.tui.app import OneCoderApp


@pytest.mark.asyncio
async def test_app_initialization():
    """Test that OneCoderApp initializes correctly."""
    app = OneCoderApp(api_url="http://test:8000")

    assert app.api_url == "http://test:8000"
    assert app.session_id == "tui-session"
    assert app.user_id == "local-user"
    assert app.is_processing is False


@pytest.mark.asyncio
async def test_app_composition():
    """Test that app composes correctly with all widgets."""
    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        # Check that Header exists
        header = pilot.app.query_one("Header")
        assert header is not None

        # Check that RichLog exists
        chat_log = pilot.app.query_one("#chat-log", RichLog)
        assert chat_log is not None

        # Check that Input exists
        input_widget = pilot.app.query_one("#user-input", Input)
        assert input_widget is not None

        # Check that Footer exists
        footer = pilot.app.query_one("Footer")
        assert footer is not None


@pytest.mark.asyncio
async def test_keyboard_bindings():
    """Test that keyboard bindings are defined."""
    app = OneCoderApp(api_url="http://test:8000")

    expected_bindings = [
        ("ctrl+c", "quit"),
        ("ctrl+l", "clear_log"),
        ("ctrl+s", "toggle_theme"),
        ("ctrl+d", "toggle_dark"),
    ]

    actual_bindings = [(b.key, b.action) for b in app.BINDINGS]

    for expected in expected_bindings:
        assert expected in actual_bindings


@pytest.mark.asyncio
async def test_action_clear_log():
    """Test that clear_log action clears the chat log."""
    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        chat_log = pilot.app.query_one("#chat-log", RichLog)

        # Write some content
        chat_log.write("Test message")

        # Verify content exists
        assert len(chat_log.lines) > 0

        # Clear log
        await pilot.app.action_clear_log()

        # Verify log is cleared
        assert len(chat_log.lines) == 0


@pytest.mark.asyncio
async def test_theme_toggle():
    """Test that theme can be toggled."""
    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        initial_theme = pilot.app.theme

        await pilot.app.action_toggle_theme()

        assert pilot.app.theme != initial_theme


@pytest.mark.asyncio
@patch("onecoder.tui.app.get_token_from_ipc")
async def test_initialization_with_valid_token(mock_get_token):
    """Test app initialization with valid token."""
    mock_get_token.return_value = "test-token"

    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        await pilot.pause()

        assert app.token == "test-token"


@pytest.mark.asyncio
@patch("onecoder.tui.app.get_token_from_ipc")
async def test_initialization_without_token(mock_get_token):
    """Test app initialization without token shows error."""
    mock_get_token.return_value = None

    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        await pilot.pause()

        assert app.token is None
        # Error message should be in log


@pytest.mark.asyncio
@patch("onecoder.tui.app.get_token_from_ipc")
async def test_input_submission_with_quit(mock_get_token):
    """Test that 'quit' and 'exit' close the app."""
    mock_get_token.return_value = "test-token"

    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        await pilot.pause()
        input_widget = pilot.app.query_one("#user-input", Input)

        # Test 'quit'
        input_widget.value = "quit"
        await pilot.press("enter")

        # App should exit
        assert not pilot.app.is_running


@pytest.mark.asyncio
@patch("onecoder.tui.app.get_token_from_ipc")
async def test_input_submission_with_empty_message(mock_get_token):
    """Test that empty messages are ignored."""
    mock_get_token.return_value = "test-token"

    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        await pilot.pause()
        input_widget = pilot.app.query_one("#user-input", Input)

        # Submit empty message
        input_widget.value = "   "
        await pilot.press("enter")

        # Input should still be enabled
        assert not pilot.app.is_processing


@pytest.mark.asyncio
async def test_write_user_message():
    """Test that user messages are written correctly."""
    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        chat_log = pilot.app.query_one("#chat-log", RichLog)

        await pilot.app._write_user_message("Hello, OneCoder!")

        # Message should be in log
        assert len(chat_log.lines) > 0


@pytest.mark.asyncio
async def test_write_agent_message():
    """Test that agent messages are written correctly."""
    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        chat_log = pilot.app.query_one("#chat-log", RichLog)

        await pilot.app._write_agent_message("Hello, User!")

        # Message should be in log
        assert len(chat_log.lines) > 0


@pytest.mark.asyncio
async def test_show_tool_call():
    """Test that tool calls are displayed correctly."""
    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        chat_log = pilot.app.query_one("#chat-log", RichLog)

        # Test running status
        await pilot.app._show_tool_call("test_tool", {}, status="running")

        # Test success status
        await pilot.app._show_tool_call("test_tool", {}, status="success")

        # Test error status
        await pilot.app._show_tool_call("test_tool", {}, status="error")

        # All tool calls should be in log
        assert len(chat_log.lines) > 0


@pytest.mark.asyncio
async def test_write_error():
    """Test that error messages are written correctly."""
    app = OneCoderApp(api_url="http://test:8000")

    async with app.run_test() as pilot:
        chat_log = pilot.app.query_one("#chat-log", RichLog)

        await pilot.app._write_error("Test error message")

        # Error should be in log
        assert len(chat_log.lines) > 0
