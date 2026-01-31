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
| `search_avatars` | Search avatars by name or description |
| `get_avatar` | Get details of a specific avatar |
| `create_avatar` | Create custom avatar from image (enterprise/pro) |
| `update_avatar` | Update an avatar's metadata |
| `delete_avatar` | Delete a custom avatar |

### Voice Management

| Tool | Description |
|------|-------------|
| `list_voices` | List all available voices (400+ in 50+ languages) |
| `search_voices` | Search voices by name, language, or gender |
| `get_voice` | Get details of a specific voice |
| `create_voice` | Create a custom voice |
| `update_voice` | Update a voice's metadata |
| `delete_voice` | Delete a custom voice |

### Tool Management

| Tool | Description |
|------|-------------|
| `list_tools` | List all tools in your organization |
| `get_tool` | Get details of a specific tool |
| `create_webhook_tool` | Create a webhook tool for API integrations |
| `create_knowledge_tool` | Create a knowledge/RAG tool |
| `update_tool` | Update a tool's configuration |
| `delete_tool` | Delete a tool |

### Session Management

| Tool | Description |
|------|-------------|
| `create_session_token` | Generate a session token for the client SDK |
| `list_sessions` | List all sessions with optional filters |
| `get_session` | Get details of a specific session |
| `get_session_recording` | Download a session recording |

### Knowledge Folders

| Tool | Description |
|------|-------------|
| `list_knowledge_folders` | List knowledge folders |
| `get_knowledge_folder` | Get details of a specific folder |
| `create_knowledge_folder` | Create a new folder for documents |
| `update_knowledge_folder` | Update a folder's metadata |
| `delete_knowledge_folder` | Delete a knowledge folder |
| `search_knowledge_folder` | Search within a knowledge folder |

### Knowledge Documents

| Tool | Description |
|------|-------------|
| `list_knowledge_documents` | List documents in a folder |
| `get_knowledge_document` | Get details of a specific document |
| `upload_knowledge_document` | Upload a document to a folder |
| `update_knowledge_document` | Update document metadata |
| `delete_knowledge_document` | Delete a document |
| `get_knowledge_document_download` | Download a document |

### LLM Management

| Tool | Description |
|------|-------------|
| `list_llms` | List all LLM configurations |
| `get_llm` | Get details of a specific LLM |
| `create_llm` | Create a new LLM configuration |
| `update_llm` | Update an LLM configuration |
| `delete_llm` | Delete an LLM configuration |

### Share Links

| Tool | Description |
|------|-------------|
| `list_share_links` | List all share links |
| `get_share_link` | Get details of a specific share link |
| `create_share_link` | Create a share link for a persona |
| `update_share_link` | Update a share link |
| `delete_share_link` | Delete a share link |

### Text-to-Avatar (Early Access)

> **Internal Testing** - This feature is in early access. Contact [support@anam.ai](mailto:support@anam.ai) for access.

| Tool | Description |
|------|-------------|
| `generate_avatar_video` | Generate an MP4 video of an avatar speaking a script |

### Meeting Avatars (Recall Integration)

Add AI avatars to video meetings (Zoom, Google Meet, Microsoft Teams). Requires a [Recall AI](https://recall.ai) API key.

| Tool | Description |
|------|-------------|
| `add_avatar_to_meeting` | Add an Anam avatar to a video meeting |
| `get_meeting_bot_status` | Check the status of a meeting bot |
| `remove_avatar_from_meeting` | Remove an avatar from a meeting |
| `list_meeting_bots` | List all active meeting bots |

**Configuration**: Set `RECALL_API_KEY` environment variable alongside your `ANAM_API_KEY`.

## Example Usage

Once configured, you can ask Claude:

- "List all my Anam personas"
- "Create a new persona named 'Sales Assistant' with a friendly personality"
- "What avatars are available?"
- "Generate a session token for my customer support persona"
- "Add an avatar to my Google Meet call at meet.google.com/abc-defg-hij"

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
| `RECALL_API_KEY` | Recall AI API key (for meeting avatars) | - |
| `MEET_PAGE_URL` | Avatar meet page URL | `https://meet.anam.ai` |
| `TEXT_TO_AVATAR_URL` | Text-to-avatar service URL (early access) | `https://anam-org--text-to-avatar-api.modal.run` |

## Documentation

- [Anam Developer Docs](https://docs.anam.ai)
- [API Reference](https://docs.anam.ai/api-reference)
- [Avatar Gallery](https://docs.anam.ai/resources/avatar-gallery)
- [Voice Gallery](https://docs.anam.ai/resources/voice-gallery)

## License

MIT License - see [LICENSE](LICENSE) for details.
