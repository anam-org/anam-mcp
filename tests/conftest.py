"""Pytest configuration and fixtures for anam-mcp tests."""

from __future__ import annotations

import os
import uuid
from typing import AsyncGenerator

import pytest

from anam_mcp.client import AnamClient


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests that call the real Anam API (requires ANAM_API_KEY)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip integration tests if ANAM_API_KEY is not set."""
    if os.getenv("ANAM_API_KEY"):
        return

    skip_integration = pytest.mark.skip(reason="ANAM_API_KEY not set")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture
def api_key() -> str:
    """Get the API key from environment."""
    key = os.getenv("ANAM_API_KEY")
    if not key:
        pytest.skip("ANAM_API_KEY not set")
    return key


@pytest.fixture
def client(api_key: str) -> AnamClient:
    """Create an Anam API client."""
    return AnamClient(api_key=api_key)


@pytest.fixture
def test_prefix() -> str:
    """Generate a unique prefix for test resources to avoid collisions."""
    return f"test_{uuid.uuid4().hex[:8]}"


# ─────────────────────────────────────────────────────────────────────────────────
# Pagination helper
# ─────────────────────────────────────────────────────────────────────────────────


async def fetch_all_pages(
    fetch_fn,
    per_page: int = 100,
) -> list[dict]:
    """Fetch all items across all pages from a paginated endpoint.

    Args:
        fetch_fn: Async function that takes page and per_page kwargs
        per_page: Number of items per page

    Returns:
        List of all items from all pages
    """
    all_items = []
    page = 1
    while True:
        result = await fetch_fn(page=page, per_page=per_page)
        if not isinstance(result, dict):
            break
        items = result.get("data") or []
        all_items.extend([i for i in items if i is not None])
        meta = result.get("meta") or {}
        if page >= (meta.get("lastPage") or 1):
            break
        page += 1
    return all_items


# ─────────────────────────────────────────────────────────────────────────────────
# Resource lookup helpers (for getting valid IDs for tests)
# ─────────────────────────────────────────────────────────────────────────────────


@pytest.fixture
async def stock_avatar_id(client: AnamClient) -> str:
    """Get a valid stock avatar ID for tests."""
    result = await client.list_avatars(per_page=10)
    items = result.get("data", [])
    # Find a stock avatar (one without createdByOrganizationId)
    for item in items:
        if item.get("createdByOrganizationId") is None:
            return item["id"]
    pytest.skip("No stock avatars available")


@pytest.fixture
async def stock_voice_id(client: AnamClient) -> str:
    """Get a valid stock voice ID for tests."""
    result = await client.list_voices(per_page=10)
    items = result.get("data", [])
    if items:
        return items[0]["id"]
    pytest.skip("No voices available")


@pytest.fixture
async def default_llm_id() -> str:
    """Get the default LLM ID."""
    return "0934d97d-0c3a-4f33-91b0-5e136a0ef466"


# ─────────────────────────────────────────────────────────────────────────────────
# Cleanup tracking fixtures
# ─────────────────────────────────────────────────────────────────────────────────


@pytest.fixture
async def cleanup_personas(client: AnamClient) -> AsyncGenerator[list[str], None]:
    """Track persona IDs to clean up after tests."""
    created_ids: list[str] = []
    yield created_ids
    # Cleanup: delete all created personas
    for persona_id in created_ids:
        try:
            await client.delete_persona(persona_id)
        except Exception:
            pass  # Best effort cleanup


@pytest.fixture
async def cleanup_tools(client: AnamClient) -> AsyncGenerator[list[str], None]:
    """Track tool IDs to clean up after tests."""
    created_ids: list[str] = []
    yield created_ids
    for tool_id in created_ids:
        try:
            await client.delete_tool(tool_id)
        except Exception:
            pass


@pytest.fixture
async def cleanup_knowledge_groups(client: AnamClient) -> AsyncGenerator[list[str], None]:
    """Track knowledge group IDs to clean up after tests."""
    created_ids: list[str] = []
    yield created_ids
    for group_id in created_ids:
        try:
            await client.delete_knowledge_group(group_id)
        except Exception:
            pass


@pytest.fixture
async def cleanup_avatars(client: AnamClient) -> AsyncGenerator[list[str], None]:
    """Track avatar IDs to clean up after tests."""
    created_ids: list[str] = []
    yield created_ids
    for avatar_id in created_ids:
        try:
            await client.delete_avatar(avatar_id)
        except Exception:
            pass


@pytest.fixture
async def cleanup_voices(client: AnamClient) -> AsyncGenerator[list[str], None]:
    """Track voice IDs to clean up after tests."""
    created_ids: list[str] = []
    yield created_ids
    for voice_id in created_ids:
        try:
            await client.delete_voice(voice_id)
        except Exception:
            pass


@pytest.fixture
async def cleanup_llms(client: AnamClient) -> AsyncGenerator[list[str], None]:
    """Track LLM IDs to clean up after tests."""
    created_ids: list[str] = []
    yield created_ids
    for llm_id in created_ids:
        try:
            await client.delete_llm(llm_id)
        except Exception:
            pass


@pytest.fixture
async def cleanup_share_links(client: AnamClient) -> AsyncGenerator[list[str], None]:
    """Track share link IDs to clean up after tests."""
    created_ids: list[str] = []
    yield created_ids
    for link_id in created_ids:
        try:
            await client.delete_share_link(link_id)
        except Exception:
            pass
