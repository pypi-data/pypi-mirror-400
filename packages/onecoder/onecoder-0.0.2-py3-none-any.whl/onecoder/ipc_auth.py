import os
import socket
import uuid
import secrets
import asyncio
import time
from typing import Dict, Optional


class TokenStore:
    """Manages session-based tokens with TTL for API authentication."""

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize token store.

        Args:
            ttl_seconds: Time-to-live for tokens in seconds (default: 1 hour)
        """
        self._tokens: Dict[str, float] = {}  # token -> expiry_timestamp
        self.ttl_seconds = ttl_seconds

    def generate_token(self) -> str:
        """Generate a new session token with TTL."""
        token = secrets.token_urlsafe(32)
        expiry = time.time() + self.ttl_seconds
        self._tokens[token] = expiry
        return token

    def validate_token(self, token: str) -> bool:
        """
        Validates a token without consuming it (session-based).

        Args:
            token: The token to validate

        Returns:
            True if token exists and hasn't expired, False otherwise
        """
        if token not in self._tokens:
            return False

        # Check if token has expired
        if time.time() > self._tokens[token]:
            # Clean up expired token
            del self._tokens[token]
            return False

        return True

    def cleanup_expired(self) -> int:
        """
        Remove expired tokens from the store.

        Returns:
            Number of tokens cleaned up
        """
        current_time = time.time()
        expired_tokens = [
            token for token, expiry in self._tokens.items() if current_time > expiry
        ]

        for token in expired_tokens:
            del self._tokens[token]

        return len(expired_tokens)

    def revoke_token(self, token: str) -> bool:
        """
        Manually revoke a token.

        Args:
            token: The token to revoke

        Returns:
            True if token was revoked, False if it didn't exist
        """
        if token in self._tokens:
            del self._tokens[token]
            return True
        return False


# Global store for the running process
TOKEN_STORE = TokenStore()


class IPCAuthServer:
    """
    A Unix Domain Socket server that vends one-time tokens to local clients.
    This ensures that only processes with access to the socket (local users)
    can obtain authorization to hit the agent API.
    """

    def __init__(self, socket_path: str = "/tmp/onecoder_auth.sock"):
        self.socket_path = socket_path

    async def start(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        server = await asyncio.start_unix_server(self.handle_client, self.socket_path)

        # Ensure only the current user can read/write to the socket
        os.chmod(self.socket_path, 0o600)

        print(f"IPC Auth Server started on {self.socket_path}")

        # Start periodic cleanup task
        cleanup_task = asyncio.create_task(self._periodic_cleanup())

        async with server:
            try:
                await server.serve_forever()
            finally:
                cleanup_task.cancel()

    async def _periodic_cleanup(self):
        """Periodically clean up expired tokens (every 5 minutes)."""
        while True:
            await asyncio.sleep(300)  # 5 minutes
            cleaned = TOKEN_STORE.cleanup_expired()
            if cleaned > 0:
                print(f"Cleaned up {cleaned} expired tokens")

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """
        Handles token requests from local UI launchers.
        Protocol:
        - Client sends: "REQUEST_TOKEN\n"
        - Server replies: "<token>\n"
        """
        data = await reader.readline()
        message = data.decode().strip()

        if message == "REQUEST_TOKEN":
            token = TOKEN_STORE.generate_token()
            writer.write(f"{token}\n".encode())
            await writer.drain()

        writer.close()
        await writer.wait_closed()


async def get_token_from_ipc(
    socket_path: str = "/tmp/onecoder_auth.sock",
) -> Optional[str]:
    """Client utility to fetch a token via the IPC socket."""
    try:
        reader, writer = await asyncio.open_unix_connection(socket_path)
        writer.write(b"REQUEST_TOKEN\n")
        await writer.drain()

        data = await reader.readline()
        token = data.decode().strip()

        writer.close()
        await writer.wait_closed()
        return token
    except Exception as e:
        print(f"Error fetching token from IPC: {e}")
        return None


if __name__ == "__main__":
    # Test execution
    async def main():
        server = IPCAuthServer()
        # Run server in background
        server_task = asyncio.create_task(server.start())
        await asyncio.sleep(1)  # Wait for startup

        # Simulate client
        token = await get_token_from_ipc()
        if token:
            print(f"Client fetched token: {token}")

            # Validate (should work - session-based)
            is_valid = TOKEN_STORE.validate_token(token)
            print(f"Token is valid: {is_valid}")

            # Validate again (should still work - not consumed)
            is_valid_again = TOKEN_STORE.validate_token(token)
            print(f"Token is still valid after first check: {is_valid_again}")

            # Revoke token
            revoked = TOKEN_STORE.revoke_token(token)
            print(f"Token revoked: {revoked}")

            # Validate after revocation (should fail)
            is_valid_after_revoke = TOKEN_STORE.validate_token(token)
            print(f"Token valid after revocation: {is_valid_after_revoke}")
        else:
            print("Failed to fetch token from IPC")

        server_task.cancel()

    asyncio.run(main())
