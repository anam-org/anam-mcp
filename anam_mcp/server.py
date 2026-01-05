"""Anam MCP Server - Exposes Anam AI API as MCP tools."""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import AnamAPIError, AnamClient

# Initialize the MCP server
mcp = FastMCP("anam")

# Default pagination size
DEFAULT_PER_PAGE = 100

# Lazy-initialize the client to allow environment variables to be set
_client: AnamClient | None = None


def get_client() -> AnamClient:
    """Get or create the Anam API client."""
    global _client
    if _client is None:
        _client = AnamClient()
    return _client


def format_error(e: AnamAPIError) -> str:
    """Format an API error as a user-friendly message."""
    return f"Error: {e.message}"


def format_response(data: Any) -> str:
    """Format API response data as a readable string."""
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2)
    return str(data)


def format_avatar_summary(data: dict) -> str:
    """Format avatar list as a clean summary table."""
    items = data.get("data", [])
    meta = data.get("meta", {})

    if not items:
        return "No avatars found."

    lines = [f"Avatars ({meta.get('total', len(items))} total):\n"]
    lines.append(f"{'Name':<20} {'Variant':<12} {'ID':<38} {'Type'}")
    lines.append("-" * 85)

    for item in items:
        name = item.get("displayName", "unnamed")[:19]
        variant = item.get("variantName", "-")[:11]
        item_id = item.get("id", "")
        is_stock = "stock" if item.get("createdByOrganizationId") is None else "custom"
        lines.append(f"{name:<20} {variant:<12} {item_id:<38} {is_stock}")

    if meta.get("lastPage", 1) > 1:
        lines.append(f"\nPage {meta.get('currentPage', 1)} of {meta.get('lastPage', 1)}")

    return "\n".join(lines)


def format_voice_summary(data: dict) -> str:
    """Format voice list as a clean summary table."""
    items = data.get("data", [])
    meta = data.get("meta", {})

    if not items:
        return "No voices found."

    lines = [f"Voices ({meta.get('total', len(items))} total):\n"]
    lines.append(f"{'Name':<30} {'Gender':<8} {'Country':<8} {'ID'}")
    lines.append("-" * 90)

    for item in items:
        name = item.get("displayName", item.get("name", "unnamed"))[:29]
        gender = item.get("gender", "-")[:7]
        country = item.get("country", "-")[:7]
        item_id = item.get("id", "")
        lines.append(f"{name:<30} {gender:<8} {country:<8} {item_id}")

    if meta.get("lastPage", 1) > 1:
        lines.append(f"\nPage {meta.get('currentPage', 1)} of {meta.get('lastPage', 1)}")

    return "\n".join(lines)


def format_persona_summary(data: dict) -> str:
    """Format persona list as a clean summary table."""
    items = data.get("data", [])
    meta = data.get("meta", {})

    if not items:
        return "No personas found."

    lines = [f"Personas ({meta.get('total', len(items))} total):\n"]
    lines.append(f"{'Name':<25} {'ID':<38} {'Avatar':<15}")
    lines.append("-" * 85)

    for item in items:
        name = item.get("name", "unnamed")[:24]
        item_id = item.get("id", "")
        avatar = item.get("avatar", {})
        avatar_name = avatar.get("displayName", "-")[:14] if avatar else "-"
        lines.append(f"{name:<25} {item_id:<38} {avatar_name:<15}")

    if meta.get("lastPage", 1) > 1:
        lines.append(f"\nPage {meta.get('currentPage', 1)} of {meta.get('lastPage', 1)}")

    return "\n".join(lines)


def format_tool_summary(data: dict) -> str:
    """Format tool list as a clean summary table."""
    items = data.get("data", [])
    meta = data.get("meta", {})

    if not items:
        return "No tools found."

    lines = [f"Tools ({meta.get('total', len(items))} total):\n"]
    lines.append(f"{'Name':<25} {'Type':<12} {'ID'}")
    lines.append("-" * 80)

    for item in items:
        name = item.get("name", "unnamed")[:24]
        tool_type = item.get("subtype", item.get("type", "-"))[:11]
        item_id = item.get("id", "")
        lines.append(f"{name:<25} {tool_type:<12} {item_id}")

    if meta.get("lastPage", 1) > 1:
        lines.append(f"\nPage {meta.get('currentPage', 1)} of {meta.get('lastPage', 1)}")

    return "\n".join(lines)


def fuzzy_match(query: str, text: str) -> bool:
    """Simple case-insensitive substring match."""
    return query.lower() in text.lower()


# ─────────────────────────────────────────────────────────────────────────────────
# Persona Tools
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_personas(
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """List all personas in your Anam account.

    Returns a formatted summary of personas with their IDs, names, and avatars.

    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 100)
    """
    client = get_client()
    try:
        result = await client.list_personas(page=page, per_page=per_page or DEFAULT_PER_PAGE)
        return format_persona_summary(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def get_persona(persona_id: str) -> str:
    """Get details of a specific persona by ID.

    Args:
        persona_id: The UUID of the persona to retrieve
    """
    client = get_client()
    try:
        result = await client.get_persona(persona_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


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
        avatar_id: UUID of the avatar. Use list_avatars or search_avatars to find one.
        voice_id: UUID of the voice. Use list_voices or search_voices to find one.
        system_prompt: Instructions defining the persona's personality and behavior.
        llm_id: UUID of the LLM. Defaults to Anam's standard LLM.
    """
    client = get_client()
    try:
        result = await client.create_persona(
            name=name,
            avatar_id=avatar_id,
            voice_id=voice_id,
            system_prompt=system_prompt,
            llm_id=llm_id,
        )
        return f"Created persona '{name}' with ID: {result.get('id')}"
    except AnamAPIError as e:
        return format_error(e)


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
        name: New display name
        avatar_id: New avatar UUID
        voice_id: New voice UUID
        system_prompt: New personality instructions
        llm_id: New LLM UUID
    """
    client = get_client()
    try:
        result = await client.update_persona(
            persona_id=persona_id,
            name=name,
            avatar_id=avatar_id,
            voice_id=voice_id,
            system_prompt=system_prompt,
            llm_id=llm_id,
        )
        return f"Updated persona: {result.get('name', persona_id)}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def delete_persona(persona_id: str) -> str:
    """Delete a persona by ID. This action cannot be undone.

    Args:
        persona_id: The UUID of the persona to delete
    """
    client = get_client()
    try:
        await client.delete_persona(persona_id)
        return f"Deleted persona: {persona_id}"
    except AnamAPIError as e:
        return format_error(e)


# ─────────────────────────────────────────────────────────────────────────────────
# Avatar Tools
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_avatars(
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """List all available avatars.

    Returns a formatted summary of avatars with IDs, names, variants, and type (stock/custom).

    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 100)
    """
    client = get_client()
    try:
        result = await client.list_avatars(page=page, per_page=per_page or DEFAULT_PER_PAGE)
        return format_avatar_summary(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def search_avatars(
    query: str,
    stock_only: bool = False,
) -> str:
    """Search avatars by name.

    Fetches all avatars and filters by name match. Use this to find avatars
    like "Cara", "Mia", "Gabriel", etc.

    Args:
        query: Name to search for (case-insensitive, partial match)
        stock_only: If True, only return stock avatars (not custom)
    """
    client = get_client()
    try:
        # Fetch all avatars
        result = await client.list_avatars(per_page=DEFAULT_PER_PAGE)
        items = result.get("data", [])

        # Filter by query and stock_only
        matches = []
        for item in items:
            name = item.get("displayName") or ""
            variant = item.get("variantName") or ""
            description = item.get("description") or ""
            is_stock = item.get("createdByOrganizationId") is None

            if stock_only and not is_stock:
                continue

            # Match on name, variant, or description
            if fuzzy_match(query, name) or fuzzy_match(query, variant) or fuzzy_match(query, description):
                matches.append(item)

        if not matches:
            return f"No avatars found matching '{query}'"

        # Format results
        lines = [f"Found {len(matches)} avatar(s) matching '{query}':\n"]
        lines.append(f"{'Name':<20} {'Variant':<12} {'ID':<38} {'Type'}")
        lines.append("-" * 85)

        for item in matches:
            name = item.get("displayName", "unnamed")[:19]
            variant = item.get("variantName", "-")[:11]
            item_id = item.get("id", "")
            is_stock = "stock" if item.get("createdByOrganizationId") is None else "custom"
            lines.append(f"{name:<20} {variant:<12} {item_id:<38} {is_stock}")

        return "\n".join(lines)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def create_avatar(
    name: str,
    image_url: str,
) -> str:
    """Create a custom avatar from an image URL.

    Note: This feature is only available for enterprise and pro plans.

    Args:
        name: Display name for the avatar
        image_url: URL of the image to use
    """
    client = get_client()
    try:
        result = await client.create_avatar(name=name, image_url=image_url)
        return f"Created avatar '{name}' with ID: {result.get('id')}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def delete_avatar(avatar_id: str) -> str:
    """Delete a custom avatar by ID. Cannot delete stock avatars.

    Args:
        avatar_id: The UUID of the avatar to delete
    """
    client = get_client()
    try:
        await client.delete_avatar(avatar_id)
        return f"Deleted avatar: {avatar_id}"
    except AnamAPIError as e:
        return format_error(e)


# ─────────────────────────────────────────────────────────────────────────────────
# Voice Tools
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_voices(
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """List all available voices.

    Returns a formatted summary of voices with IDs, names, and languages.
    Over 400 voices available in 50+ languages.

    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 100)
    """
    client = get_client()
    try:
        result = await client.list_voices(page=page, per_page=per_page or DEFAULT_PER_PAGE)
        return format_voice_summary(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def search_voices(
    query: str | None = None,
    country: str | None = None,
    gender: str | None = None,
) -> str:
    """Search voices by name, country, or gender.

    Fetches all voices and filters by the specified criteria.

    Args:
        query: Name to search for (case-insensitive, partial match)
        country: Country code to filter by (e.g., "US", "GB", "FR", "DE", "PT")
        gender: Gender to filter by ("MALE" or "FEMALE")
    """
    client = get_client()
    try:
        if not query and not country and not gender:
            return "Please provide at least one filter: query (name), country, or gender."

        # Fetch all voices (may need multiple pages for 400+ voices)
        all_items = []
        page = 1
        while True:
            result = await client.list_voices(page=page, per_page=DEFAULT_PER_PAGE)
            # Defensive: ensure result is a dict
            if not isinstance(result, dict):
                break
            items = result.get("data") or []
            # Defensive: filter out None items
            all_items.extend([i for i in items if i is not None])
            meta = result.get("meta") or {}
            if page >= (meta.get("lastPage") or 1):
                break
            page += 1

        # Filter
        matches = []
        for item in all_items:
            if not isinstance(item, dict):
                continue
            name = item.get("displayName") or item.get("name") or ""
            item_country = item.get("country") or ""
            item_gender = item.get("gender") or ""
            description = item.get("description") or ""

            # Fuzzy match on name and description
            name_match = not query or fuzzy_match(query, name) or fuzzy_match(query, description)
            # Exact match on country/gender (case-insensitive)
            country_match = not country or item_country.upper() == country.upper()
            gender_match = not gender or item_gender.upper() == gender.upper()

            if name_match and country_match and gender_match:
                matches.append(item)

        if not matches:
            filter_desc = []
            if query:
                filter_desc.append(f"name='{query}'")
            if country:
                filter_desc.append(f"country='{country}'")
            if gender:
                filter_desc.append(f"gender='{gender}'")
            return f"No voices found matching {', '.join(filter_desc)}"

        # Format results (limit to 50 to avoid huge output)
        display = matches[:50]
        lines = [f"Found {len(matches)} voice(s)" + (f" (showing first 50)" if len(matches) > 50 else "") + ":\n"]
        lines.append(f"{'Name':<30} {'Gender':<8} {'Country':<8} {'ID'}")
        lines.append("-" * 90)

        for item in display:
            name = (item.get("displayName") or item.get("name") or "unnamed")[:29]
            item_gender = (item.get("gender") or "-")[:7]
            item_country = (item.get("country") or "-")[:7]
            item_id = item.get("id") or ""
            lines.append(f"{name:<30} {item_gender:<8} {item_country:<8} {item_id}")

        return "\n".join(lines)
    except AnamAPIError as e:
        return format_error(e)


# ─────────────────────────────────────────────────────────────────────────────────
# Tool Management
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_tools(
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """List all tools in your organization.

    Returns webhook tools, knowledge tools, and client tools that can be
    attached to personas.

    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 100)
    """
    client = get_client()
    try:
        result = await client.list_tools(page=page, per_page=per_page or DEFAULT_PER_PAGE)
        return format_tool_summary(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def create_webhook_tool(
    name: str,
    description: str,
    url: str,
    method: str = "POST",
    await_response: bool = True,
) -> str:
    """Create a webhook tool for personas to call external APIs.

    Args:
        name: Tool name in snake_case (e.g., "check_order_status")
        description: When the LLM should call this tool. Be specific.
        url: The HTTP endpoint to call
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        await_response: Wait for response (False for fire-and-forget)
    """
    client = get_client()
    try:
        result = await client.create_webhook_tool(
            name=name,
            description=description,
            url=url,
            method=method,
            await_response=await_response,
        )
        return f"Created webhook tool '{name}' with ID: {result.get('id')}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def create_knowledge_tool(
    name: str,
    description: str,
    folder_ids: list[str],
) -> str:
    """Create a knowledge tool for RAG (document search).

    Args:
        name: Tool name in snake_case (e.g., "search_product_docs")
        description: When the LLM should use this tool
        folder_ids: List of knowledge folder UUIDs to search
    """
    client = get_client()
    try:
        result = await client.create_knowledge_tool(
            name=name,
            description=description,
            folder_ids=folder_ids,
        )
        return f"Created knowledge tool '{name}' with ID: {result.get('id')}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def delete_tool(tool_id: str) -> str:
    """Delete a tool by ID.

    Args:
        tool_id: The UUID of the tool to delete
    """
    client = get_client()
    try:
        await client.delete_tool(tool_id)
        return f"Deleted tool: {tool_id}"
    except AnamAPIError as e:
        return format_error(e)


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
    """Create a session token for the Anam client SDK.

    Use EITHER persona_id (for saved personas) OR individual config fields (ephemeral).

    Args:
        persona_id: UUID of a saved persona (recommended for production)
        name: Persona name (ephemeral mode)
        avatar_id: Avatar UUID (ephemeral). Use search_avatars to find one.
        voice_id: Voice UUID (ephemeral). Use search_voices to find one.
        system_prompt: Personality instructions (ephemeral)
        llm_id: LLM UUID (ephemeral)
        language_code: Speech recognition language (e.g., "en", "fr")
        max_session_length_seconds: Session timeout
    """
    client = get_client()
    try:
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
        token = result.get("sessionToken", "")
        # Truncate token for display
        display_token = token[:20] + "..." + token[-10:] if len(token) > 35 else token
        return f"Session token created: {display_token}\n\nFull token:\n{token}"
    except AnamAPIError as e:
        return format_error(e)


# ─────────────────────────────────────────────────────────────────────────────────
# Knowledge Base
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_knowledge_folders() -> str:
    """List all knowledge folders in your organization.

    Knowledge folders contain documents for RAG capabilities.
    """
    client = get_client()
    try:
        result = await client.list_knowledge_folders()

        # Handle both list and dict responses
        if isinstance(result, list):
            items = result
        else:
            items = result.get("data", [result])

        if not items:
            return "No knowledge folders found."

        lines = [f"Knowledge Folders ({len(items)}):\n"]
        lines.append(f"{'Name':<30} {'ID'}")
        lines.append("-" * 70)

        for item in items:
            name = item.get("name", "unnamed")[:29]
            item_id = item.get("id", "")
            lines.append(f"{name:<30} {item_id}")

        return "\n".join(lines)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def create_knowledge_folder(
    name: str,
    description: str | None = None,
) -> str:
    """Create a new knowledge folder for documents.

    After creating, upload documents via Anam Lab UI or API.

    Args:
        name: Folder name (e.g., "Product Documentation")
        description: Optional description
    """
    client = get_client()
    try:
        result = await client.create_knowledge_folder(
            name=name,
            description=description,
        )
        return f"Created folder '{name}' with ID: {result.get('id')}"
    except AnamAPIError as e:
        return format_error(e)


def main():
    """Run the Anam MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
