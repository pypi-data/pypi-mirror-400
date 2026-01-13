import yaml
import os
import re

class ProbLLMGuardian:
    """
    Enforces governance policies to prevent ProbLLM vulnerabilities (Prompt Injection,
    Automatic Tool Invocation, Data Exfiltration).
    """

    def __init__(self, governance_path="governance.yaml"):
        self.governance_path = governance_path
        self.policy = self._load_policy()

    def _load_policy(self):
        """Loads the governance policy from yaml."""
        if not os.path.exists(self.governance_path):
            return {}

        try:
            with open(self.governance_path, "r") as f:
                data = yaml.safe_load(f)
                return data.get("probllm_prevention", {})
        except Exception:
            return {}

    def is_enabled(self):
        """Checks if ProbLLM prevention is enabled."""
        return self.policy.get("enabled", False)

    def validate_tool_execution(self, tool_name: str, args: dict):
        """
        Validates whether a tool execution is safe based on the policy.
        Returns (is_safe, message).
        """
        if not self.is_enabled():
            return True, "Policy disabled"

        # 1. Check for High-Risk Tools requiring Confirmation
        restricted_tools = self.policy.get("require_human_confirmation_for_tools", [])
        if tool_name in restricted_tools:
            # In a real CLI, we would prompt here.
            # For now, we return a warning status that the caller must handle (e.g., prompt user).
            return False, f"Tool '{tool_name}' is restricted and requires Human Confirmation."

        # 2. Check for Secret Exposure in Args (Input Sanitization)
        # (Simplified check: looks for env var patterns like $SECRET or generic key patterns)
        if self.policy.get("block_secret_exposure", True):
            if self._contains_secrets(str(args)):
                return False, "Tool arguments appear to contain secrets or environment variables."

        return True, "Safe"

    def validate_output(self, output: str):
        """
        Scans LLM or Tool output for leaked secrets.
        """
        if not self.is_enabled():
            return True, "Policy disabled"

        if self.policy.get("block_secret_exposure", True):
            if self._contains_secrets(output):
                 return False, "Output blocked: Potential secret leakage detected."

        return True, "Safe"

    def _contains_secrets(self, text: str) -> bool:
        """
        Heuristic check for secrets.
        """
        # 1. Check for common API Key patterns (simplified)
        # Starts with sk-, gh-, etc. followed by alphanumeric
        patterns = [
            r"sk-[a-zA-Z0-9]{20,}", # OpenAI/Stripe style
            r"gh[pousr]-[a-zA-Z0-9]{20,}", # GitHub tokens
            r"xox[baprs]-[a-zA-Z0-9]{10,}", # Slack tokens
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                return True

        # 2. Check if any known environment variable values are present
        # (Be careful not to block common words if an env var is common)
        sensitive_keys = ["API_KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIALS"]
        for key, value in os.environ.items():
            if any(s in key for s in sensitive_keys) and len(value) > 8: # Only check long secrets
                if value in text:
                    return True

        return False
