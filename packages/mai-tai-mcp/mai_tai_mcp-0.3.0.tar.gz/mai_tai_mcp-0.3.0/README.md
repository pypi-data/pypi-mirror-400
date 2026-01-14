# mai-tai MCP Server

MCP (Model Context Protocol) server for mai-tai, enabling AI coding agents to communicate with humans through the mai-tai platform.

## Quick Start

### 1. Install with uv (recommended)

```bash
# One-time install (adds to PATH)
uv tool install mai-tai-mcp

# Or run directly without installing
uvx mai-tai-mcp
```

### 2. Alternative: Install with pipx

```bash
pipx install mai-tai-mcp
```

### 3. Development install

```bash
cd mcp-server
pip install -e .
```

## Configuration for Claude Desktop

Add this to `~/.config/claude/claude_desktop_config.json` (Mac/Linux) or the equivalent on Windows:

```json
{
  "mcpServers": {
    "mai-tai": {
      "command": "uvx",
      "args": ["mai-tai-mcp"],
      "env": {
        "MAI_TAI_API_URL": "https://api.mai-tai.dev",
        "MAI_TAI_API_KEY": "mt_your_api_key_here",
        "MAI_TAI_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

Then restart Claude Desktop.

## Configuration for Augment

Add to your Augment MCP settings:

```json
{
  "mcpServers": {
    "mai-tai": {
      "command": "uvx",
      "args": ["mai-tai-mcp"],
      "env": {
        "MAI_TAI_API_URL": "https://api.mai-tai.dev",
        "MAI_TAI_API_KEY": "mt_your_api_key_here",
        "MAI_TAI_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MAI_TAI_API_URL` | mai-tai backend URL | `https://api.mai-tai.dev` |
| `MAI_TAI_API_KEY` | API key from mai-tai project | `mt_xxx...` |
| `MAI_TAI_PROJECT_ID` | Your project ID | `df944ea7-...` |

All three variables are required. The server will fail fast with a clear error message if any are missing.

## Available Tools

### `ask_human`
Primary tool for escalating questions to humans. Use when you need:
- Information you don't have access to
- A decision or approval
- Clarification on requirements
- Help with an error you can't resolve

### `list_channels`
List all channels in the mai-tai project.

### `get_channel`
Get details about a specific channel.

### `send_message`
Send a message to a channel (non-blocking status updates).

### `get_messages`
Get messages from a channel.

### `get_project_info`
Get information about the connected mai-tai project.

> **Note:** Agents cannot create channels. Channels must be created by humans via the mai-tai web UI.

## Getting an API Key

1. Log in to mai-tai at https://mai-tai.dev
2. Go to your project settings
3. Create a new API key
4. Copy the key (it's only shown once)

## Testing

Test with MCP Inspector:

```bash
MAI_TAI_API_URL="http://localhost:8000" \
MAI_TAI_API_KEY="your-key" \
MAI_TAI_PROJECT_ID="your-project-id" \
  npx @modelcontextprotocol/inspector mai-tai-mcp
```
