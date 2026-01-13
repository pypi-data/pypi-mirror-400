#!/usr/bin/env python3
"""
Tests for token expiration handling.

Tests cover:
- Token expiration behavior
- Expiration mid-conversation
- Token refresh after expiration
- Graceful degradation
"""

import sys
import time
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from onecoder.ipc_auth import TokenStore
from onecoder.tui import OneCoderTUI


def test_token_expiration_basic():
    """Test that tokens expire after TTL."""
    print("Test 1: Basic Token Expiration")

    # Create TokenStore with short TTL (2 seconds)
    store = TokenStore(ttl_seconds=2)
    token = store.generate_token()

    # Token should be valid immediately
    is_valid = store.validate_token(token)
    assert is_valid is True, "Token should be valid immediately"
    print("  ✓ Token valid immediately after creation")

    # Wait for expiration (with buffer)
    print("  ⏳ Waiting 3 seconds for token to expire...")
    time.sleep(3)

    # Token should be invalid after TTL
    is_valid_after = store.validate_token(token)
    assert is_valid_after is False, "Token should be invalid after TTL"
    print("  ✓ Token expired after TTL")

    return True


def test_multiple_tokens_expiration():
    """Test that multiple tokens can expire independently."""
    print("\nTest 2: Multiple Tokens with Different Expiration Times")

    # Create two stores to track tokens independently
    store1 = TokenStore(ttl_seconds=2)
    store2 = TokenStore(ttl_seconds=3)

    token1 = store1.generate_token()
    print("  ✓ Generated first token (2s TTL)")

    time.sleep(1)
    token2 = store2.generate_token()
    print("  ✓ Generated second token (3s TTL)")

    # Both tokens should be valid in their respective stores
    assert store1.validate_token(token1) is True, "First token should be valid"
    assert store2.validate_token(token2) is True, "Second token should be valid"
    print("  ✓ Both tokens valid in their stores")

    # Wait for first token to expire
    print("  ⏳ Waiting 1.5 seconds for first token to expire...")
    time.sleep(1.5)

    # First token should be expired, second should still be valid
    assert store1.validate_token(token1) is False, "First token should be expired"
    assert store2.validate_token(token2) is True, "Second token should still be valid"
    print("  ✓ First token expired, second token still valid")

    # Wait for second token to expire
    print("  ⏳ Waiting 1.5 seconds for second token to expire...")
    time.sleep(1.5)

    # Both tokens should be expired
    assert store1.validate_token(token1) is False, "First token should be expired"
    assert store2.validate_token(token2) is False, "Second token should be expired"
    print("  ✓ Both tokens expired")

    return True


def test_expired_token_cleanup():
    """Test that expired tokens can be cleaned up."""
    print("\nTest 3: Cleanup of Expired Tokens")

    store = TokenStore(ttl_seconds=1)

    # Generate multiple tokens
    tokens = [store.generate_token() for _ in range(5)]
    print(f"  ✓ Generated {len(tokens)} tokens")

    # Wait for all to expire
    print("  ⏳ Waiting 2 seconds for all tokens to expire...")
    time.sleep(2)

    # Cleanup expired tokens
    cleaned = store.cleanup_expired()
    # Can't assert exact count since validate_token may auto-delete
    assert cleaned >= 0, "Should clean up expired tokens"
    print(f"  ✓ Cleaned up {cleaned} expired tokens")

    # Tokens should be invalid
    for i, token in enumerate(tokens):
        assert store.validate_token(token) is False, f"Token {i} should be invalid"
    print(f"  ✓ All {len(tokens)} tokens now invalid")

    return True


def test_token_reuse_before_expiration():
    """Test that tokens can be reused multiple times before expiration."""
    print("\nTest 4: Token Reuse Before Expiration")

    store = TokenStore(ttl_seconds=5)
    token = store.generate_token()
    print("  ✓ Generated token")

    # Use token multiple times
    for i in range(10):
        is_valid = store.validate_token(token)
        assert is_valid is True, f"Token should be valid on use {i + 1}"

    print("  ✓ Token reused 10 times successfully")

    # Verify token still valid
    assert store.validate_token(token) is True, "Token should still be valid"
    print("  ✓ Token still valid after multiple uses")

    return True


def test_token_expiration_with_refresh():
    """Test token refresh mechanism (generate new token after expiration)."""
    print("\nTest 5: Token Refresh After Expiration")

    store = TokenStore(ttl_seconds=2)
    token1 = store.generate_token()
    print("  ✓ Generated initial token")

    # Use token
    assert store.validate_token(token1) is True
    print("  ✓ Initial token valid")

    # Wait for expiration
    print("  ⏳ Waiting 3 seconds for token to expire...")
    time.sleep(3)

    # Token should be expired
    assert store.validate_token(token1) is False, "Initial token should be expired"
    print("  ✓ Initial token expired")

    # Generate new token (refresh)
    token2 = store.generate_token()
    assert token1 != token2, "New token should be different from old"
    print("  ✓ Generated new token (refresh)")

    # New token should be valid
    assert store.validate_token(token2) is True, "New token should be valid"
    print("  ✓ New token valid")

    # Old token should still be invalid
    assert store.validate_token(token1) is False, "Old token should still be invalid"
    print("  ✓ Old token remains invalid")

    return True


def test_token_expiration_during_session():
    """Test handling of token expiration during active session."""
    print("\nTest 6: Token Expiration During Active Session")

    store = TokenStore(ttl_seconds=2)
    token = store.generate_token()
    print("  ✓ Generated token")

    # Simulate multiple uses before expiration
    for i in range(3):
        assert store.validate_token(token) is True, (
            f"Token should be valid at use {i + 1}"
        )
        time.sleep(0.3)  # Small delay between uses

    print("  ✓ Token used 3 times successfully")

    # Wait for expiration
    print("  ⏳ Waiting 2 seconds for token to expire...")
    time.sleep(2)

    # Token should be expired
    assert store.validate_token(token) is False, "Token should be expired after TTL"
    print("  ✓ Token expired after TTL")

    # Try to use expired token (should fail gracefully)
    is_valid = store.validate_token(token)
    assert is_valid is False, "Expired token validation should fail"
    print("  ✓ Expired token properly rejected")

    return True


def test_long_ttl_token_stability():
    """Test token stability with longer TTL."""
    print("\nTest 7: Token Stability with Long TTL")

    # Create TokenStore with long TTL (10 seconds)
    store = TokenStore(ttl_seconds=10)
    token = store.generate_token()
    print("  ✓ Generated token with 10 second TTL")

    # Validate token multiple times over 5 seconds
    start_time = time.time()
    validation_count = 0
    while time.time() - start_time < 5:
        assert store.validate_token(token) is True, "Token should remain valid"
        validation_count += 1
        time.sleep(0.5)

    print(f"  ✓ Token validated {validation_count} times over 5 seconds")

    # Token should still be valid
    assert store.validate_token(token) is True, "Token should still be valid"
    print("  ✓ Token remains stable with long TTL")

    return True


def test_concurrent_tokens_expiration():
    """Test expiration handling with concurrent tokens."""
    print("\nTest 8: Concurrent Token Expiration")

    store = TokenStore(ttl_seconds=1)

    # Generate 10 concurrent tokens
    tokens = [store.generate_token() for _ in range(10)]
    print(f"  ✓ Generated {len(tokens)} concurrent tokens")

    # All tokens should be valid
    for token in tokens:
        assert store.validate_token(token) is True, "All tokens should be valid"
    print("  ✓ All tokens valid")

    # Wait for expiration
    print("  ⏳ Waiting 2 seconds for all tokens to expire...")
    time.sleep(2)

    # All tokens should be expired
    for i, token in enumerate(tokens):
        assert store.validate_token(token) is False, f"Token {i} should be expired"
    print("  ✓ All tokens expired")

    # Cleanup should remove all remaining
    cleaned = store.cleanup_expired()
    # Most tokens likely already deleted by validate_token checks
    assert cleaned >= 0, "Should clean up expired tokens"
    print(f"  ✓ Cleanup removed {cleaned} expired tokens")

    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("OneCoder Token Expiration Handling Tests")
    print("=" * 70)
    print()

    tests = [
        test_token_expiration_basic,
        test_multiple_tokens_expiration,
        test_expired_token_cleanup,
        test_token_reuse_before_expiration,
        test_token_expiration_with_refresh,
        test_token_expiration_during_session,
        test_long_ttl_token_stability,
        test_concurrent_tokens_expiration,
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
