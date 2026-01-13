import pytest
import os
import yaml
import re
from onecoder.governance.probllm import ProbLLMGuardian

@pytest.fixture
def temp_gov_file(tmp_path):
    gov_file = tmp_path / "governance.yaml"
    policy = {
        "probllm_prevention": {
            "enabled": True,
            "block_secret_exposure": True,
            "require_human_confirmation_for_tools": ["shell_execute_confirmed"],
            "banned_file_access": [".env", "secrets.yaml"],
            "banned_shell_commands": ["rm", "mv", "pkill"]
        }
    }
    with open(gov_file, "w") as f:
        yaml.dump(policy, f)
    return str(gov_file)

def test_probllm_enabled(temp_gov_file):
    guardian = ProbLLMGuardian(temp_gov_file)
    assert guardian.is_enabled() is True

def test_banned_file_access(temp_gov_file):
    guardian = ProbLLMGuardian(temp_gov_file)
    
    # Test .env access
    is_safe, message = guardian.validate_tool_execution("read_file", {"path": "/path/to/.env"})
    assert is_safe is False
    assert "banned file/pattern '.env'" in message

    # Test secrets.yaml access
    is_safe, message = guardian.validate_tool_execution("cat", {"args": "secrets.yaml"})
    assert is_safe is False
    assert "banned file/pattern 'secrets.yaml'" in message

    # Test safe file
    is_safe, message = guardian.validate_tool_execution("read_file", {"path": "README.md"})
    assert is_safe is True

def test_banned_shell_commands(temp_gov_file):
    guardian = ProbLLMGuardian(temp_gov_file)
    
    # Test rm
    is_safe, message = guardian.validate_tool_execution("shell_execute", {"command": "rm -rf /"})
    assert is_safe is False
    assert "Shell command 'rm' is banned" in message

    # Test rm with pipe
    is_safe, message = guardian.validate_tool_execution("shell_execute", {"command": "ls | rm"})
    assert is_safe is False
    assert "Shell command 'rm' is banned" in message

    # Test pkill after semicolon
    is_safe, message = guardian.validate_tool_execution("shell_execute", {"command": "ls; pkill -9 python"})
    assert is_safe is False
    assert "Shell command 'pkill' is banned" in message

    # Test safe command
    is_safe, message = guardian.validate_tool_execution("shell_execute", {"command": "ls -la"})
    assert is_safe is True

def test_secret_leakage_detection(temp_gov_file):
    guardian = ProbLLMGuardian(temp_gov_file)
    
    # Test OpenAI Key
    is_safe, message = guardian.validate_output("Here is my key: sk-U0987654321QWERTYUIOP")
    assert is_safe is False
    assert "Potential secret leakage detected" in message

    # Test Google Key
    is_safe, message = guardian.validate_output("AIzaSyB-1234567890-abcdefghij-klmnopqrs")
    assert is_safe is False

    # Test Safe output
    is_safe, message = guardian.validate_output("Analysis complete. No issues found.")
    assert is_safe is True

def test_policy_disabled(tmp_path):
    gov_file = tmp_path / "governance_disabled.yaml"
    policy = {"probllm_prevention": {"enabled": False}}
    with open(gov_file, "w") as f:
        yaml.dump(policy, f)
    
    guardian = ProbLLMGuardian(str(gov_file))
    assert guardian.is_enabled() is False
    
    # Everything should be safe when disabled
    is_safe, message = guardian.validate_tool_execution("shell_execute", {"command": "rm -rf /"})
    assert is_safe is True
