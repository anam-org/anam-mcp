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

            # Handle empty responses (e.g., 204 No Content from DELETE)
            if response.status_code == 204 or not response.content:
                return {}

            # Ensure we always return a dict, even if API returns null/empty
            result = response.json()
            if result is None:
                return {}
            return result

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

    async def get_avatar(self, avatar_id: str) -> dict[str, Any]:
        """Get an avatar by ID."""
        return await self._request("GET", f"/v1/avatars/{avatar_id}")

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
        name: str | None = None,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        """Update an avatar."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if display_name is not None:
            payload["displayName"] = display_name
        return await self._request("PUT", f"/v1/avatars/{avatar_id}", json=payload)

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

    async def get_voice(self, voice_id: str) -> dict[str, Any]:
        """Get a voice by ID."""
        return await self._request("GET", f"/v1/voices/{voice_id}")

    async def create_voice(
        self,
        display_name: str,
        provider: str,
        provider_voice_id: str,
        gender: str | None = None,
        country: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a custom voice."""
        payload = {
            "displayName": display_name,
            "provider": provider,
            "providerVoiceId": provider_voice_id,
        }
        if gender is not None:
            payload["gender"] = gender
        if country is not None:
            payload["country"] = country
        if description is not None:
            payload["description"] = description
        return await self._request("POST", "/v1/voices", json=payload)

    async def update_voice(
        self,
        voice_id: str,
        display_name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a voice."""
        payload = {}
        if display_name is not None:
            payload["displayName"] = display_name
        if description is not None:
            payload["description"] = description
        return await self._request("PUT", f"/v1/voices/{voice_id}", json=payload)

    async def delete_voice(self, voice_id: str) -> dict[str, Any]:
        """Delete a voice by ID."""
        return await self._request("DELETE", f"/v1/voices/{voice_id}")

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

    async def get_tool(self, tool_id: str) -> dict[str, Any]:
        """Get a tool by ID."""
        return await self._request("GET", f"/v1/tools/{tool_id}")

    async def update_tool(
        self,
        tool_id: str,
        name: str | None = None,
        description: str | None = None,
        url: str | None = None,
        method: str | None = None,
        await_response: bool | None = None,
    ) -> dict[str, Any]:
        """Update a tool."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if url is not None:
            payload["url"] = url
        if method is not None:
            payload["method"] = method
        if await_response is not None:
            payload["awaitResponse"] = await_response
        return await self._request("PUT", f"/v1/tools/{tool_id}", json=payload)

    async def delete_tool(self, tool_id: str) -> dict[str, Any]:
        """Delete a tool by ID."""
        return await self._request("DELETE", f"/v1/tools/{tool_id}")

    # ─────────────────────────────────────────────────────────────────────────────
    # Sessions
    # ─────────────────────────────────────────────────────────────────────────────

    # Default IDs for ephemeral sessions
    DEFAULT_LLM_ID = "7736a22f-2d79-4720-952c-25fdca55ad40"  # GPT-4o-mini
    DEFAULT_VOICE_ID = "6bfbe25a-979d-40f3-a92b-5394170af54b"  # "Cara" - English female
    DEFAULT_AVATAR_ID = "30fa96d0-26c4-4e55-94a0-517025942e18"  # "Cara" avatar

    async def create_session_token(
        self,
        persona_id: str | None = None,
        name: str | None = None,
        avatar_id: str | None = None,
        voice_id: str | None = None,
        system_prompt: str | None = None,
        llm_id: str | None = None,
        avatar_model: str = "cara-3",
        max_session_length_seconds: int | None = None,
        skip_greeting: bool | None = None,
    ) -> dict[str, Any]:
        """
        Create a session token for connecting to an Anam persona.

        Use EITHER persona_id (for saved personas) OR the individual config fields
        (for ephemeral sessions).

        For ephemeral sessions:
        - avatarModel defaults to "cara-3"
        - llmId defaults to GPT-4o-mini
        - voiceId defaults to "Cara" voice (REQUIRED for ephemeral)
        - avatarId defaults to "Cara" avatar
        """
        if persona_id:
            persona_config = {"personaId": persona_id}
        else:
            # Ephemeral session config
            # voiceId is REQUIRED for ephemeral sessions - server rejects without it
            persona_config: dict[str, Any] = {
                "avatarModel": avatar_model,
                "llmId": llm_id or self.DEFAULT_LLM_ID,
                "voiceId": voice_id or self.DEFAULT_VOICE_ID,
                "avatarId": avatar_id or self.DEFAULT_AVATAR_ID,
            }
            if name:
                persona_config["name"] = name
            if system_prompt:
                persona_config["systemPrompt"] = system_prompt
            if max_session_length_seconds:
                persona_config["maxSessionLengthSeconds"] = max_session_length_seconds
            if skip_greeting is not None:
                persona_config["skipGreeting"] = skip_greeting

        return await self._request(
            "POST", "/v1/auth/session-token", json={"personaConfig": persona_config}
        )

    async def list_sessions(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List all sessions."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request("GET", "/v1/sessions", params=params or None)

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Get a session by ID."""
        return await self._request("GET", f"/v1/sessions/{session_id}")

    async def get_session_recording(self, session_id: str) -> dict[str, Any]:
        """Get a session recording."""
        return await self._request("GET", f"/v1/sessions/{session_id}/recording")

    # ─────────────────────────────────────────────────────────────────────────────
    # Knowledge Base
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_knowledge_folders(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List all knowledge folders (groups)."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request("GET", "/v1/knowledge/groups", params=params or None)

    async def get_knowledge_group(self, group_id: str) -> dict[str, Any]:
        """Get a knowledge group by ID."""
        return await self._request("GET", f"/v1/knowledge/groups/{group_id}")

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

    async def update_knowledge_group(
        self,
        group_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a knowledge group."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        return await self._request("PUT", f"/v1/knowledge/groups/{group_id}", json=payload)

    async def delete_knowledge_group(self, group_id: str) -> dict[str, Any]:
        """Delete a knowledge group by ID."""
        return await self._request("DELETE", f"/v1/knowledge/groups/{group_id}")

    async def search_knowledge_group(
        self,
        group_id: str,
        query: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Search within a knowledge group."""
        payload = {"query": query}
        if limit is not None:
            payload["limit"] = limit
        return await self._request("POST", f"/v1/knowledge/groups/{group_id}/search", json=payload)

    # ─────────────────────────────────────────────────────────────────────────────
    # Knowledge Documents
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_knowledge_documents(
        self,
        group_id: str,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List documents in a knowledge group."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request(
            "GET", f"/v1/knowledge/groups/{group_id}/documents", params=params or None
        )

    async def get_knowledge_document(self, document_id: str) -> dict[str, Any]:
        """Get a knowledge document by ID."""
        return await self._request("GET", f"/v1/knowledge/documents/{document_id}")

    async def get_knowledge_document_download(self, document_id: str) -> dict[str, Any]:
        """Get download URL for a knowledge document."""
        return await self._request("GET", f"/v1/knowledge/documents/{document_id}/download")

    async def upload_knowledge_document(
        self,
        group_id: str,
        name: str,
        content: str,
        content_type: str = "text/plain",
    ) -> dict[str, Any]:
        """Upload a document to a knowledge group.

        Note: For file uploads, use the appropriate content_type.
        This method handles text content directly.
        """
        payload = {
            "name": name,
            "content": content,
            "contentType": content_type,
        }
        return await self._request(
            "POST", f"/v1/knowledge/groups/{group_id}/documents", json=payload
        )

    async def update_knowledge_document(
        self,
        document_id: str,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Update a knowledge document."""
        payload = {}
        if name is not None:
            payload["name"] = name
        return await self._request("PUT", f"/v1/knowledge/documents/{document_id}", json=payload)

    async def delete_knowledge_document(self, document_id: str) -> dict[str, Any]:
        """Delete a knowledge document by ID."""
        return await self._request("DELETE", f"/v1/knowledge/documents/{document_id}")

    # ─────────────────────────────────────────────────────────────────────────────
    # LLMs
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_llms(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List all available LLMs."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request("GET", "/v1/llms", params=params or None)

    async def get_llm(self, llm_id: str) -> dict[str, Any]:
        """Get an LLM by ID."""
        return await self._request("GET", f"/v1/llms/{llm_id}")

    async def create_llm(
        self,
        name: str,
        provider: str,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Create a custom LLM configuration."""
        payload = {
            "name": name,
            "provider": provider,
            "model": model,
        }
        if api_key is not None:
            payload["apiKey"] = api_key
        if base_url is not None:
            payload["baseUrl"] = base_url
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["maxTokens"] = max_tokens
        return await self._request("POST", "/v1/llms", json=payload)

    async def update_llm(
        self,
        llm_id: str,
        name: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Update an LLM configuration."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["maxTokens"] = max_tokens
        return await self._request("PUT", f"/v1/llms/{llm_id}", json=payload)

    async def delete_llm(self, llm_id: str) -> dict[str, Any]:
        """Delete an LLM by ID."""
        return await self._request("DELETE", f"/v1/llms/{llm_id}")

    # ─────────────────────────────────────────────────────────────────────────────
    # Share Links
    # ─────────────────────────────────────────────────────────────────────────────

    async def list_share_links(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> dict[str, Any]:
        """List all share links."""
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        return await self._request("GET", "/v1/share-links", params=params or None)

    async def get_share_link(self, link_id: str) -> dict[str, Any]:
        """Get a share link by ID."""
        return await self._request("GET", f"/v1/share-links/{link_id}")

    async def create_share_link(
        self,
        persona_id: str,
        name: str | None = None,
        expires_at: str | None = None,
        max_uses: int | None = None,
    ) -> dict[str, Any]:
        """Create a new share link for a persona."""
        payload = {"personaId": persona_id}
        if name is not None:
            payload["name"] = name
        if expires_at is not None:
            payload["expiresAt"] = expires_at
        if max_uses is not None:
            payload["maxUses"] = max_uses
        return await self._request("POST", "/v1/share-links", json=payload)

    async def update_share_link(
        self,
        link_id: str,
        name: str | None = None,
        expires_at: str | None = None,
        max_uses: int | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Update a share link."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if expires_at is not None:
            payload["expiresAt"] = expires_at
        if max_uses is not None:
            payload["maxUses"] = max_uses
        if is_active is not None:
            payload["isActive"] = is_active
        return await self._request("PUT", f"/v1/share-links/{link_id}", json=payload)

    async def delete_share_link(self, link_id: str) -> dict[str, Any]:
        """Delete a share link by ID."""
        return await self._request("DELETE", f"/v1/share-links/{link_id}")
