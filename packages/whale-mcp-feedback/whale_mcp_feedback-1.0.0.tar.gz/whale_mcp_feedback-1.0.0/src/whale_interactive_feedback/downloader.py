"""Download and manage the Rust binary."""

import os
import stat
import sys
import tarfile
import tempfile
from pathlib import Path

import httpx
from platformdirs import user_cache_dir

from .config import (
    GITHUB_OWNER,
    GITHUB_REPO,
    BINARY_NAME,
    get_platform_key,
    get_binary_filename,
)


def get_cache_dir() -> Path:
    """Get the cache directory for storing the binary."""
    cache_dir = Path(user_cache_dir("whale-interactive-feedback"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_binary_path() -> Path:
    """Get the path to the binary."""
    return get_cache_dir() / get_binary_filename()


def get_version_file() -> Path:
    """Get the path to the version file."""
    return get_cache_dir() / "version.txt"


def get_latest_version() -> str:
    """Get the latest version from GitHub releases."""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        return data["tag_name"]


def get_installed_version() -> str | None:
    """Get the currently installed version."""
    version_file = get_version_file()
    if version_file.exists():
        return version_file.read_text().strip()
    return None


def download_binary(version: str) -> Path:
    """Download the binary for the current platform."""
    platform_key = get_platform_key()
    filename = f"{BINARY_NAME}-{version}-{platform_key}.tar.gz"
    url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/download/{version}/{filename}"
    
    print(f"Downloading {filename}...", file=sys.stderr)
    
    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        
        # Save to temp file and extract
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
    
    try:
        # Extract the binary
        cache_dir = get_cache_dir()
        with tarfile.open(tmp_path, "r:gz") as tar:
            tar.extractall(cache_dir)
        
        # Set executable permission
        binary_path = get_binary_path()
        if binary_path.exists():
            os.chmod(binary_path, os.stat(binary_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            # Remove macOS quarantine attributes to avoid Gatekeeper issues
            import platform
            if platform.system() == "Darwin":
                import subprocess
                try:
                    subprocess.run(
                        ["xattr", "-cr", str(binary_path)],
                        capture_output=True,
                        check=False
                    )
                    # Also clear attributes on the app binary if it exists
                    app_path = cache_dir / "app"
                    if app_path.exists():
                        subprocess.run(
                            ["xattr", "-cr", str(app_path)],
                            capture_output=True,
                            check=False
                        )
                except Exception:
                    pass  # Ignore errors, xattr might not be available
        
        # Save version
        get_version_file().write_text(version)
        
        print(f"Successfully installed {BINARY_NAME} {version}", file=sys.stderr)
        return binary_path
    finally:
        # Cleanup temp file
        os.unlink(tmp_path)


def ensure_binary() -> Path:
    """Ensure the binary is installed and up to date."""
    binary_path = get_binary_path()
    
    # Check if binary exists
    if not binary_path.exists():
        print(f"{BINARY_NAME} not found, downloading...")
        version = get_latest_version()
        return download_binary(version)
    
    # Binary exists, optionally check for updates
    # For now, just return the existing binary
    return binary_path


def update_binary() -> Path:
    """Force update the binary to the latest version."""
    version = get_latest_version()
    installed = get_installed_version()
    
    if installed == version:
        print(f"Already at latest version: {version}")
        return get_binary_path()
    
    print(f"Updating from {installed} to {version}...")
    return download_binary(version)
