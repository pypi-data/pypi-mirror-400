#!/usr/bin/env python3
"""
Test script for OneCoder token lifecycle.
Tests session-based tokens with TTL.
"""

import sys
import time
import asyncio
from pathlib import Path

# Add parent directory to path to import onecoder modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from onecoder.ipc_auth import TokenStore

def test_token_generation():
    """Test that tokens are generated correctly."""
    print("Test 1: Token Generation")
    store = TokenStore(ttl_seconds=3600)
    token = store.generate_token()
    assert token is not None
    assert len(token) > 0
    print(f"  ✓ Generated token: {token[:16]}...")
    return store, token

def test_token_validation(store, token):
    """Test that tokens validate correctly."""
    print("\nTest 2: Token Validation")
    is_valid = store.validate_token(token)
    assert is_valid == True
    print(f"  ✓ Token is valid")

def test_token_reusability(store, token):
    """Test that tokens can be used multiple times (session-based)."""
    print("\nTest 3: Token Reusability (Session-Based)")
    # First validation
    is_valid_1 = store.validate_token(token)
    assert is_valid_1 == True
    print(f"  ✓ First validation: valid")
    
    # Second validation (should still work - not consumed)
    is_valid_2 = store.validate_token(token)
    assert is_valid_2 == True
    print(f"  ✓ Second validation: still valid (not consumed)")
    
    # Third validation
    is_valid_3 = store.validate_token(token)
    assert is_valid_3 == True
    print(f"  ✓ Third validation: still valid")

def test_token_expiry():
    """Test that tokens expire after TTL."""
    print("\nTest 4: Token Expiry")
    store = TokenStore(ttl_seconds=2)  # 2 second TTL for testing
    token = store.generate_token()
    
    # Should be valid immediately
    is_valid = store.validate_token(token)
    assert is_valid == True
    print(f"  ✓ Token valid immediately after creation")
    
    # Wait for expiry
    print(f"  ⏳ Waiting 3 seconds for token to expire...")
    time.sleep(3)
    
    # Should be invalid after TTL
    is_valid_after = store.validate_token(token)
    assert is_valid_after == False
    print(f"  ✓ Token expired after TTL")

def test_token_revocation(store, token):
    """Test manual token revocation."""
    print("\nTest 5: Token Revocation")
    # Token should be valid before revocation
    is_valid_before = store.validate_token(token)
    assert is_valid_before == True
    print(f"  ✓ Token valid before revocation")
    
    # Revoke token
    revoked = store.revoke_token(token)
    assert revoked == True
    print(f"  ✓ Token revoked successfully")
    
    # Token should be invalid after revocation
    is_valid_after = store.validate_token(token)
    assert is_valid_after == False
    print(f"  ✓ Token invalid after revocation")

def test_cleanup():
    """Test expired token cleanup."""
    print("\nTest 6: Expired Token Cleanup")
    store = TokenStore(ttl_seconds=1)
    
    # Generate multiple tokens
    token1 = store.generate_token()
    token2 = store.generate_token()
    token3 = store.generate_token()
    print(f"  ✓ Generated 3 tokens")
    
    # Wait for expiry
    print(f"  ⏳ Waiting 2 seconds for tokens to expire...")
    time.sleep(2)
    
    # Cleanup expired tokens
    cleaned = store.cleanup_expired()
    assert cleaned == 3
    print(f"  ✓ Cleaned up {cleaned} expired tokens")

def main():
    """Run all tests."""
    print("=" * 60)
    print("OneCoder Token Lifecycle Tests")
    print("=" * 60)
    
    try:
        # Run tests
        store, token = test_token_generation()
        test_token_validation(store, token)
        test_token_reusability(store, token)
        test_token_expiry()
        
        # Generate new token for revocation test (old one was revoked in reusability test)
        new_token = store.generate_token()
        test_token_revocation(store, new_token)
        
        test_cleanup()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
