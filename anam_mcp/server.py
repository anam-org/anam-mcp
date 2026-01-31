"""Anam MCP Server - Exposes Anam AI API as MCP tools."""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import AnamAPIError, AnamClient
from .recall import RecallAPIError, RecallClient

# Initialize the MCP server
mcp = FastMCP("anam")

# Default pagination size
DEFAULT_PER_PAGE = 100

# Lazy-initialize the clients to allow environment variables to be set
_client: AnamClient | None = None
_recall_client: RecallClient | None = None


def get_client() -> AnamClient:
    """Get or create the Anam API client."""
    global _client
    if _client is None:
        _client = AnamClient()
    return _client


def get_recall_client() -> RecallClient:
    """Get or create the Recall API client."""
    global _recall_client
    if _recall_client is None:
        _recall_client = RecallClient()
    return _recall_client


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
async def get_avatar(avatar_id: str) -> str:
    """Get details of a specific avatar by ID.

    Args:
        avatar_id: The UUID of the avatar to retrieve
    """
    client = get_client()
    try:
        result = await client.get_avatar(avatar_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def update_avatar(
    avatar_id: str,
    name: str | None = None,
    display_name: str | None = None,
) -> str:
    """Update a custom avatar. Only provide the fields you want to change.

    Args:
        avatar_id: The UUID of the avatar to update
        name: New internal name
        display_name: New display name
    """
    client = get_client()
    try:
        result = await client.update_avatar(
            avatar_id=avatar_id,
            name=name,
            display_name=display_name,
        )
        return f"Updated avatar: {result.get('displayName', avatar_id)}"
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


@mcp.tool()
async def get_voice(voice_id: str) -> str:
    """Get details of a specific voice by ID.

    Args:
        voice_id: The UUID of the voice to retrieve
    """
    client = get_client()
    try:
        result = await client.get_voice(voice_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def create_voice(
    display_name: str,
    provider: str,
    provider_voice_id: str,
    gender: str | None = None,
    country: str | None = None,
    description: str | None = None,
) -> str:
    """Create a custom voice configuration.

    Args:
        display_name: Display name for the voice
        provider: Voice provider (e.g., "cartesia", "elevenlabs")
        provider_voice_id: The voice ID from the provider
        gender: Gender of the voice ("MALE" or "FEMALE")
        country: Country code (e.g., "US", "GB")
        description: Optional description
    """
    client = get_client()
    try:
        result = await client.create_voice(
            display_name=display_name,
            provider=provider,
            provider_voice_id=provider_voice_id,
            gender=gender,
            country=country,
            description=description,
        )
        return f"Created voice '{display_name}' with ID: {result.get('id')}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def update_voice(
    voice_id: str,
    display_name: str | None = None,
    description: str | None = None,
) -> str:
    """Update a voice configuration. Only provide the fields you want to change.

    Args:
        voice_id: The UUID of the voice to update
        display_name: New display name
        description: New description
    """
    client = get_client()
    try:
        result = await client.update_voice(
            voice_id=voice_id,
            display_name=display_name,
            description=description,
        )
        return f"Updated voice: {result.get('displayName', voice_id)}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def delete_voice(voice_id: str) -> str:
    """Delete a voice by ID.

    Args:
        voice_id: The UUID of the voice to delete
    """
    client = get_client()
    try:
        await client.delete_voice(voice_id)
        return f"Deleted voice: {voice_id}"
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
async def get_tool(tool_id: str) -> str:
    """Get details of a specific tool by ID.

    Args:
        tool_id: The UUID of the tool to retrieve
    """
    client = get_client()
    try:
        result = await client.get_tool(tool_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def update_tool(
    tool_id: str,
    name: str | None = None,
    description: str | None = None,
    url: str | None = None,
    method: str | None = None,
    await_response: bool | None = None,
) -> str:
    """Update a tool. Only provide the fields you want to change.

    Args:
        tool_id: The UUID of the tool to update
        name: New tool name
        description: New description
        url: New webhook URL (for webhook tools)
        method: New HTTP method (for webhook tools)
        await_response: Whether to wait for response (for webhook tools)
    """
    client = get_client()
    try:
        result = await client.update_tool(
            tool_id=tool_id,
            name=name,
            description=description,
            url=url,
            method=method,
            await_response=await_response,
        )
        return f"Updated tool: {result.get('name', tool_id)}"
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
    avatar_model: str = "cara-3",
    max_session_length_seconds: int | None = None,
    skip_greeting: bool | None = None,
) -> str:
    """Create a session token for the Anam client SDK.

    Use EITHER persona_id (for saved personas) OR individual config fields (ephemeral).

    Args:
        persona_id: UUID of a saved persona (recommended for production)
        name: Persona name (ephemeral mode)
        avatar_id: Avatar UUID (ephemeral). Use search_avatars to find one.
        voice_id: Voice UUID (ephemeral). Use search_voices to find one.
        system_prompt: Personality instructions (ephemeral)
        llm_id: LLM UUID (ephemeral, defaults to GPT-4o-mini)
        avatar_model: Avatar model ("cara-2" or "cara-3", default: cara-3)
        max_session_length_seconds: Session timeout
        skip_greeting: Skip the initial greeting (default: False)
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
            avatar_model=avatar_model,
            max_session_length_seconds=max_session_length_seconds,
            skip_greeting=skip_greeting,
        )
        token = result.get("sessionToken", "")
        # Truncate token for display
        display_token = token[:20] + "..." + token[-10:] if len(token) > 35 else token
        return f"Session token created: {display_token}\n\nFull token:\n{token}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def list_sessions(
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """List all sessions in your account.

    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 100)
    """
    client = get_client()
    try:
        result = await client.list_sessions(page=page, per_page=per_page or DEFAULT_PER_PAGE)
        items = result.get("data", [])
        meta = result.get("meta", {})

        if not items:
            return "No sessions found."

        lines = [f"Sessions ({meta.get('total', len(items))} total):\n"]
        lines.append(f"{'ID':<38} {'Status':<12} {'Start Time'}")
        lines.append("-" * 80)

        for item in items:
            session_id = item.get("id", "")
            status = item.get("status", "-")[:11]
            start_time = item.get("startTime", "-")[:20]
            lines.append(f"{session_id:<38} {status:<12} {start_time}")

        if meta.get("lastPage", 1) > 1:
            lines.append(f"\nPage {meta.get('currentPage', 1)} of {meta.get('lastPage', 1)}")

        return "\n".join(lines)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def get_session(session_id: str) -> str:
    """Get details of a specific session by ID.

    Args:
        session_id: The UUID of the session to retrieve
    """
    client = get_client()
    try:
        result = await client.get_session(session_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def get_session_recording(session_id: str) -> str:
    """Get recording information for a session.

    Args:
        session_id: The UUID of the session
    """
    client = get_client()
    try:
        result = await client.get_session_recording(session_id)
        return format_response(result)
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


@mcp.tool()
async def get_knowledge_group(group_id: str) -> str:
    """Get details of a specific knowledge group by ID.

    Args:
        group_id: The UUID of the knowledge group to retrieve
    """
    client = get_client()
    try:
        result = await client.get_knowledge_group(group_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def update_knowledge_group(
    group_id: str,
    name: str | None = None,
    description: str | None = None,
) -> str:
    """Update a knowledge group. Only provide the fields you want to change.

    Args:
        group_id: The UUID of the knowledge group to update
        name: New name
        description: New description
    """
    client = get_client()
    try:
        result = await client.update_knowledge_group(
            group_id=group_id,
            name=name,
            description=description,
        )
        return f"Updated knowledge group: {result.get('name', group_id)}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def delete_knowledge_group(group_id: str) -> str:
    """Delete a knowledge group by ID. This will also delete all documents in the group.

    Args:
        group_id: The UUID of the knowledge group to delete
    """
    client = get_client()
    try:
        await client.delete_knowledge_group(group_id)
        return f"Deleted knowledge group: {group_id}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def search_knowledge_group(
    group_id: str,
    query: str,
    limit: int | None = None,
) -> str:
    """Search within a knowledge group for relevant documents.

    Args:
        group_id: The UUID of the knowledge group to search
        query: Search query
        limit: Maximum number of results
    """
    client = get_client()
    try:
        result = await client.search_knowledge_group(
            group_id=group_id,
            query=query,
            limit=limit,
        )
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


# ─────────────────────────────────────────────────────────────────────────────────
# Knowledge Documents
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_knowledge_documents(
    group_id: str,
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """List all documents in a knowledge group.

    Args:
        group_id: The UUID of the knowledge group
        page: Page number (default: 1)
        per_page: Items per page (default: 100)
    """
    client = get_client()
    try:
        result = await client.list_knowledge_documents(
            group_id=group_id,
            page=page,
            per_page=per_page or DEFAULT_PER_PAGE,
        )

        if isinstance(result, list):
            items = result
            total = len(items)
        else:
            items = result.get("data", [])
            meta = result.get("meta", {})
            total = meta.get("total", len(items))

        if not items:
            return "No documents found in this knowledge group."

        lines = [f"Documents ({total} total):\n"]
        lines.append(f"{'Name':<40} {'ID'}")
        lines.append("-" * 80)

        for item in items:
            name = item.get("name", "unnamed")[:39]
            item_id = item.get("id", "")
            lines.append(f"{name:<40} {item_id}")

        return "\n".join(lines)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def get_knowledge_document(document_id: str) -> str:
    """Get details of a specific knowledge document by ID.

    Args:
        document_id: The UUID of the document to retrieve
    """
    client = get_client()
    try:
        result = await client.get_knowledge_document(document_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def get_knowledge_document_download(document_id: str) -> str:
    """Get download URL for a knowledge document.

    Args:
        document_id: The UUID of the document
    """
    client = get_client()
    try:
        result = await client.get_knowledge_document_download(document_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def upload_knowledge_document(
    group_id: str,
    name: str,
    content: str,
    content_type: str = "text/plain",
) -> str:
    """Upload a document to a knowledge group.

    Args:
        group_id: The UUID of the knowledge group
        name: Document name
        content: Document content (text)
        content_type: MIME type (default: text/plain)
    """
    client = get_client()
    try:
        result = await client.upload_knowledge_document(
            group_id=group_id,
            name=name,
            content=content,
            content_type=content_type,
        )
        return f"Uploaded document '{name}' with ID: {result.get('id')}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def update_knowledge_document(
    document_id: str,
    name: str | None = None,
) -> str:
    """Update a knowledge document.

    Args:
        document_id: The UUID of the document to update
        name: New document name
    """
    client = get_client()
    try:
        result = await client.update_knowledge_document(
            document_id=document_id,
            name=name,
        )
        return f"Updated document: {result.get('name', document_id)}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def delete_knowledge_document(document_id: str) -> str:
    """Delete a knowledge document by ID.

    Args:
        document_id: The UUID of the document to delete
    """
    client = get_client()
    try:
        await client.delete_knowledge_document(document_id)
        return f"Deleted document: {document_id}"
    except AnamAPIError as e:
        return format_error(e)


# ─────────────────────────────────────────────────────────────────────────────────
# LLMs
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_llms(
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """List all available LLMs.

    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 100)
    """
    client = get_client()
    try:
        result = await client.list_llms(page=page, per_page=per_page or DEFAULT_PER_PAGE)

        if isinstance(result, list):
            items = result
            total = len(items)
        else:
            items = result.get("data", [])
            meta = result.get("meta", {})
            total = meta.get("total", len(items))

        if not items:
            return "No LLMs found."

        lines = [f"LLMs ({total} total):\n"]
        lines.append(f"{'Name':<30} {'Provider':<15} {'ID'}")
        lines.append("-" * 85)

        for item in items:
            name = item.get("name", "unnamed")[:29]
            provider = item.get("provider", "-")[:14]
            item_id = item.get("id", "")
            lines.append(f"{name:<30} {provider:<15} {item_id}")

        return "\n".join(lines)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def get_llm(llm_id: str) -> str:
    """Get details of a specific LLM by ID.

    Args:
        llm_id: The UUID of the LLM to retrieve
    """
    client = get_client()
    try:
        result = await client.get_llm(llm_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def create_llm(
    name: str,
    provider: str,
    model: str,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Create a custom LLM configuration.

    Args:
        name: Display name for the LLM
        provider: LLM provider (e.g., "openai", "anthropic")
        model: Model name (e.g., "gpt-4", "claude-3")
        api_key: API key for the provider
        base_url: Custom base URL (for self-hosted models)
        temperature: Sampling temperature
        max_tokens: Maximum output tokens
    """
    client = get_client()
    try:
        result = await client.create_llm(
            name=name,
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return f"Created LLM '{name}' with ID: {result.get('id')}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def update_llm(
    llm_id: str,
    name: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Update an LLM configuration. Only provide the fields you want to change.

    Args:
        llm_id: The UUID of the LLM to update
        name: New display name
        temperature: New sampling temperature
        max_tokens: New maximum output tokens
    """
    client = get_client()
    try:
        result = await client.update_llm(
            llm_id=llm_id,
            name=name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return f"Updated LLM: {result.get('name', llm_id)}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def delete_llm(llm_id: str) -> str:
    """Delete an LLM by ID.

    Args:
        llm_id: The UUID of the LLM to delete
    """
    client = get_client()
    try:
        await client.delete_llm(llm_id)
        return f"Deleted LLM: {llm_id}"
    except AnamAPIError as e:
        return format_error(e)


# ─────────────────────────────────────────────────────────────────────────────────
# Share Links
# ─────────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_share_links(
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """List all share links in your organization.

    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 100)
    """
    client = get_client()
    try:
        result = await client.list_share_links(page=page, per_page=per_page or DEFAULT_PER_PAGE)
        items = result.get("data", [])
        meta = result.get("meta", {})

        if not items:
            return "No share links found."

        lines = [f"Share Links ({meta.get('total', len(items))} total):\n"]
        lines.append(f"{'Name':<25} {'Active':<8} {'ID'}")
        lines.append("-" * 80)

        for item in items:
            name = item.get("name", "unnamed")[:24]
            is_active = "Yes" if item.get("isActive", True) else "No"
            item_id = item.get("id", "")
            lines.append(f"{name:<25} {is_active:<8} {item_id}")

        if meta.get("lastPage", 1) > 1:
            lines.append(f"\nPage {meta.get('currentPage', 1)} of {meta.get('lastPage', 1)}")

        return "\n".join(lines)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def get_share_link(link_id: str) -> str:
    """Get details of a specific share link by ID.

    Args:
        link_id: The UUID of the share link to retrieve
    """
    client = get_client()
    try:
        result = await client.get_share_link(link_id)
        return format_response(result)
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def create_share_link(
    persona_id: str,
    name: str | None = None,
    expires_at: str | None = None,
    max_uses: int | None = None,
) -> str:
    """Create a new share link for a persona.

    Args:
        persona_id: The UUID of the persona to share
        name: Optional name for the link
        expires_at: Expiration timestamp (ISO 8601)
        max_uses: Maximum number of uses
    """
    client = get_client()
    try:
        result = await client.create_share_link(
            persona_id=persona_id,
            name=name,
            expires_at=expires_at,
            max_uses=max_uses,
        )
        link_url = result.get("url", "")
        return f"Created share link with ID: {result.get('id')}\nURL: {link_url}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def update_share_link(
    link_id: str,
    name: str | None = None,
    expires_at: str | None = None,
    max_uses: int | None = None,
    is_active: bool | None = None,
) -> str:
    """Update a share link. Only provide the fields you want to change.

    Args:
        link_id: The UUID of the share link to update
        name: New name
        expires_at: New expiration timestamp (ISO 8601)
        max_uses: New maximum number of uses
        is_active: Whether the link is active
    """
    client = get_client()
    try:
        result = await client.update_share_link(
            link_id=link_id,
            name=name,
            expires_at=expires_at,
            max_uses=max_uses,
            is_active=is_active,
        )
        return f"Updated share link: {result.get('name', link_id)}"
    except AnamAPIError as e:
        return format_error(e)


@mcp.tool()
async def delete_share_link(link_id: str) -> str:
    """Delete a share link by ID.

    Args:
        link_id: The UUID of the share link to delete
    """
    client = get_client()
    try:
        await client.delete_share_link(link_id)
        return f"Deleted share link: {link_id}"
    except AnamAPIError as e:
        return format_error(e)


# ─────────────────────────────────────────────────────────────────────────────
# Text-to-Avatar (Internal Testing)
# ─────────────────────────────────────────────────────────────────────────────

# Text-to-Avatar service configuration
TEXT_TO_AVATAR_BASE_URL = os.getenv(
    "TEXT_TO_AVATAR_URL", "https://anam-org--text-to-avatar-api.modal.run"
)


@mcp.tool()
async def generate_avatar_video(
    script: str,
    persona_id: str | None = None,
    avatar_id: str | None = None,
    voice_id: str | None = None,
    avatar_model: str = "cara-3",
    poll_interval: float = 3.0,
    max_wait: float = 600.0,
) -> str:
    """Generate an avatar video from a text script.

    **INTERNAL TESTING ONLY** - This feature is in early access.
    Contact support@anam.ai for access.

    Creates an MP4 video of an avatar speaking the provided script.
    The video generation runs asynchronously and may take 30-120 seconds
    depending on script length.

    Args:
        script: The text for the avatar to speak
        persona_id: Use a saved persona (provide this OR avatar_id + voice_id)
        avatar_id: Avatar ID for ephemeral session (requires voice_id)
        voice_id: Voice ID for ephemeral session (requires avatar_id)
        avatar_model: Avatar model to use (default: cara-3)
        poll_interval: Seconds between status checks (default: 3.0)
        max_wait: Maximum seconds to wait for completion (default: 600.0)

    Stock Avatars (use with voice_id):
        Female:
        - Liv: 071b0286-4cce-4808-bee2-e642f1062de3
        - Mia: edf6fdcb-acab-44b8-b974-ded72665ee26
        - Sophie: 6dbc1e47-7768-403e-878a-94d7fcc3677b
        - Bella: dc9aa3e1-32f2-499e-9921-ecabac1076fc
        - Julia: edcb8f1a-334f-4cdb-871c-5c513db806a7
        - Anne: 27e12daa-50fc-4384-93c2-ebca73f1f78d
        - Layla: ae2ea8c1-db28-47e3-b6ea-493e4ed3c554
        Male:
        - Gabriel: 6cc28442-cccd-42a8-b6e4-24b7210a09c5
        - Finn: 8a339c9f-0666-46bd-ab27-e90acd0409dc
        - Hunter: ecfb2ddb-80ec-4526-88a7-299a4738957c
        - Kevin: ccf00c0e-7302-455b-ace2-057e0cf58127
        - Richard: 19d18eb0-5346-4d50-a77f-26b3723ed79d
        - William: 81b70170-2e80-4e4b-a6fb-e04ac110dc4b

    Recommended Voices:
        Female: Jessica - b138c2a2-ba66-4887-95d5-1a57093fc92d
        Male: Adam - e54745c7-9439-44c3-b61a-193b42cce5bd

    Returns:
        Download URL for the generated video, or error message
    """
    import asyncio

    import httpx

    api_key = os.getenv("ANAM_API_KEY")
    if not api_key:
        return "Error: ANAM_API_KEY environment variable is required"

    # Validate input
    if not script or not script.strip():
        return "Error: script is required and cannot be empty"

    if not persona_id and not (avatar_id and voice_id):
        return "Error: Provide either persona_id OR both avatar_id and voice_id"

    # Build request payload
    payload: dict[str, Any] = {"script": script}
    if persona_id:
        payload["persona_id"] = persona_id
    else:
        payload["avatar_id"] = avatar_id
        payload["voice_id"] = voice_id
        payload["avatar_model"] = avatar_model

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Submit the job
            response = await client.post(
                f"{TEXT_TO_AVATAR_BASE_URL}/generate",
                headers=headers,
                json=payload,
            )

            if response.status_code == 401:
                return "Error: Invalid API key for text-to-avatar service"
            if response.status_code != 200:
                return f"Error: Failed to submit job - {response.text}"

            job = response.json()
            call_id = job.get("call_id")
            if not call_id:
                return "Error: No call_id returned from service"

            # Poll for completion
            elapsed = 0.0
            while elapsed < max_wait:
                status_response = await client.get(
                    f"{TEXT_TO_AVATAR_BASE_URL}/status/{call_id}",
                    headers=headers,
                )

                if status_response.status_code != 200:
                    return f"Error: Failed to check status - {status_response.text}"

                status_data = status_response.json()
                status = status_data.get("status")

                if status == "complete":
                    download_url = f"{TEXT_TO_AVATAR_BASE_URL}/download/{call_id}"
                    return (
                        f"Video generated successfully!\n\n"
                        f"Download URL: {download_url}\n\n"
                        f"Note: Video is available for 7 days."
                    )

                if status == "failed":
                    error = status_data.get("error", "Unknown error")
                    return f"Error: Video generation failed - {error}"

                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

            return f"Error: Timed out waiting for video generation (waited {max_wait}s)"

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# Recall AI - Meeting Avatars
# ─────────────────────────────────────────────────────────────────────────────

# Meet page URL - renders avatar video for Recall to use as bot camera
MEET_PAGE_BASE_URL = os.getenv("MEET_PAGE_URL", "https://meet.anam.ai")


def format_recall_error(e: RecallAPIError) -> str:
    """Format a Recall API error as a user-friendly message."""
    return f"Error: {e.message}"


def format_bot_status(bot: dict) -> str:
    """Format bot status as readable output."""
    status_code = bot.get("status_changes", [{}])[-1].get("code", "unknown")
    lines = [
        f"Bot ID: {bot.get('id')}",
        f"Status: {status_code}",
        f"Meeting URL: {bot.get('meeting_url', {}).get('url', 'N/A')}",
        f"Bot Name: {bot.get('bot_name', 'N/A')}",
    ]
    if bot.get("join_at"):
        lines.append(f"Scheduled Join: {bot.get('join_at')}")
    return "\n".join(lines)


@mcp.tool()
async def add_avatar_to_meeting(
    meeting_url: str,
    avatar_id: str,
    voice_id: str,
    system_prompt: str,
    bot_name: str = "Anam Avatar",
    llm_id: str | None = None,
    avatar_model: str = "cara-3",
) -> str:
    """Add an Anam avatar to a video meeting (Zoom, Google Meet, Teams).

    Creates an ephemeral session and deploys a Recall bot that shows
    the avatar as its camera feed. The avatar can hear and respond
    to meeting participants.

    Args:
        meeting_url: Video conference URL (e.g., https://meet.google.com/abc-defg-hij)
        avatar_id: Anam avatar ID. Use search_avatars to find one.
        voice_id: Anam voice ID. Use search_voices to find one.
        system_prompt: Instructions for the avatar's personality and behavior.
        bot_name: Name shown in the meeting participant list (default: "Anam Avatar")
        llm_id: Optional LLM ID. Defaults to GPT-4o-mini.
        avatar_model: Avatar model ("cara-2" or "cara-3", default: cara-3)

    Returns:
        Bot ID and status information
    """
    import os

    # Check for Recall API key first
    if not os.getenv("RECALL_API_KEY"):
        return "Error: RECALL_API_KEY environment variable is required for meeting avatars"

    # Step 1: Create ephemeral session token via Anam API
    anam_client = get_client()
    try:
        token_result = await anam_client.create_session_token(
            name=bot_name,
            avatar_id=avatar_id,
            voice_id=voice_id,
            system_prompt=system_prompt,
            llm_id=llm_id,
            avatar_model=avatar_model,
        )
        session_token = token_result.get("sessionToken")
        if not session_token:
            return "Error: Failed to create session token"
    except AnamAPIError as e:
        return f"Error creating session: {format_error(e)}"

    # Step 2: Build meet page URL with token
    meet_page_url = f"{MEET_PAGE_BASE_URL}/?token={session_token}"

    # Step 3: Create Recall bot
    try:
        recall_client = get_recall_client()
        bot = await recall_client.create_bot(
            meeting_url=meeting_url,
            output_media_url=meet_page_url,
            bot_name=bot_name,
        )

        bot_id = bot.get("id")
        return (
            f"Avatar joining meeting!\n\n"
            f"Bot ID: {bot_id}\n"
            f"Meeting: {meeting_url}\n"
            f"Bot Name: {bot_name}\n\n"
            f"Use get_meeting_bot_status('{bot_id}') to check status.\n"
            f"Use remove_avatar_from_meeting('{bot_id}') to leave."
        )
    except RecallAPIError as e:
        return format_recall_error(e)


@mcp.tool()
async def get_meeting_bot_status(bot_id: str) -> str:
    """Check the status of a Recall meeting bot.

    Args:
        bot_id: The Recall bot ID returned by add_avatar_to_meeting

    Returns:
        Bot status including meeting URL, join status, etc.
    """
    import os

    if not os.getenv("RECALL_API_KEY"):
        return "Error: RECALL_API_KEY environment variable is required"

    try:
        recall_client = get_recall_client()
        bot = await recall_client.get_bot(bot_id)
        return format_bot_status(bot)
    except RecallAPIError as e:
        return format_recall_error(e)


@mcp.tool()
async def remove_avatar_from_meeting(bot_id: str) -> str:
    """Remove an avatar from a video meeting.

    Makes the Recall bot leave the meeting gracefully.

    Args:
        bot_id: The Recall bot ID returned by add_avatar_to_meeting
    """
    import os

    if not os.getenv("RECALL_API_KEY"):
        return "Error: RECALL_API_KEY environment variable is required"

    try:
        recall_client = get_recall_client()
        await recall_client.leave_meeting(bot_id)
        return f"Avatar left the meeting (bot: {bot_id})"
    except RecallAPIError as e:
        return format_recall_error(e)


@mcp.tool()
async def list_meeting_bots(limit: int = 20) -> str:
    """List all Recall meeting bots.

    Shows recent bots including their status and meeting URLs.

    Args:
        limit: Maximum number of bots to return (default: 20)
    """
    import os

    if not os.getenv("RECALL_API_KEY"):
        return "Error: RECALL_API_KEY environment variable is required"

    try:
        recall_client = get_recall_client()
        result = await recall_client.list_bots(limit=limit)

        bots = result.get("results", [])
        if not bots:
            return "No meeting bots found."

        lines = [f"Meeting Bots ({len(bots)}):\n"]
        lines.append(f"{'Status':<15} {'Bot Name':<20} {'ID'}")
        lines.append("-" * 75)

        for bot in bots:
            status_changes = bot.get("status_changes", [])
            status = status_changes[-1].get("code", "unknown")[:14] if status_changes else "unknown"
            name = bot.get("bot_name", "unnamed")[:19]
            bot_id = bot.get("id", "")
            lines.append(f"{status:<15} {name:<20} {bot_id}")

        return "\n".join(lines)
    except RecallAPIError as e:
        return format_recall_error(e)


def main():
    """Run the Anam MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
