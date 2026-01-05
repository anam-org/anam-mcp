# Anam MCP Server

Official MCP (Model Context Protocol) server for [Anam AI](https://anam.ai) - manage AI personas, avatars, voices, and sessions directly from Claude or any MCP client.

## Installation

### Using uvx (recommended)

```bash
uvx anam-mcp
```

### Using pip

```bash
pip install anam-mcp
```

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "anam": {
      "command": "uvx",
      "args": ["anam-mcp"],
      "env": {
        "ANAM_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

### Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "anam": {
      "type": "stdio",
      "command": "uvx",
      "args": ["anam-mcp"],
      "env": {
        "ANAM_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

## Getting Your API Key

1. Sign up at [Anam Lab](https://lab.anam.ai)
2. Navigate to the [API Keys page](https://lab.anam.ai/api-keys)
3. Click "Create API key" and save it securely

## Available Tools

### Persona Management

| Tool | Description |
|------|-------------|
| `list_personas` | List all personas in your account |
| `get_persona` | Get details of a specific persona |
| `create_persona` | Create a new persona with avatar, voice, and personality |
| `update_persona` | Update an existing persona |
| `delete_persona` | Delete a persona |

### Avatar Management

| Tool | Description |
|------|-------------|
| `list_avatars` | List all available avatars |
| `create_avatar` | Create custom avatar from image (enterprise/pro) |
| `delete_avatar` | Delete a custom avatar |

### Voice Management

| Tool | Description |
|------|-------------|
| `list_voices` | List all available voices (400+ in 50+ languages) |

### Tool Management

| Tool | Description |
|------|-------------|
| `list_tools` | List all tools in your organization |
| `create_webhook_tool` | Create a webhook tool for API integrations |
| `create_knowledge_tool` | Create a knowledge/RAG tool |
| `delete_tool` | Delete a tool |

### Session Management

| Tool | Description |
|------|-------------|
| `create_session_token` | Generate a session token for the client SDK |

### Knowledge Base

| Tool | Description |
|------|-------------|
| `list_knowledge_folders` | List knowledge folders |
| `create_knowledge_folder` | Create a new folder for documents |

## Example Usage

Once configured, you can ask Claude:

- "List all my Anam personas"
- "Create a new persona named 'Sales Assistant' with a friendly personality"
- "What avatars are available?"
- "Generate a session token for my customer support persona"

## Default IDs

For quick testing, you can use these default IDs:

| Resource | ID |
|----------|-----|
| Avatar (Cara) | `30fa96d0-26c4-4e55-94a0-517025942e18` |
| Voice (Cara) | `6bfbe25a-979d-40f3-a92b-5394170af54b` |
| Default LLM | `0934d97d-0c3a-4f33-91b0-5e136a0ef466` |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANAM_API_KEY` | Your Anam API key (required) | - |
| `ANAM_API_URL` | API base URL (for staging) | `https://api.anam.ai` |

## Documentation

- [Anam Developer Docs](https://docs.anam.ai)
- [API Reference](https://docs.anam.ai/api-reference)
- [Avatar Gallery](https://docs.anam.ai/resources/avatar-gallery)
- [Voice Gallery](https://docs.anam.ai/resources/voice-gallery)

## License

MIT License - see [LICENSE](LICENSE) for details.
