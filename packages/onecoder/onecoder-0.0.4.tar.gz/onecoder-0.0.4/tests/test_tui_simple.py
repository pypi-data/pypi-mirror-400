#!/usr/bin/env python3
"""
Simple TUI test without complex inline code.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from onecoder.ipc_auth import get_token_from_ipc, TOKEN_STORE
from onecoder.tui import OneCoderTUI


async def test_tui():
    """Test TUI functionality."""
    print("Testing token generation...")
    token = await get_token_from_ipc()
    if token:
        is_valid = TOKEN_STORE.validate_token(token)
        print(f"✓ Token validation: {is_valid}")

        # Test TUI class instantiation
        tui = OneCoderTUI()
        print("✓ TUI class instantiated")

        # Test token refresh simulation
        tui.token = token
        print("✓ TUI token assignment successful")
    else:
        print("❌ TUI test failed: No token available")


if __name__ == "__main__":
    asyncio.run(test_tui())
