"""Configuration for whale-interactive-feedback."""

import platform
import sys

# GitHub repository info
GITHUB_OWNER = "whalesea1314"
GITHUB_REPO = "whale-interactive-feedback"

# Binary name
BINARY_NAME = "whale-ask-server"

# Supported platforms
PLATFORMS = {
    ("Darwin", "arm64"): "macos-aarch64",
    ("Darwin", "x86_64"): "macos-x86_64",
    ("Linux", "x86_64"): "linux-x86_64",
    ("Windows", "AMD64"): "windows-x86_64",
}


def get_platform_key() -> str:
    """Get the platform key for the current system."""
    system = platform.system()
    machine = platform.machine()
    
    key = (system, machine)
    if key not in PLATFORMS:
        raise RuntimeError(
            f"Unsupported platform: {system} {machine}. "
            f"Supported platforms: {list(PLATFORMS.keys())}"
        )
    
    return PLATFORMS[key]


def get_binary_filename() -> str:
    """Get the binary filename for the current platform."""
    if platform.system() == "Windows":
        return f"{BINARY_NAME}.exe"
    return BINARY_NAME
