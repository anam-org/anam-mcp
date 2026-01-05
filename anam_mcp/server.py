"""Anam MCP Server - Exposes Anam AI API as MCP tools."""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import AnamClient

# Initialize the MCP server
mcp = FastMCP("anam")

# Lazy-initialize the client to allow environment variables to be set
_client: AnamClient | None = None


def get_client() -> AnamClient:
    """Get or create the Anam API client."""
    global _client
    if _client is None:
        _client = AnamClient()
    return _client


def format_response(data: Any) -> str:
    """Format API response data as a readable string."""
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2)
    return str(data)


# ─────────────────────────────────────────────────────────────────────────────────
# Persona Tools
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_personas() -> str:
    """List all personas in your Anam account.

    Returns a list of all personas with their IDs, names, avatar IDs, voice IDs,
    and system prompts.
    """
    client = get_client()
    result = await client.list_personas()
    return format_response(result)


@mcp.tool()
async def get_persona(persona_id: str) -> str:
    """Get details of a specific persona by ID.

    Args:
        persona_id: The UUID of the persona to retrieve
    """
    client = get_client()
    result = await client.get_persona(persona_id)
    return format_response(result)


@mcp.tool()
async def create_persona(
    name: str,
    avatar_id: str,
    voice_id: str,
    system_prompt: str,
    llm_id: str = "0934d97d-0c3a-4f33-91b0-5e136a0ef466",
) -> str:
    """Create a new Anam persona with specified avatar, voice, and personality.

    Args:
        name: Display name for the persona (e.g., "Customer Support Agent")
        avatar_id: UUID of the avatar to use. Use list_avatars to see available options.
        voice_id: UUID of the voice to use. Use list_voices to see available options.
        system_prompt: Instructions defining the persona's personality and behavior.
            Example: "You are a helpful customer service representative. Be friendly and concise."
        llm_id: UUID of the LLM to use. Defaults to Anam's standard LLM.
            Use "CUSTOMER_CLIENT_V1" for custom LLM integration.
    """
    client = get_client()
    result = await client.create_persona(
        name=name,
        avatar_id=avatar_id,
        voice_id=voice_id,
        system_prompt=system_prompt,
        llm_id=llm_id,
    )
    return format_response(result)


@mcp.tool()
async def update_persona(
    persona_id: str,
    name: str | None = None,
    avatar_id: str | None = None,
    voice_id: str | None = None,
    system_prompt: str | None = None,
    llm_id: str | None = None,
) -> str:
    """Update an existing persona. Only provide the fields you want to change.

    Args:
        persona_id: The UUID of the persona to update
        name: New display name for the persona
        avatar_id: New avatar UUID
        voice_id: New voice UUID
        system_prompt: New system prompt/personality instructions
        llm_id: New LLM UUID
    """
    client = get_client()
    result = await client.update_persona(
        persona_id=persona_id,
        name=name,
        avatar_id=avatar_id,
        voice_id=voice_id,
        system_prompt=system_prompt,
        llm_id=llm_id,
    )
    return format_response(result)


@mcp.tool()
async def delete_persona(persona_id: str) -> str:
    """Delete a persona by ID. This action cannot be undone.

    Args:
        persona_id: The UUID of the persona to delete
    """
    client = get_client()
    result = await client.delete_persona(persona_id)
    return format_response(result)


# ─────────────────────────────────────────────────────────────────────────────────
# Avatar Tools
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_avatars() -> str:
    """List all available avatars.

    Returns a list of avatars with their IDs and names. Use the avatar ID when
    creating personas or session tokens.

    Common avatars include:
    - Cara (default): 30fa96d0-26c4-4e55-94a0-517025942e18
    """
    client = get_client()
    result = await client.list_avatars()
    return format_response(result)


@mcp.tool()
async def create_avatar(
    name: str,
    image_url: str,
) -> str:
    """Create a custom avatar from an image URL.

    Note: This feature is only available for enterprise and pro plans.

    Args:
        name: Display name for the avatar
        image_url: URL of the image to use for the avatar
    """
    client = get_client()
    result = await client.create_avatar(name=name, image_url=image_url)
    return format_response(result)


@mcp.tool()
async def delete_avatar(avatar_id: str) -> str:
    """Delete a custom avatar by ID. This action cannot be undone.

    Note: You cannot delete stock avatars, only custom ones you've created.

    Args:
        avatar_id: The UUID of the avatar to delete
    """
    client = get_client()
    result = await client.delete_avatar(avatar_id)
    return format_response(result)


# ─────────────────────────────────────────────────────────────────────────────────
# Voice Tools
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_voices() -> str:
    """List all available voices.

    Returns a list of voices with their IDs, names, and language information.
    Use the voice ID when creating personas or session tokens.

    Common voices include:
    - Cara (default English): 6bfbe25a-979d-40f3-a92b-5394170af54b

    Over 400 voices are available in 50+ languages.
    """
    client = get_client()
    result = await client.list_voices()
    return format_response(result)


# ─────────────────────────────────────────────────────────────────────────────────
# Tool Management
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_tools() -> str:
    """List all tools in your organization.

    Returns webhook tools, knowledge tools, and client tools that can be
    attached to personas to give them additional capabilities.
    """
    client = get_client()
    result = await client.list_tools()
    return format_response(result)


@mcp.tool()
async def create_webhook_tool(
    name: str,
    description: str,
    url: str,
    method: str = "POST",
    await_response: bool = True,
) -> str:
    """Create a webhook tool that allows personas to call external APIs.

    Args:
        name: Tool name in snake_case (e.g., "check_order_status")
        description: When the LLM should call this tool. Be specific about triggers.
            Example: "Check the status of a customer order when they ask about their order"
        url: The HTTP endpoint to call
        method: HTTP method (GET, POST, PUT, PATCH, DELETE). Defaults to POST.
        await_response: Whether to wait for the response. Set to False for fire-and-forget.
    """
    client = get_client()
    result = await client.create_webhook_tool(
        name=name,
        description=description,
        url=url,
        method=method,
        await_response=await_response,
    )
    return format_response(result)


@mcp.tool()
async def create_knowledge_tool(
    name: str,
    description: str,
    folder_ids: list[str],
) -> str:
    """Create a knowledge tool for RAG (Retrieval-Augmented Generation).

    This allows personas to search through documents you've uploaded to
    knowledge folders.

    Args:
        name: Tool name in snake_case (e.g., "search_product_docs")
        description: When the LLM should use this tool.
            Example: "Search product documentation when users ask about features or specifications"
        folder_ids: List of knowledge folder UUIDs to search. Use list_knowledge_folders to see available folders.
    """
    client = get_client()
    result = await client.create_knowledge_tool(
        name=name,
        description=description,
        folder_ids=folder_ids,
    )
    return format_response(result)


@mcp.tool()
async def delete_tool(tool_id: str) -> str:
    """Delete a tool by ID. This action cannot be undone.

    Args:
        tool_id: The UUID of the tool to delete
    """
    client = get_client()
    result = await client.delete_tool(tool_id)
    return format_response(result)


# ─────────────────────────────────────────────────────────────────────────────────
# Session Management
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def create_session_token(
    persona_id: str | None = None,
    name: str | None = None,
    avatar_id: str | None = None,
    voice_id: str | None = None,
    system_prompt: str | None = None,
    llm_id: str | None = None,
    language_code: str | None = None,
    max_session_length_seconds: int | None = None,
) -> str:
    """Create a session token for connecting to an Anam persona via the client SDK.

    Use EITHER persona_id (for saved personas) OR the individual config fields
    (for ephemeral sessions).

    Stateful mode (recommended for production):
        Provide only persona_id to use a pre-configured persona from the Anam Lab.

    Ephemeral mode (for quick testing):
        Provide name, avatar_id, voice_id, and system_prompt to create a
        temporary persona configuration.

    Args:
        persona_id: UUID of a saved persona (stateful mode)
        name: Persona display name (ephemeral mode)
        avatar_id: Avatar UUID (ephemeral mode). Default Cara: 30fa96d0-26c4-4e55-94a0-517025942e18
        voice_id: Voice UUID (ephemeral mode). Default Cara: 6bfbe25a-979d-40f3-a92b-5394170af54b
        system_prompt: Personality instructions (ephemeral mode)
        llm_id: LLM UUID (ephemeral mode). Default: 0934d97d-0c3a-4f33-91b0-5e136a0ef466
        language_code: Language for speech recognition (e.g., "en", "fr", "es")
        max_session_length_seconds: Optional session timeout in seconds
    """
    client = get_client()
    result = await client.create_session_token(
        persona_id=persona_id,
        name=name,
        avatar_id=avatar_id,
        voice_id=voice_id,
        system_prompt=system_prompt,
        llm_id=llm_id,
        language_code=language_code,
        max_session_length_seconds=max_session_length_seconds,
    )
    return format_response(result)


# ─────────────────────────────────────────────────────────────────────────────────
# Knowledge Base
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_knowledge_folders() -> str:
    """List all knowledge folders in your organization.

    Knowledge folders contain documents that can be searched by personas
    using knowledge tools (RAG).
    """
    client = get_client()
    result = await client.list_knowledge_folders()
    return format_response(result)


@mcp.tool()
async def create_knowledge_folder(
    name: str,
    description: str | None = None,
) -> str:
    """Create a new knowledge folder for storing documents.

    After creating a folder, you can upload documents via the Anam Lab UI
    or the API to enable RAG capabilities for your personas.

    Args:
        name: Descriptive name for the folder (e.g., "Product Documentation")
        description: Optional description of what content is in this folder
    """
    client = get_client()
    result = await client.create_knowledge_folder(
        name=name,
        description=description,
    )
    return format_response(result)


def main():
    """Run the Anam MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
