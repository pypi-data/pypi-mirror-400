# Whale Interactive Feedback

MCP server for interactive user feedback with GUI.

This is a Python wrapper that automatically downloads and runs the Rust binary.

## Installation

```bash
# Using uvx (recommended)
uvx whale-interactive-feedback

# Or install globally
pip install whale-interactive-feedback

# If you use SOCKS proxy, install with socks support
pip install "whale-interactive-feedback[socks]"
```

## MCP Configuration

Add to your MCP client configuration (Kiro, Cursor, Claude Desktop, Windsurf):

```json
{
  "mcpServers": {
    "whale-interactive-feedback": {
      "command": "uvx",
      "args": ["whale-interactive-feedback"]
    }
  }
}
```

## Commands

```bash
# Run the MCP server
whale-ask-server

# Check version
whale-ask-server --version

# Update to latest version
whale-ask-server --update
```

## Features

- 🐋 Interactive feedback collection via GUI popup
- 📎 File drag-and-drop support
- 🖼️ Image attachment support
- ⚡ Fast Rust binary with Python wrapper for easy installation
- 🔄 Auto-download and update

## License

MIT
