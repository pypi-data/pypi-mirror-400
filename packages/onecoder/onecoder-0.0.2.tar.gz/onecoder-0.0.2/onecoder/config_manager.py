import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".onecoder"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            # Set restrictive permissions
            os.chmod(self.config_dir, 0o700)

    def load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def save_config(self, config: Dict[str, Any]):
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            # Set restrictive permissions
            os.chmod(self.config_file, 0o600)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_token(self) -> Optional[str]:
        config = self.load_config()
        return config.get("api_token")

    def set_token(self, token: str):
        config = self.load_config()
        config["api_token"] = token
        self.save_config(config)

    def clear_token(self):
        config = self.load_config()
        if "api_token" in config:
            del config["api_token"]
            self.save_config(config)

    def get_user(self) -> Optional[Dict[str, Any]]:
        config = self.load_config()
        return config.get("user")

    def set_user(self, user: Dict[str, Any]):
        config = self.load_config()
        config["user"] = user
        self.save_config(config)

    def get_model_config(self) -> Optional[Dict[str, Any]]:
        config = self.load_config()
        return config.get("model")

    def set_model_config(self, model_config: Dict[str, Any]):
        config = self.load_config()
        config["model"] = model_config
        self.save_config(config)

    def get_github_client_id(self) -> str:
        """Get the GitHub Client ID from config or environment variable."""
        # Environment variable takes highest precedence
        env_id = os.getenv("GITHUB_CLIENT_ID")
        if env_id:
            return env_id
            
        config = self.load_config()
        # Return from config or the production default
        return config.get("github_client_id", "Iv23limfvipYiMLhjhq1")

    def set_github_client_id(self, client_id: str):
        """Set the GitHub Client ID in the config file."""
        config = self.load_config()
        config["github_client_id"] = client_id
        self.save_config(config)

config_manager = ConfigManager()
