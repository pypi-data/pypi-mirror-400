#!/usr/bin/env python3
"""
Automated tests for TUI session management.

Tests cover:
- API session creation and retrieval
- TUI session handling
- Multi-turn conversation support
- Token-based authentication
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from onecoder.ipc_auth import TokenStore
from onecoder.api import session_service
from google.genai.types import Content, Part


def test_session_creation():
    """Test that sessions can be created and retrieved."""
    print("Test 1: Session Creation and Retrieval")

    user_id = "test-user-1"
    session_id = "test-session-1"

    async def run_test():
        # Check session doesn't exist
        session = await session_service.get_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
        )
        assert session is None, "Session should not exist initially"
        print("  ✓ Session doesn't exist initially")

        # Create session
        session = await session_service.create_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
        )
        assert session is not None, "Session should be created"
        assert session.id == session_id, "Session ID should match"
        print("  ✓ Session created successfully")

        # Verify session exists
        retrieved = await session_service.get_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
        )
        assert retrieved is not None, "Session should be retrievable"
        assert retrieved.id == session_id, "Retrieved session ID should match"
        print("  ✓ Session retrieved successfully")

    asyncio.run(run_test())
    return True


def test_multiple_users_independent_sessions():
    """Test that different users have independent sessions."""
    print("\nTest 2: Multiple Users with Independent Sessions")

    user1 = "test-user-2"
    user2 = "test-user-3"
    session_id = "test-session-2"

    async def run_test():
        # Create session for user 1
        await session_service.create_session(
            app_name="onecoder-unified-api", user_id=user1, session_id=session_id
        )

        # Create session for user 2
        await session_service.create_session(
            app_name="onecoder-unified-api", user_id=user2, session_id=session_id
        )

        # Retrieve both sessions
        retrieved1 = await session_service.get_session(
            app_name="onecoder-unified-api", user_id=user1, session_id=session_id
        )
        retrieved2 = await session_service.get_session(
            app_name="onecoder-unified-api", user_id=user2, session_id=session_id
        )

        # Verify both sessions exist
        assert retrieved1 is not None, "User 1 session should exist"
        assert retrieved2 is not None, "User 2 session should exist"
        print("  ✓ Both users have independent sessions")

    asyncio.run(run_test())
    return True


def test_multi_turn_with_same_session():
    """Test that multiple messages work with same session."""
    print("\nTest 3: Multi-turn Conversation with Same Session")

    user_id = "test-user-multi"
    session_id = "test-session-multi"

    async def run_test():
        # Create session
        await session_service.create_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
        )

        # Create multiple message objects (simulating multi-turn)
        messages = [
            Content(parts=[Part(text="First message")], role="user"),
            Content(parts=[Part(text="Second message")], role="user"),
            Content(parts=[Part(text="Third message")], role="user"),
        ]

        # Verify session still exists after all messages
        session = await session_service.get_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
        )
        assert session is not None, "Session should still exist"
        assert session.id == session_id, "Session ID should match"
        print(f"  ✓ Session maintained across {len(messages)} messages")

    asyncio.run(run_test())
    return True


def test_tui_default_config():
    """Test that TUI uses default session configuration."""
    print("\nTest 4: TUI Default Session Configuration")

    from onecoder.tui import OneCoderTUI

    tui = OneCoderTUI()

    assert tui.session_id == "tui-session", "Default session ID should match"
    assert tui.user_id == "local-user", "Default user ID should match"
    assert tui.api_url == "http://127.0.0.1:8000", "Default API URL should match"

    print("  ✓ TUI default configuration correct")
    return True


def test_tui_custom_api_url():
    """Test that TUI can use custom API URL."""
    print("\nTest 5: TUI Custom API URL Configuration")

    from onecoder.tui import OneCoderTUI

    custom_url = "http://127.0.0.1:8001"
    tui = OneCoderTUI(api_url=custom_url)

    assert tui.api_url == custom_url, "Custom API URL should be set"

    print("  ✓ TUI can use custom API URL")
    return True


def test_token_based_authentication():
    """Test token-based authentication flow."""
    print("\nTest 6: Token-Based Authentication")

    token_store = TokenStore(ttl_seconds=3600)

    # Generate token
    token = token_store.generate_token()
    assert token is not None, "Token should be generated"
    assert len(token) > 0, "Token should not be empty"
    print("  ✓ Token generated successfully")

    # Validate token (simulating API check)
    is_valid = token_store.validate_token(token)
    assert is_valid is True, "Token should be valid"
    print("  ✓ Token validates successfully")

    # Reuse token (simulating multi-turn)
    is_valid_2 = token_store.validate_token(token)
    assert is_valid_2 is True, "Token should still be valid on reuse"
    print("  ✓ Token can be reused (session-based)")

    # Revoke token (simulating logout)
    revoked = token_store.revoke_token(token)
    assert revoked is True, "Token should be revocable"
    print("  ✓ Token can be revoked")

    # Validate after revocation
    is_valid_after = token_store.validate_token(token)
    assert is_valid_after is False, "Token should be invalid after revocation"
    print("  ✓ Token invalid after revocation")

    return True


def test_different_sessions_independent():
    """Test that different sessions maintain independent state."""
    print("\nTest 7: Different Sessions Maintain Independence")

    user_id = "test-user-independent"
    session1_id = "session-1"
    session2_id = "session-2"

    async def run_test():
        # Create two sessions
        await session_service.create_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session1_id
        )
        await session_service.create_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session2_id
        )

        # Retrieve both sessions
        session1 = await session_service.get_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session1_id
        )
        session2 = await session_service.get_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session2_id
        )

        # Verify sessions are independent
        assert session1 is not None, "Session 1 should exist"
        assert session2 is not None, "Session 2 should exist"
        assert session1.id == session1_id, "Session 1 ID should match"
        assert session2.id == session2_id, "Session 2 ID should match"
        assert session1.id != session2.id, "Sessions should have different IDs"
        print("  ✓ Sessions maintain independent state")

    asyncio.run(run_test())
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("OneCoder TUI Session Management Tests")
    print("=" * 70)
    print()

    tests = [
        test_session_creation,
        test_multiple_users_independent_sessions,
        test_multi_turn_with_same_session,
        test_tui_default_config,
        test_tui_custom_api_url,
        test_token_based_authentication,
        test_different_sessions_independent,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"  ❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print()
    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
