# Anam MCP Server Implementation Plan

## Overview

Build a Python MCP (Model Context Protocol) server that wraps the Anam AI API, allowing Claude and other MCP clients to manage personas, avatars, voices, tools, and sessions programmatically.

## Reference Implementation

Use the ElevenLabs MCP server as the structural reference: https://github.com/elevenlabs/elevenlabs-mcp

Key patterns to follow:

- Python package with `pyproject.toml` for dependencies and CLI entry point
- Uses `mcp` Python SDK (FastMCP pattern)
- Environment variable for API key (`ANAM_API_KEY`)
- Async HTTP client (`httpx`) for API calls
- Published to PyPI so users can run via `uvx anam-mcp`

## Anam API Details

**Base URL:** `https://api.anam.ai`

**Authentication:** Bearer token in Authorization header
```
Authorization: Bearer {ANAM_API_KEY}
```

## API Endpoints to Implement

Based on the API reference at https://docs.anam.ai/api-reference/:

### Personas

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/personas` | List all personas |
| POST | `/v1/personas` | Create a new persona |
| GET | `/v1/personas/{id}` | Get persona by ID |
| PUT | `/v1/personas/{id}` | Update persona by ID |
| DELETE | `/v1/personas/{id}` | Delete persona by ID |

### Avatars

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/avatars` | List all avatars |
| POST | `/v1/avatars` | Create avatar (enterprise/pro only, accepts image file or URL) |
| PUT | `/v1/avatars/{id}` | Update avatar (display name only) |
| DELETE | `/v1/avatars/{id}` | Delete avatar by ID |

### Voices

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/voices` | List all voices |

### Tools

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/tools` | List all tools for the organization |
| POST | `/v1/tools` | Create a new tool (webhook, knowledge, or client tool) |
| PUT | `/v1/tools/{id}` | Update a tool |
| DELETE | `/v1/tools/{id}` | Delete a tool |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/auth/session-token` | Create a session token (ephemeral or stateful) |

### Knowledge Base

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/knowledge/groups` | List knowledge folders |
| POST | `/v1/knowledge/groups` | Create knowledge folder |
| POST | `/v1/knowledge/groups/{id}/documents` | Upload document to folder |

## Persona Configuration Schema

When creating personas or session tokens, the `personaConfig` object has these fields:

```python
{
    "name": str,                    # Display name
    "avatarId": str,                # UUID of the avatar
    "voiceId": str,                 # UUID of the voice
    "llmId": str,                   # UUID of LLM or "CUSTOMER_CLIENT_V1" for custom
    "systemPrompt": str,            # Personality/behavior instructions
    "languageCode": str,            # Optional: "en", "fr", "es", etc.
    "maxSessionLengthSeconds": int, # Optional: session timeout
    "toolIds": list[str],           # Optional: attached tool UUIDs
}
```

For stateful personas (created in the Lab), you can reference by ID:

```python
{
    "personaId": str  # UUID of saved persona
}
```

## Default IDs (for reference/examples)

| Resource | ID |
|----------|-----|
| Default Avatar (Cara) | `30fa96d0-26c4-4e55-94a0-517025942e18` |
| Default Voice (Cara) | `6bfbe25a-979d-40f3-a92b-5394170af54b` |
| Default LLM | `0934d97d-0c3a-4f33-91b0-5e136a0ef466` |

## Project Structure

```
anam-mcp/
├── anam_mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server with tool definitions
│   └── client.py          # Async Anam API client wrapper
├── pyproject.toml         # Dependencies, CLI entry point, PyPI metadata
├── README.md              # Usage instructions
├── .env.example           # Example environment variables
└── LICENSE                # MIT
```

## MCP Tools to Implement

### Persona Management

| Tool | Description |
|------|-------------|
| `list_personas` | List all personas in the account |
| `get_persona` | Get details of a specific persona by ID |
| `create_persona` | Create a new persona with avatar, voice, LLM, system prompt |
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
| `list_voices` | List all available voices with language info |

### Tool Management

| Tool | Description |
|------|-------------|
| `list_tools` | List all tools in the organization |
| `create_webhook_tool` | Create a webhook tool for API integrations |
| `create_knowledge_tool` | Create a knowledge/RAG tool |
| `delete_tool` | Delete a tool |

### Session Management

| Tool | Description |
|------|-------------|
| `create_session_token` | Generate a session token for client SDK use. Support both ephemeral (inline config) and stateful (persona ID) modes |

### Knowledge Base (if time permits)

| Tool | Description |
|------|-------------|
| `list_knowledge_folders` | List knowledge folders |
| `create_knowledge_folder` | Create a new folder |
| `upload_document` | Upload a document to a folder |

## Implementation Details

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "anam-mcp"
version = "0.1.0"
description = "Official Anam AI MCP server for managing AI personas"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
authors = [
    { name = "Anam AI", email = "support@anam.ai" }
]
keywords = ["mcp", "anam", "ai", "avatar", "persona"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "mcp>=1.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[project.scripts]
anam-mcp = "anam_mcp.server:main"

[tool.hatch.build.targets.wheel]
packages = ["anam_mcp"]
```

### Environment Variables

```
ANAM_API_KEY=your-api-key-here
ANAM_API_URL=https://api.anam.ai  # Optional override for staging
```

### Example Tool Implementation

```python
from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("anam")

ANAM_API_URL = os.getenv("ANAM_API_URL", "https://api.anam.ai")
ANAM_API_KEY = os.getenv("ANAM_API_KEY")

def get_headers():
    return {
        "Authorization": f"Bearer {ANAM_API_KEY}",
        "Content-Type": "application/json"
    }

@mcp.tool()
async def list_personas() -> dict:
    """List all personas in your Anam account."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{ANAM_API_URL}/v1/personas",
            headers=get_headers()
        )
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def create_persona(
    name: str,
    avatar_id: str,
    voice_id: str,
    system_prompt: str,
    llm_id: str = "0934d97d-0c3a-4f33-91b0-5e136a0ef466"
) -> dict:
    """Create a new Anam persona with specified avatar, voice, and personality.

    Args:
        name: Display name for the persona
        avatar_id: UUID of the avatar to use (see list_avatars)
        voice_id: UUID of the voice to use (see list_voices)
        system_prompt: Instructions defining the persona's personality and behavior
        llm_id: UUID of the LLM to use (defaults to Anam's standard LLM)
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ANAM_API_URL}/v1/personas",
            headers=get_headers(),
            json={
                "name": name,
                "avatarId": avatar_id,
                "voiceId": voice_id,
                "llmId": llm_id,
                "systemPrompt": system_prompt
            }
        )
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def create_session_token(
    persona_id: str = None,
    name: str = None,
    avatar_id: str = None,
    voice_id: str = None,
    system_prompt: str = None,
    llm_id: str = None,
    max_session_length_seconds: int = None
) -> dict:
    """Create a session token for connecting to an Anam persona.

    Use EITHER persona_id (for saved personas) OR the individual config fields (for ephemeral sessions).

    Args:
        persona_id: UUID of a saved persona (stateful mode)
        name: Persona display name (ephemeral mode)
        avatar_id: Avatar UUID (ephemeral mode)
        voice_id: Voice UUID (ephemeral mode)
        system_prompt: Personality instructions (ephemeral mode)
        llm_id: LLM UUID (ephemeral mode)
        max_session_length_seconds: Optional session timeout
    """
    if persona_id:
        persona_config = {"personaId": persona_id}
    else:
        persona_config = {}
        if name: persona_config["name"] = name
        if avatar_id: persona_config["avatarId"] = avatar_id
        if voice_id: persona_config["voiceId"] = voice_id
        if system_prompt: persona_config["systemPrompt"] = system_prompt
        if llm_id: persona_config["llmId"] = llm_id
        if max_session_length_seconds:
            persona_config["maxSessionLengthSeconds"] = max_session_length_seconds

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ANAM_API_URL}/v1/auth/session-token",
            headers=get_headers(),
            json={"personaConfig": persona_config}
        )
        resp.raise_for_status()
        return resp.json()

def main():
    mcp.run()

if __name__ == "__main__":
    main()
```

## User Configuration

Once published, users add to Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "anam": {
      "command": "uvx",
      "args": ["anam-mcp"],
      "env": {
        "ANAM_API_KEY": "<their-api-key>"
      }
    }
  }
}
```

Or for Claude Code (`.mcp.json`):

```json
{
  "mcpServers": {
    "anam": {
      "type": "stdio",
      "command": "uvx",
      "args": ["anam-mcp"],
      "env": {
        "ANAM_API_KEY": "<their-api-key>"
      }
    }
  }
}
```

## CI/CD: GitHub Actions for PyPI Publishing

Set up automated publishing to PyPI when a new version tag is pushed.

### Project Structure Addition

```
anam-mcp/
├── .github/
│   └── workflows/
│       └── publish.yml    # PyPI publish on tagged releases
├── anam_mcp/
│   └── ...
└── ...
```

### GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v*"

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release
    permissions:
      id-token: write  # Required for trusted publishing

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # Uses trusted publishing - no API token needed
        # Configure at: https://pypi.org/manage/project/anam-mcp/settings/publishing/
```

### PyPI Trusted Publishing Setup

1. Create a PyPI account at https://pypi.org
2. Create the `anam-mcp` project (first publish can be manual or via token)
3. Go to project settings → Publishing → Add a new publisher
4. Configure trusted publisher:
   - Owner: `anam-org`
   - Repository: `anam-mcp`
   - Workflow name: `publish.yml`
   - Environment: `release`

### Release Process

1. Update version in `pyproject.toml`
2. Commit the version bump
3. Create and push a tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. GitHub Actions automatically builds and publishes to PyPI

### Optional: Add Version Validation

Add a job to ensure the tag matches `pyproject.toml` version:

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Validate version
        run: |
          TAG_VERSION=${GITHUB_REF#refs/tags/v}
          PKG_VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
          if [ "$TAG_VERSION" != "$PKG_VERSION" ]; then
            echo "Tag version ($TAG_VERSION) does not match package version ($PKG_VERSION)"
            exit 1
          fi

  publish:
    needs: validate
    # ... rest of publish job
```

## Testing

1. Create a test script that validates each tool works
2. Test with a real Anam API key
3. Verify Claude Desktop integration works

## Deliverables

1. Working Python MCP server package
2. All tools implemented with proper docstrings (these become tool descriptions)
3. README with installation and usage instructions
4. Published to PyPI as `anam-mcp`

## Notes

- The Anam API is primarily for managing personas and generating session tokens. The actual real-time video/audio streaming happens via WebRTC in the client SDK, not via REST API.
- Focus on the management/configuration tools that make sense for an MCP context (listing, creating, updating resources).
- Good docstrings are critical—they become the tool descriptions that Claude sees.
