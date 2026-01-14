"""CLI entry point for whale-interactive-feedback."""

import subprocess
import sys
import os

from .downloader import ensure_binary, update_binary


def main():
    """Main entry point."""
    # Handle special commands
    if len(sys.argv) > 1:
        if sys.argv[1] == "--update":
            update_binary()
            return
        elif sys.argv[1] == "--version":
            from . import __version__
            from .downloader import get_installed_version
            print(f"whale-interactive-feedback (Python wrapper) v{__version__}")
            installed = get_installed_version()
            if installed:
                print(f"whale-ask-server (Rust binary) {installed}")
            return
        elif sys.argv[1] == "--help":
            print("whale-interactive-feedback - MCP server for interactive user feedback")
            print()
            print("Usage: whale-ask-server [OPTIONS]")
            print()
            print("Options:")
            print("  --version    Show version information")
            print("  --update     Update to latest binary version")
            print("  --help       Show this help message")
            print()
            print("This is a Python wrapper that downloads and runs the Rust binary.")
            print("The binary is cached at: ~/Library/Caches/whale-interactive-feedback/")
            return
    
    # Ensure binary is installed
    try:
        binary_path = ensure_binary()
    except Exception as e:
        print(f"Error: Failed to ensure binary: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the binary, passing through all arguments and stdio
    # This is critical for MCP protocol which uses stdin/stdout
    try:
        result = subprocess.run(
            [str(binary_path)] + sys.argv[1:],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error: Failed to run binary: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
