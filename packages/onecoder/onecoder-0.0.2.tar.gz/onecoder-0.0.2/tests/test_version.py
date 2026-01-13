"""Tests for onecoder CLI version flag."""
import subprocess
import re


def test_version_flag_exists():
    """Test that --version flag is recognized."""
    result = subprocess.run(
        ["uv", "run", "onecoder", "--version"],
        capture_output=True,
        text=True,
        cwd="/Users/unblockd/devbox/coding-platform/platform/onecoder-cli"
    )
    assert result.returncode == 0, f"Command failed with: {result.stderr}"


def test_version_output_format():
    """Test that version output matches expected format."""
    result = subprocess.run(
        ["uv", "run", "onecoder", "--version"],
        capture_output=True,
        text=True,
        cwd="/Users/unblockd/devbox/coding-platform/platform/onecoder-cli"
    )
    output = result.stdout.strip()
    
    # Expected format: "onecoder, version X.Y.Z"
    pattern = r"onecoder, version \d+\.\d+\.\d+"
    assert re.match(pattern, output), f"Unexpected version format: {output}"


def test_version_matches_pyproject():
    """Test that version matches pyproject.toml."""
    result = subprocess.run(
        ["uv", "run", "onecoder", "--version"],
        capture_output=True,
        text=True,
        cwd="/Users/unblockd/devbox/coding-platform/platform/onecoder-cli"
    )
    output = result.stdout.strip()
    
    # Extract version from output
    version_match = re.search(r"version (\d+\.\d+\.\d+)", output)
    assert version_match, f"Could not extract version from: {output}"
    
    cli_version = version_match.group(1)
    
    # Expected version from pyproject.toml
    expected_version = "0.1.0"
    assert cli_version == expected_version, \
        f"Version mismatch: CLI reports {cli_version}, expected {expected_version}"
