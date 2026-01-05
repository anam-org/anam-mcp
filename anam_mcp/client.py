"""Async HTTP client wrapper for the Anam AI API."""

from __future__ import annotations

import os
from typing import Any

import httpx


class AnamAPIError(Exception):
    """Exception raised when the Anam API returns an error."""

    def __init__(self, status_code: int, message: str, details: dict | None = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{status_code}] {message}")


class AnamClient:
    """Async client for interacting with the Anam AI API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key or os.getenv("ANAM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANAM_API_KEY is required. Set it as an environment variable or pass it to the client."
            )
        self.base_url = base_url or os.getenv("ANAM_API_URL", "https://api.anam.ai")

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Anam API."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers=self._get_headers(),
                json=json,
                params=params,
                timeout=30.0,
            )

            if response.status_code >= 400:
                # Try to parse error details from response
                try:
                    error_data = response.json()
                    message = error_data.get("message", error_data.get("error", str(error_data)))
                    details = error_data
                except Exception:
                    message = response.text or f"HTTP {response.status_code}"
                    details = {}

                # Provide friendly error messages for common cases
                if response.status_code == 401:
                    message = "Invalid API key. Check your ANAM_API_KEY."
                elif response.status_code == 403:
                    message = f"Access denied: {message}"
                elif response.status_code == 404:
                    message = f"Not found: {path}"
                elif response.status_code == 429:
                    message = "Rate limit exceeded. Please wait and try again."

                raise AnamAPIError(response.status_code, message, details)

            return response.json()

    # ─────────────────────────────────────────────────────────────────────────────
    # Personas
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_personas(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List all personas in the account."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request("GET", "/v1/personas", params=params or None)

    async def get_persona(self, persona_id: str) -> dict[str, Any]:
        """Get a persona by ID."""
        return await self._request("GET", f"/v1/personas/{persona_id}")

    async def create_persona(
        self,
        name: str,
        avatar_id: str,
        voice_id: str,
        system_prompt: str,
        llm_id: str = "0934d97d-0c3a-4f33-91b0-5e136a0ef466",
        tool_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new persona."""
        payload = {
            "name": name,
            "avatarId": avatar_id,
            "voiceId": voice_id,
            "llmId": llm_id,
            "systemPrompt": system_prompt,
        }
        if tool_ids:
            payload["toolIds"] = tool_ids
        return await self._request("POST", "/v1/personas", json=payload)

    async def update_persona(
        self,
        persona_id: str,
        name: str | None = None,
        avatar_id: str | None = None,
        voice_id: str | None = None,
        system_prompt: str | None = None,
        llm_id: str | None = None,
        tool_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing persona."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if avatar_id is not None:
            payload["avatarId"] = avatar_id
        if voice_id is not None:
            payload["voiceId"] = voice_id
        if system_prompt is not None:
            payload["systemPrompt"] = system_prompt
        if llm_id is not None:
            payload["llmId"] = llm_id
        if tool_ids is not None:
            payload["toolIds"] = tool_ids
        return await self._request("PUT", f"/v1/personas/{persona_id}", json=payload)

    async def delete_persona(self, persona_id: str) -> dict[str, Any]:
        """Delete a persona by ID."""
        return await self._request("DELETE", f"/v1/personas/{persona_id}")

    # ─────────────────────────────────────────────────────────────────────────────
    # Avatars
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_avatars(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List all available avatars."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request("GET", "/v1/avatars", params=params or None)

    async def create_avatar(
        self,
        name: str,
        image_url: str | None = None,
    ) -> dict[str, Any]:
        """Create a new avatar from an image URL (enterprise/pro only)."""
        payload = {"name": name}
        if image_url:
            payload["imageUrl"] = image_url
        return await self._request("POST", "/v1/avatars", json=payload)

    async def update_avatar(
        self,
        avatar_id: str,
        name: str,
    ) -> dict[str, Any]:
        """Update an avatar's display name."""
        return await self._request(
            "PUT", f"/v1/avatars/{avatar_id}", json={"name": name}
        )

    async def delete_avatar(self, avatar_id: str) -> dict[str, Any]:
        """Delete an avatar by ID."""
        return await self._request("DELETE", f"/v1/avatars/{avatar_id}")

    # ─────────────────────────────────────────────────────────────────────────────
    # Voices
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_voices(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List all available voices."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request("GET", "/v1/voices", params=params or None)

    # ─────────────────────────────────────────────────────────────────────────────
    # Tools
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_tools(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List all tools in the organization."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request("GET", "/v1/tools", params=params or None)

    async def create_webhook_tool(
        self,
        name: str,
        description: str,
        url: str,
        method: str = "POST",
        headers: dict[str, str] | None = None,
        parameters: dict[str, Any] | None = None,
        await_response: bool = True,
    ) -> dict[str, Any]:
        """Create a new webhook tool."""
        payload = {
            "type": "server",
            "subtype": "webhook",
            "name": name,
            "description": description,
            "url": url,
            "method": method,
            "awaitResponse": await_response,
        }
        if headers:
            payload["headers"] = headers
        if parameters:
            payload["parameters"] = parameters
        return await self._request("POST", "/v1/tools", json=payload)

    async def create_knowledge_tool(
        self,
        name: str,
        description: str,
        folder_ids: list[str],
    ) -> dict[str, Any]:
        """Create a new knowledge/RAG tool."""
        payload = {
            "type": "server",
            "subtype": "knowledge",
            "name": name,
            "description": description,
            "folderIds": folder_ids,
        }
        return await self._request("POST", "/v1/tools", json=payload)

    async def delete_tool(self, tool_id: str) -> dict[str, Any]:
        """Delete a tool by ID."""
        return await self._request("DELETE", f"/v1/tools/{tool_id}")

    # ─────────────────────────────────────────────────────────────────────────────
    # Sessions
    # ─────────────────────────────────────────────────────────────────────────────

    async def create_session_token(
        self,
        persona_id: str | None = None,
        name: str | None = None,
        avatar_id: str | None = None,
        voice_id: str | None = None,
        system_prompt: str | None = None,
        llm_id: str | None = None,
        language_code: str | None = None,
        max_session_length_seconds: int | None = None,
    ) -> dict[str, Any]:
        """
        Create a session token for connecting to an Anam persona.

        Use EITHER persona_id (for saved personas) OR the individual config fields
        (for ephemeral sessions).
        """
        if persona_id:
            persona_config = {"personaId": persona_id}
        else:
            persona_config = {}
            if name:
                persona_config["name"] = name
            if avatar_id:
                persona_config["avatarId"] = avatar_id
            if voice_id:
                persona_config["voiceId"] = voice_id
            if system_prompt:
                persona_config["systemPrompt"] = system_prompt
            if llm_id:
                persona_config["llmId"] = llm_id
            if language_code:
                persona_config["languageCode"] = language_code
            if max_session_length_seconds:
                persona_config["maxSessionLengthSeconds"] = max_session_length_seconds

        return await self._request(
            "POST", "/v1/auth/session-token", json={"personaConfig": persona_config}
        )

    # ─────────────────────────────────────────────────────────────────────────────
    # Knowledge Base
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_knowledge_folders(self) -> list[dict[str, Any]]:
        """List all knowledge folders."""
        return await self._request("GET", "/v1/knowledge/groups")

    async def create_knowledge_folder(
        self,
        name: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new knowledge folder."""
        payload = {"name": name}
        if description:
            payload["description"] = description
        return await self._request("POST", "/v1/knowledge/groups", json=payload)
