"""Validation functions for pre-flight checks."""

import re
import shutil
import subprocess
from typing import Optional, Tuple


def check_docker_running() -> bool:
    """Check if Docker Desktop is running.

    Returns:
        True if Docker is running, False otherwise
    """
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, timeout=5, check=False
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_ssh_agent() -> Tuple[bool, bool]:
    """Check if SSH agent is running and has keys loaded.

    Returns:
        Tuple of (agent_running, keys_loaded)
    """
    try:
        result = subprocess.run(
            ["ssh-add", "-l"], capture_output=True, text=True, check=False
        )
        # Return code 0 = keys loaded
        # Return code 1 = agent running but no keys
        # Return code 2 = agent not running
        agent_running = result.returncode in (0, 1)
        keys_loaded = result.returncode == 0
        return agent_running, keys_loaded
    except FileNotFoundError:
        return False, False


def check_vscode_installed() -> bool:
    """Check if VS Code is installed.

    Returns:
        True if 'code' command is available, False otherwise
    """
    return shutil.which("code") is not None


def run_preflight_checks() -> list[str]:
    """Run pre-flight checks and return list of errors.

    Returns:
        List of error messages (empty if all checks pass)
    """
    errors = []

    if not check_docker_running():
        errors.append(
            "Docker Desktop is not running. Please start Docker Desktop and try again."
        )

    agent_running, keys_loaded = check_ssh_agent()
    if not agent_running:
        errors.append(
            "SSH agent is not running. Start it with: eval $(ssh-agent -s)"
        )
    elif not keys_loaded:
        errors.append("No SSH keys loaded in agent. Add keys with: ssh-add ~/.ssh/id_rsa")

    return errors


def validate_python_version(version: str) -> Optional[str]:
    """Validate Python version string.

    Args:
        version: Python version string (e.g., "3.11", "3.12")

    Returns:
        None if valid, error message if invalid
    """
    # Check format (should be X.Y or X.Y.Z)
    if not re.match(r"^\d+\.\d+(\.\d+)?$", version):
        return f"Invalid Python version format: {version}. Expected format: X.Y or X.Y.Z (e.g., 3.11)"

    # Parse major.minor version
    parts = version.split(".")
    major = int(parts[0])
    minor = int(parts[1])

    # Check version range (3.9 - 3.13 supported)
    if major != 3:
        return f"Python {major}.x is not supported. Only Python 3.x versions are supported."

    if minor < 9:
        return f"Python 3.{minor} is too old. Minimum supported version is 3.9."

    if minor > 13:
        return f"Python 3.{minor} is not yet supported. Maximum supported version is 3.13."

    return None


def validate_node_version(version: str) -> Optional[str]:
    """Validate Node.js version string.

    Args:
        version: Node.js version string (e.g., "18", "20")

    Returns:
        None if valid, error message if invalid
    """
    # Check format (should be a number)
    if not version.isdigit():
        return f"Invalid Node.js version format: {version}. Expected a number (e.g., 18, 20)"

    version_num = int(version)

    # Check version range (18-22 supported - LTS versions)
    if version_num < 18:
        return f"Node.js {version_num} is too old. Minimum supported version is 18 (LTS)."

    if version_num > 22:
        return f"Node.js {version_num} is not yet supported. Maximum supported version is 22."

    # Warn about non-LTS versions (18, 20, 22 are LTS as of 2024)
    if version_num not in (18, 20, 22):
        return None  # Accept but don't error

    return None


def validate_claude_version(version: str) -> Optional[str]:
    """Validate Claude Code version string.

    Args:
        version: Claude Code version string (e.g., "latest", "1.0.0")

    Returns:
        None if valid, error message if invalid
    """
    if version == "latest":
        return None

    # Check semver format
    if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$", version):
        return (
            f"Invalid Claude Code version format: {version}. "
            "Expected 'latest' or semver format (e.g., 1.0.0)"
        )

    return None
