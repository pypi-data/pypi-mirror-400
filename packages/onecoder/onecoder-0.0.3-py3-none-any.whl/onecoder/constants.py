import os
from .config_manager import config_manager

# Default to Production API URL
ONECODER_API_URL = os.getenv("ONECODER_API_URL", "https://api.onecoder.dev")

# Production GitHub App Client ID
# This is safe to share as it is a public identifier, not a secret.
GITHUB_CLIENT_ID = config_manager.get_github_client_id()
