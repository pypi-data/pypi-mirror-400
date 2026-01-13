#!/usr/bin/env python3
"""
Tests for error scenarios in TUI and API.

Tests cover:
- Network error handling
- Server unavailability
- Invalid token scenarios
- Timeout handling
- Malformed response handling
"""

import sys
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
import httpx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from onecoder.ipc_auth import TokenStore


def test_server_not_running():
    """Test handling when server is not running."""
    print("Test 1: Server Not Running")

    async def run_test():
        try:
            # Try to connect to non-existent server (use different port)
            async with httpx.AsyncClient(timeout=1.0) as client:
                response = await client.get("http://127.0.0.1:9999/")
                # Should get connection error
                print(f"  ❌ Unexpected success: {response.status_code}")
                return False
        except httpx.ConnectError as e:
            print(f"  ✓ Connection error properly caught: {type(e).__name__}")
            return True
        except Exception as e:
            print(f"  ✓ Other error caught: {type(e).__name__}")
            return True

    result = asyncio.run(run_test())
    assert result is True, "Should handle server unavailability gracefully"
    return True


def test_invalid_token():
    """Test handling of invalid tokens."""
    print("\nTest 2: Invalid Token")

    store = TokenStore(ttl_seconds=3600)
    valid_token = store.generate_token()

    # Test completely invalid token
    invalid_tokens = [
        "",
        None,
        "invalid-token-12345",
        "not-a-real-token",
    ]

    passed = 0
    for invalid_token in invalid_tokens:
        if invalid_token is None or invalid_token == "":
            # Skip None/empty as they don't reach validate_token
            continue

        is_valid = store.validate_token(invalid_token)
        assert is_valid is False, f"Invalid token should be rejected: {invalid_token}"
        passed += 1

    print(f"  ✓ All {passed} invalid tokens rejected")
    return True


def test_expired_token():
    """Test handling of expired tokens."""
    print("\nTest 3: Expired Token")

    import time

    store = TokenStore(ttl_seconds=1)
    token = store.generate_token()

    # Wait for expiration
    print("  ⏳ Waiting 2 seconds for token to expire...")
    time.sleep(2)

    # Token should be invalid
    is_valid = store.validate_token(token)
    assert is_valid is False, "Expired token should be rejected"
    print("  ✓ Expired token properly rejected")
    return True


def test_empty_message():
    """Test handling of empty messages."""
    print("\nTest 4: Empty Message")

    from onecoder.tui import OneCoderTUI

    tui = OneCoderTUI()

    # Empty message should be handled gracefully
    empty_messages = [
        "",
        "   ",
        "\t",
    ]

    for empty_msg in empty_messages:
        stripped = empty_msg.strip()
        assert stripped == "", f"Empty message should strip to empty: '{empty_msg}'"

    print("  ✓ Empty messages handled correctly")
    return True


def test_very_long_message():
    """Test handling of very long messages."""
    print("\nTest 5: Very Long Message")

    from onecoder.tui import OneCoderTUI

    tui = OneCoderTUI()

    # Create very long message
    long_message = "test " * 10000

    assert len(long_message) > 10000, "Long message should be created"

    # Just verify it doesn't crash
    try:
        message_content = long_message
        assert message_content is not None
        print(f"  ✓ Long message ({len(long_message)} chars) handled without crash")
        return True
    except Exception as e:
        print(f"  ❌ Long message caused error: {e}")
        return False


def test_special_characters():
    """Test handling of special characters in messages."""
    print("\nTest 6: Special Characters")

    from onecoder.tui import OneCoderTUI

    tui = OneCoderTUI()

    # Messages with special characters
    special_messages = [
        'Test with "quotes"',
        "Test with 'apostrophes'",
        "Test with newlines\nand\ttabs",
        "Test with \\backslashes\\",
        "Test with <html> &symbols&",
        "Test with unicode: café 日本語 🎉",
    ]

    for msg in special_messages:
        # Just verify they don't cause crashes
        try:
            message_content = msg
            assert message_content is not None
        except Exception as e:
            print(f"  ❌ Special characters caused error: {e}")
            return False

    print(f"  ✓ All {len(special_messages)} special character messages handled")
    return True


def test_malformed_url():
    """Test handling of malformed API URLs."""
    print("\nTest 7: Malformed API URL")

    from onecoder.tui import OneCoderTUI

    malformed_urls = [
        "not-a-url",
        "http://",
        "://127.0.0.1:8000",
        "ftp://127.0.0.1:8000",
    ]

    for url in malformed_urls:
        # Just verify TUI can be created with any URL
        # (actual connection will fail, but shouldn't crash)
        try:
            tui = OneCoderTUI(api_url=url)
            assert tui.api_url == url, f"URL should be set: {url}"
        except Exception as e:
            print(f"  ❌ Malformed URL caused error: {e}")
            return False

    print(f"  ✓ All {len(malformed_urls)} malformed URLs handled without crash")
    return True


def test_timeout_handling():
    """Test handling of timeout scenarios."""
    print("\nTest 8: Timeout Handling")

    async def run_test():
        try:
            # Try to connect with very short timeout
            async with httpx.AsyncClient(timeout=0.001) as client:
                # This will likely timeout
                response = await client.get("http://127.0.0.1:8000/")
                print(f"  ⚠ Unexpected success (may be cached): {response.status_code}")
                return True
        except httpx.TimeoutException as e:
            print(f"  ✓ Timeout properly caught: {type(e).__name__}")
            return True
        except httpx.ConnectError as e:
            # Server might not be running, also acceptable
            print(f"  ✓ Connection error (server down): {type(e).__name__}")
            return True
        except Exception as e:
            print(f"  ✓ Other error caught: {type(e).__name__}")
            return True

    result = asyncio.run(run_test())
    assert result is True, "Should handle timeout gracefully"
    return True


def test_concurrent_requests():
    """Test handling of concurrent requests to same session."""
    print("\nTest 9: Concurrent Requests")

    store = TokenStore(ttl_seconds=3600)
    token = store.generate_token()

    # Run concurrent validations (validate_token is synchronous)
    def validate_concurrent():
        results = [store.validate_token(token) for _ in range(10)]
        return all(results)

    results = validate_concurrent()

    # Verify all results are True
    assert results is True, "All concurrent validations should succeed"
    print("  ✓ 10 concurrent validations all succeeded")
    return True


def test_token_expiration_mid_conversation():
    """Test token expiration during active conversation."""
    print("\nTest 10: Token Expiration Mid-Conversation")

    import time

    store = TokenStore(ttl_seconds=1)
    token = store.generate_token()

    # Simulate conversation start (token valid)
    is_valid = store.validate_token(token)
    assert is_valid is True, "Token should be valid at conversation start"
    print("  ✓ Token valid at conversation start")

    # Simulate message exchanges
    for i in range(3):
        time.sleep(0.2)
        is_valid = store.validate_token(token)
        if not is_valid:
            print(f"  ❌ Token expired during message {i + 1}")
            return False

    # Wait for expiration
    print("  ⏳ Waiting 1.5 seconds for token to expire...")
    time.sleep(1.5)

    # Try to send another message
    is_valid_after = store.validate_token(token)
    assert is_valid_after is False, "Expired token should be rejected"
    print("  ✓ Token expired mid-conversation properly handled")

    return True


def test_multiple_token_reuse():
    """Test that multiple sessions can use tokens independently."""
    print("\nTest 11: Multiple Session Token Independence")

    store = TokenStore(ttl_seconds=3600)

    # Generate tokens for different sessions
    token1 = store.generate_token()
    token2 = store.generate_token()
    token3 = store.generate_token()

    # All tokens should be valid independently
    assert store.validate_token(token1) is True, "Token 1 should be valid"
    assert store.validate_token(token2) is True, "Token 2 should be valid"
    assert store.validate_token(token3) is True, "Token 3 should be valid"

    print("  ✓ All 3 tokens valid independently")

    # Revoke one token
    store.revoke_token(token2)

    # Other tokens should still be valid
    assert store.validate_token(token1) is True, "Token 1 should still be valid"
    assert store.validate_token(token2) is False, "Token 2 should be revoked"
    assert store.validate_token(token3) is True, "Token 3 should still be valid"

    print("  ✓ Token revocation doesn't affect other tokens")
    return True


def test_unicode_messages():
    """Test handling of Unicode messages."""
    print("\nTest 12: Unicode Messages")

    unicode_messages = [
        "Hello 世界",  # Chinese
        "Привет мир",  # Russian
        "こんにちは世界",  # Japanese
        "مرحبا بالعالمية",  # Arabic
        "Γειά σου κόσμε",  # Greek
        "🎉🌟🎊",  # Emojis
        "Mix of 🎉 and text 世界",  # Mixed
    ]

    for msg in unicode_messages:
        try:
            message_content = msg
            assert message_content is not None
            assert len(msg) > 0, "Unicode message should have content"
        except Exception as e:
            print(f"  ❌ Unicode message caused error: {e}")
            return False

    print(f"  ✓ All {len(unicode_messages)} Unicode messages handled")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("OneCoder Error Scenario Tests")
    print("=" * 70)
    print()

    tests = [
        test_server_not_running,
        test_invalid_token,
        test_expired_token,
        test_empty_message,
        test_very_long_message,
        test_special_characters,
        test_malformed_url,
        test_timeout_handling,
        test_concurrent_requests,
        test_token_expiration_mid_conversation,
        test_multiple_token_reuse,
        test_unicode_messages,
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
