# Anam MCP Server

> [!IMPORTANT]
> **This server has moved.** Anam now hosts its MCP server at
> **`https://lab.anam.ai/mcp`**. There's nothing to install: you sign in with
> your Anam account over OAuth instead of pasting an API key, and new tools
> arrive without an update.
>
> This Python package (`anam-mcp` on PyPI) is no longer maintained. Switch to
> the hosted server using the steps below, or follow the
> [setup guide](https://lab.anam.ai/mcp) and the
> [docs](https://anam.ai/docs/resources/mcp).

## Connect to the hosted server

Server URL:

```text
https://lab.anam.ai/mcp
```

The first time you connect, your app opens Anam in a browser. Sign in, choose
one organization, and choose **Full access** or **Read only**.

### Claude (claude.ai and Claude Desktop)

1. Open **Settings**, then **Connectors**, and choose **Add custom connector**.
2. Name it Anam, paste `https://lab.anam.ai/mcp` and add it.
3. Choose **Connect** and sign in to Anam.

On Team and Enterprise plans, an owner adds the connector in the
organization's settings first.

### ChatGPT

1. Open **Plugins**, choose the plus button, then **Add custom MCP server**.
2. Name it Anam, paste `https://lab.anam.ai/mcp` and choose **OAuth**.
3. Accept the warning, choose **Create as a plugin** and sign in to Anam.

### Claude Code

```bash
claude mcp add --transport http --scope user anam https://lab.anam.ai/mcp
claude mcp login anam
```

### Cursor

Add Anam to `~/.cursor/mcp.json`, or to `.cursor/mcp.json` in a project:

```json
{
  "mcpServers": {
    "anam": {
      "url": "https://lab.anam.ai/mcp"
    }
  }
}
```

Cursor asks you to sign in to Anam when it first connects.

### VS Code

```bash
code --add-mcp '{"name":"anam","type":"http","url":"https://lab.anam.ai/mcp"}'
```

### Codex

```bash
codex mcp add anam --url https://lab.anam.ai/mcp
codex mcp login anam
```

### Other clients

Add `https://lab.anam.ai/mcp` as a remote MCP server (Streamable HTTP). Sign-in
is OAuth 2.1 with PKCE; clients register themselves. See the
[setup guide](https://lab.anam.ai/mcp) for details.

### Agents without a browser: API keys

Your Anam API key still works. Send it as a Bearer token instead of signing in:

```json
{
  "mcpServers": {
    "anam": {
      "url": "https://lab.anam.ai/mcp",
      "headers": {
        "Authorization": "Bearer <your Anam API key>"
      }
    }
  }
}
```

```bash
# Claude Code
claude mcp add --transport http anam https://lab.anam.ai/mcp \
  --header "Authorization: Bearer $ANAM_API_KEY"

# Codex
codex mcp add anam --url https://lab.anam.ai/mcp --bearer-token-env-var ANAM_API_KEY
```

Create and revoke keys on the [API keys page](https://lab.anam.ai/api-keys).

### Per-client paths

`https://lab.anam.ai/mcp` serves every tool, so use it everywhere unless a
directory listing tells you otherwise. The paths `/mcp/claude`,
`/mcp/chatgpt`, `/mcp/copilot`, `/mcp/gemini`, `/mcp/agentforce` and
`/mcp/muse` serve the smaller tool sets made for those platforms' directory
listings.

## What changes when you switch

- **Sign-in:** OAuth with your Anam account replaces `ANAM_API_KEY`. API keys
  still work as a Bearer token.
- **No local install:** you no longer need Python, `uv` or `uvx`.
- **Meetings:** inviting a persona to Google Meet, Zoom or Microsoft Teams no
  longer needs a Recall AI key.
- **Tool names:** every tool now starts with `anam_`. See the table below.

| `anam-mcp` tool | Hosted server tool |
| --- | --- |
| `list_personas`, `get_persona`, `create_persona`, `update_persona`, `delete_persona` | `anam_persona_list`, `anam_persona_get`, `anam_persona_create`, `anam_persona_update`, `anam_persona_delete` |
| `list_avatars`, `get_avatar`, `create_avatar`, `update_avatar`, `delete_avatar` | `anam_avatar_list`, `anam_avatar_get`, `anam_avatar_create`, `anam_avatar_update`, `anam_avatar_delete` |
| `search_avatars` | `anam_avatar_list` with `search` |
| `list_voices`, `get_voice`, `update_voice`, `delete_voice` | `anam_voice_list`, `anam_voice_get`, `anam_voice_update`, `anam_voice_delete` |
| `search_voices` | `anam_voice_list` with `search`, `gender` or `country` |
| `create_voice` | `anam_voice_import` (a provider voice ID) or `anam_voice_clone` (a recording) |
| `list_tools`, `get_tool`, `update_tool`, `delete_tool` | `anam_tool_list`, `anam_tool_get`, `anam_tool_update`, `anam_tool_delete` |
| `create_webhook_tool`, `create_knowledge_tool` | `anam_tool_create`; for knowledge, `anam_persona_knowledge_add` |
| `create_session_token` | `anam_session_token_create` |
| `list_sessions`, `get_session`, `get_session_recording` | `anam_session_list`, `anam_session_get`, `anam_session_recording_get` |
| `list_knowledge_folders`, `create_knowledge_folder` | `anam_knowledge_folder_list`, `anam_knowledge_folder_create` |
| `get_knowledge_group`, `update_knowledge_group`, `delete_knowledge_group`, `search_knowledge_group` | `anam_knowledge_folder_get`, `anam_knowledge_folder_update`, `anam_knowledge_folder_delete`, `anam_knowledge_folder_search` |
| `list_knowledge_documents`, `get_knowledge_document`, `update_knowledge_document`, `delete_knowledge_document` | `anam_knowledge_document_list`, `anam_knowledge_document_get`, `anam_knowledge_document_update`, `anam_knowledge_document_delete` |
| `get_knowledge_document_download` | `anam_knowledge_document_download` |
| `upload_knowledge_document` | `anam_knowledge_document_create_from_text` or `anam_knowledge_document_create_from_url` |
| `list_llms`, `get_llm`, `create_llm`, `update_llm`, `delete_llm` | `anam_llm_list`, `anam_llm_get`, `anam_llm_create`, `anam_llm_update`, `anam_llm_delete` |
| `list_share_links`, `get_share_link`, `create_share_link`, `update_share_link`, `delete_share_link` | `anam_share_link_list`, `anam_share_link_get`, `anam_share_link_create`, `anam_share_link_update`, `anam_share_link_delete` |
| `generate_avatar_video` | `anam_avatar_video_create`, then `anam_avatar_video_get` until it's ready |
| `add_avatar_to_meeting` | `anam_meeting_invite_create` |
| `get_meeting_bot_status`, `list_meeting_bots` | `anam_meeting_invite_get`, `anam_meeting_invite_list` |
| `remove_avatar_from_meeting` | `anam_meeting_invite_cancel` (cancels an invite before the persona joins) |

The hosted server also adds tools this package never had, such as
`anam_quickstart`, `anam_persona_from_brief`, session transcripts and search,
pronunciation dictionaries, integration guides and docs search. The
[docs](https://anam.ai/docs/resources/mcp#tools) list them all.

## Legacy: running `anam-mcp` locally

This package still installs and runs against the Anam API, but it gets no new
tools or fixes. Its last release is 0.1.13.

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

| Variable | Description | Default |
| --- | --- | --- |
| `ANAM_API_KEY` | Your Anam API key (required) | - |
| `ANAM_API_URL` | API base URL | `https://api.anam.ai` |
| `RECALL_API_KEY` | Recall AI API key, for the meeting tools | - |
| `MEET_PAGE_URL` | Avatar meet page URL | `https://meet.anam.ai` |
| `TEXT_TO_AVATAR_URL` | Text-to-avatar service URL | `https://anam-org--text-to-avatar-api.modal.run` |

The previous README, with the full list of this package's tools, is in this
repository's history.

## License

MIT License. See [LICENSE](LICENSE).
