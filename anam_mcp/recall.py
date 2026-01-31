"""Async HTTP client for Recall AI API - adds avatars to video meetings."""

from __future__ import annotations

import os
from typing import Any

import httpx


class RecallAPIError(Exception):
    """Exception raised when the Recall API returns an error."""

    def __init__(self, status_code: int, message: str, details: dict | None = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{status_code}] {message}")


class RecallClient:
    """Async client for interacting with the Recall AI API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key or os.getenv("RECALL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "RECALL_API_KEY is required. Set it as an environment variable or pass it to the client."
            )
        self.base_url = base_url or os.getenv(
            "RECALL_API_URL", "https://us-west-2.recall.ai/api/v1"
        )

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Recall API."""
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
                try:
                    error_data = response.json()
                    message = error_data.get("detail", error_data.get("error", str(error_data)))
                    details = error_data
                except Exception:
                    message = response.text or f"HTTP {response.status_code}"
                    details = {}

                if response.status_code == 401:
                    message = "Invalid API key. Check your RECALL_API_KEY."
                elif response.status_code == 403:
                    message = f"Access denied: {message}"
                elif response.status_code == 404:
                    message = f"Not found: {path}"
                elif response.status_code == 429:
                    message = "Rate limit exceeded. Please wait and try again."

                raise RecallAPIError(response.status_code, message, details)

            if response.status_code == 204 or not response.content:
                return {}

            result = response.json()
            if result is None:
                return {}
            return result

    # ─────────────────────────────────────────────────────────────────────────────
    # Bot Management
    # ─────────────────────────────────────────────────────────────────────────────

    async def create_bot(
        self,
        meeting_url: str,
        output_media_url: str,
        bot_name: str = "Anam Avatar",
        join_at: str | None = None,
    ) -> dict[str, Any]:
        """Create a Recall bot that joins a video meeting.

        The bot renders output_media_url as its camera feed and routes
        meeting audio to the webpage via getUserMedia.

        Args:
            meeting_url: Video conference URL (Zoom, Meet, Teams)
            output_media_url: URL to render as bot's camera (e.g., meet.anam.ai page)
            bot_name: Name shown in the meeting
            join_at: ISO timestamp to schedule join (optional)
        """
        payload: dict[str, Any] = {
            "meeting_url": meeting_url,
            "bot_name": bot_name,
            "output_media": {
                "camera": {
                    "kind": "webpage",
                    "config": {
                        "url": output_media_url,
                    },
                },
            },
            # Use web_4_core variant for better frame rate (more CPU cores)
            "variant": {
                "zoom": "web_4_core",
                "google_meet": "web_4_core",
                "microsoft_teams": "web_4_core",
            },
        }
        if join_at:
            payload["join_at"] = join_at

        return await self._request("POST", "/bot/", json=payload)

    async def get_bot(self, bot_id: str) -> dict[str, Any]:
        """Get details of a Recall bot."""
        return await self._request("GET", f"/bot/{bot_id}/")

    async def list_bots(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """List all Recall bots."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return await self._request("GET", "/bot/", params=params or None)

    async def leave_meeting(self, bot_id: str) -> dict[str, Any]:
        """Make a bot leave the meeting."""
        return await self._request("POST", f"/bot/{bot_id}/leave_call/")

    async def delete_bot(self, bot_id: str) -> dict[str, Any]:
        """Delete a bot entirely."""
        return await self._request("DELETE", f"/bot/{bot_id}/")
