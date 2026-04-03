"""Unit tests for request payload compatibility."""

from __future__ import annotations

import httpx
import pytest

from anam_mcp.client import AnamClient


@pytest.mark.asyncio
async def test_create_avatar_uses_display_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Create avatar requests should match the public API schema."""
    captured: dict[str, object] = {}

    async def fake_request(self, method, url, headers=None, json=None, params=None, timeout=None):
        captured["method"] = method
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        request = httpx.Request(method, url)
        return httpx.Response(200, json={"id": "avatar-123"}, request=request)

    monkeypatch.setattr(httpx.AsyncClient, "request", fake_request)

    client = AnamClient(api_key="test-key")
    result = await client.create_avatar(
        name="Dream11 - chander-pichai",
        image_url="https://example.com/avatar.png",
    )

    assert result == {"id": "avatar-123"}
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.anam.ai/v1/avatars"
    assert captured["json"] == {
        "displayName": "Dream11 - chander-pichai",
        "imageUrl": "https://example.com/avatar.png",
    }
    assert captured["timeout"] == 120.0


@pytest.mark.asyncio
async def test_update_avatar_prefers_display_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Update avatar requests should only send the supported display name field."""
    captured: dict[str, object] = {}

    async def fake_request(self, method, url, headers=None, json=None, params=None, timeout=None):
        captured["method"] = method
        captured["url"] = url
        captured["json"] = json
        request = httpx.Request(method, url)
        return httpx.Response(200, json={"id": "avatar-123"}, request=request)

    monkeypatch.setattr(httpx.AsyncClient, "request", fake_request)

    client = AnamClient(api_key="test-key")
    result = await client.update_avatar(
        avatar_id="avatar-123",
        name="old-name",
        display_name="new-display-name",
    )

    assert result == {"id": "avatar-123"}
    assert captured["method"] == "PUT"
    assert captured["url"] == "https://api.anam.ai/v1/avatars/avatar-123"
    assert captured["json"] == {"displayName": "new-display-name"}
