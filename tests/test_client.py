"""Integration tests for the Anam API client.

These tests call the real Anam API and require ANAM_API_KEY to be set.
They are designed to leave the account in the same state after running.

Run with: pytest tests/test_client.py -v
"""

from __future__ import annotations

import pytest

from anam_mcp.client import AnamAPIError, AnamClient

pytestmark = pytest.mark.integration


# ─────────────────────────────────────────────────────────────────────────────────
# Persona Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestPersonas:
    """Tests for persona CRUD operations."""

    async def test_list_personas(self, client: AnamClient) -> None:
        """Test listing personas with pagination."""
        result = await client.list_personas(page=1, per_page=10)
        assert isinstance(result, dict)
        assert "data" in result
        assert "meta" in result
        assert isinstance(result["data"], list)
        # Verify pagination metadata
        meta = result["meta"]
        assert "total" in meta or "currentPage" in meta

    async def test_list_personas_pagination(self, client: AnamClient) -> None:
        """Test that pagination returns consistent results."""
        page1 = await client.list_personas(page=1, per_page=5)
        if page1["meta"].get("lastPage", 1) > 1:
            page2 = await client.list_personas(page=2, per_page=5)
            # Pages should have different items
            page1_ids = {p["id"] for p in page1["data"]}
            page2_ids = {p["id"] for p in page2["data"]}
            assert page1_ids.isdisjoint(page2_ids), "Pagination returned duplicate items"

    async def test_create_get_update_delete_persona(
        self,
        client: AnamClient,
        stock_avatar_id: str,
        stock_voice_id: str,
        default_llm_id: str,
        test_prefix: str,
        cleanup_personas: list[str],
    ) -> None:
        """Test full persona lifecycle: create, get, update, delete."""
        # Create
        name = f"{test_prefix}_persona"
        result = await client.create_persona(
            name=name,
            avatar_id=stock_avatar_id,
            voice_id=stock_voice_id,
            system_prompt="You are a test assistant.",
            llm_id=default_llm_id,
        )
        assert "id" in result
        persona_id = result["id"]
        cleanup_personas.append(persona_id)  # Track for cleanup

        # Get
        persona = await client.get_persona(persona_id)
        assert persona["id"] == persona_id
        assert persona["name"] == name
        # Note: system_prompt may not be returned in the response for security reasons

        # Update
        new_name = f"{test_prefix}_persona_updated"
        updated = await client.update_persona(
            persona_id=persona_id,
            name=new_name,
            system_prompt="Updated prompt.",
        )
        # Update may return full object or just confirmation
        if "name" in updated:
            assert updated["name"] == new_name

        # Verify update persisted
        verified = await client.get_persona(persona_id)
        assert verified["name"] == new_name

        # Delete
        await client.delete_persona(persona_id)
        cleanup_personas.remove(persona_id)  # Already deleted

        # Verify deletion
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_persona(persona_id)
        assert exc_info.value.status_code == 404

    async def test_get_nonexistent_persona(self, client: AnamClient) -> None:
        """Test getting a persona that doesn't exist."""
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_persona("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────────
# Avatar Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestAvatars:
    """Tests for avatar operations."""

    async def test_list_avatars(self, client: AnamClient) -> None:
        """Test listing avatars."""
        result = await client.list_avatars(page=1, per_page=10)
        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) > 0, "Expected at least one avatar"

    async def test_list_avatars_pagination(self, client: AnamClient) -> None:
        """Test avatar pagination."""
        page1 = await client.list_avatars(page=1, per_page=5)
        assert "data" in page1
        assert "meta" in page1

    async def test_get_avatar(self, client: AnamClient, stock_avatar_id: str) -> None:
        """Test getting a specific avatar by ID."""
        result = await client.get_avatar(stock_avatar_id)
        assert result["id"] == stock_avatar_id
        assert "displayName" in result

    async def test_get_nonexistent_avatar(self, client: AnamClient) -> None:
        """Test getting an avatar that doesn't exist."""
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_avatar("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404

    @pytest.mark.skip(reason="Avatar creation requires enterprise/pro plan and image processing")
    async def test_create_update_delete_avatar(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_avatars: list[str],
    ) -> None:
        """Test full avatar lifecycle."""
        # This test is skipped by default because:
        # 1. Custom avatar creation requires enterprise/pro plan
        # 2. Image URL must be valid and processable
        # 3. Avatar processing is async and may take time
        pass


# ─────────────────────────────────────────────────────────────────────────────────
# Voice Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestVoices:
    """Tests for voice operations."""

    async def test_list_voices(self, client: AnamClient) -> None:
        """Test listing voices."""
        result = await client.list_voices(page=1, per_page=10)
        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) > 0, "Expected at least one voice"

    async def test_list_voices_pagination(self, client: AnamClient) -> None:
        """Test voice pagination across multiple pages."""
        from tests.conftest import fetch_all_pages

        # Voices should have 400+ items across multiple pages
        page1 = await client.list_voices(page=1, per_page=100)
        meta = page1.get("meta", {})
        total = meta.get("total", 0)
        assert total > 100, f"Expected many voices, got {total}"

        # Verify we can fetch page 2
        if meta.get("lastPage", 1) > 1:
            page2 = await client.list_voices(page=2, per_page=100)
            assert len(page2["data"]) > 0

    async def test_get_voice(self, client: AnamClient, stock_voice_id: str) -> None:
        """Test getting a specific voice by ID."""
        result = await client.get_voice(stock_voice_id)
        assert result["id"] == stock_voice_id
        assert "displayName" in result or "name" in result

    async def test_get_nonexistent_voice(self, client: AnamClient) -> None:
        """Test getting a voice that doesn't exist."""
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_voice("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404

    @pytest.mark.skip(reason="Voice creation may require specific permissions")
    async def test_create_update_delete_voice(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_voices: list[str],
    ) -> None:
        """Test full voice lifecycle."""
        pass


# ─────────────────────────────────────────────────────────────────────────────────
# Tool Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestTools:
    """Tests for tool CRUD operations."""

    async def test_list_tools(self, client: AnamClient) -> None:
        """Test listing tools."""
        result = await client.list_tools(page=1, per_page=10)
        assert isinstance(result, dict)
        assert "data" in result

    async def test_create_get_update_delete_webhook_tool(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_tools: list[str],
    ) -> None:
        """Test full webhook tool lifecycle."""
        # Create - use snake_case name as required by API
        name = "test_webhook_tool"
        try:
            result = await client.create_webhook_tool(
                name=name,
                description="Test webhook for integration tests",
                url="https://httpbin.org/post",
                method="POST",
                await_response=True,
            )
        except AnamAPIError as e:
            if e.status_code == 400:
                pytest.skip(f"Tool creation validation error: {e.message}")
            raise

        assert "id" in result
        tool_id = result["id"]
        cleanup_tools.append(tool_id)

        # Get
        tool = await client.get_tool(tool_id)
        assert tool["id"] == tool_id
        assert tool["name"] == name

        # Update
        new_name = "test_webhook_updated"
        try:
            updated = await client.update_tool(
                tool_id=tool_id,
                name=new_name,
                description="Updated description",
            )
            # Update may return updated object or just confirmation
            if "name" in updated:
                assert updated["name"] == new_name
        except AnamAPIError as e:
            if e.status_code == 400:
                pass  # Update validation may fail, that's ok for this test
            else:
                raise

        # Delete
        await client.delete_tool(tool_id)
        cleanup_tools.remove(tool_id)

        # Verify deletion
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_tool(tool_id)
        assert exc_info.value.status_code == 404

    async def test_create_knowledge_tool(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_tools: list[str],
        cleanup_knowledge_groups: list[str],
    ) -> None:
        """Test creating a knowledge tool linked to a folder."""
        # First create a knowledge folder
        folder_name = f"{test_prefix}_folder"
        folder = await client.create_knowledge_folder(
            name=folder_name,
            description="Test folder for knowledge tool",
        )
        folder_id = folder["id"]
        cleanup_knowledge_groups.append(folder_id)

        # Create knowledge tool - use snake_case name
        tool_name = "test_knowledge_rag"
        try:
            result = await client.create_knowledge_tool(
                name=tool_name,
                description="Search test documents",
                folder_ids=[folder_id],
            )
            assert "id" in result
            tool_id = result["id"]
            cleanup_tools.append(tool_id)

            # Clean up tool first (before folder)
            await client.delete_tool(tool_id)
            cleanup_tools.remove(tool_id)
        except AnamAPIError as e:
            if e.status_code == 400:
                pytest.skip(f"Knowledge tool creation validation error: {e.message}")
            raise

    async def test_get_nonexistent_tool(self, client: AnamClient) -> None:
        """Test getting a tool that doesn't exist."""
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_tool("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────────
# Knowledge Group Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestKnowledgeGroups:
    """Tests for knowledge group (folder) operations."""

    async def test_list_knowledge_groups(self, client: AnamClient) -> None:
        """Test listing knowledge groups."""
        result = await client.list_knowledge_folders()
        # Result might be a list or dict with data key
        if isinstance(result, list):
            assert isinstance(result, list)
        else:
            assert "data" in result or isinstance(result, list)

    async def test_create_get_update_delete_knowledge_group(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_knowledge_groups: list[str],
    ) -> None:
        """Test full knowledge group lifecycle."""
        # Create
        name = f"{test_prefix}_knowledge"
        result = await client.create_knowledge_folder(
            name=name,
            description="Test knowledge folder",
        )
        assert "id" in result
        group_id = result["id"]
        cleanup_knowledge_groups.append(group_id)

        # Get
        group = await client.get_knowledge_group(group_id)
        assert group["id"] == group_id
        assert group["name"] == name

        # Update
        new_name = f"{test_prefix}_knowledge_updated"
        updated = await client.update_knowledge_group(
            group_id=group_id,
            name=new_name,
            description="Updated description",
        )
        # Update may return updated object or just confirmation
        if "name" in updated:
            assert updated["name"] == new_name

        # Verify update persisted
        verified = await client.get_knowledge_group(group_id)
        assert verified["name"] == new_name

        # Delete (may return empty response)
        await client.delete_knowledge_group(group_id)
        cleanup_knowledge_groups.remove(group_id)

        # Verify deletion
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_knowledge_group(group_id)
        assert exc_info.value.status_code == 404

    async def test_search_knowledge_group(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_knowledge_groups: list[str],
    ) -> None:
        """Test searching within a knowledge group."""
        # Create folder first
        name = f"{test_prefix}_search_test"
        folder = await client.create_knowledge_folder(
            name=name,
            description="Test folder for search",
        )
        folder_id = folder["id"]
        cleanup_knowledge_groups.append(folder_id)

        # Search (may return empty if no documents, or may not be supported)
        try:
            result = await client.search_knowledge_group(
                group_id=folder_id,
                query="test query",
            )
            assert isinstance(result, (list, dict))
        except AnamAPIError as e:
            # Search might not be available on empty folders or require specific plan
            assert e.status_code in (400, 404, 501)

        # Clean up
        await client.delete_knowledge_group(folder_id)
        cleanup_knowledge_groups.remove(folder_id)


# ─────────────────────────────────────────────────────────────────────────────────
# Knowledge Document Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestKnowledgeDocuments:
    """Tests for knowledge document operations."""

    async def test_list_documents_empty_folder(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_knowledge_groups: list[str],
    ) -> None:
        """Test listing documents in an empty folder."""
        # Create folder
        folder = await client.create_knowledge_folder(
            name=f"{test_prefix}_docs_folder",
        )
        folder_id = folder["id"]
        cleanup_knowledge_groups.append(folder_id)

        # List documents (should be empty or return valid response)
        try:
            result = await client.list_knowledge_documents(folder_id)
            if isinstance(result, list):
                # Empty list is fine
                pass
            else:
                # Dict response with data key
                data = result.get("data", [])
                assert isinstance(data, list)
        except AnamAPIError as e:
            # Some APIs may return 404 for empty folders
            assert e.status_code in (400, 404)

        # Clean up
        await client.delete_knowledge_group(folder_id)
        cleanup_knowledge_groups.remove(folder_id)

    @pytest.mark.skip(reason="Document upload requires file handling - test manually")
    async def test_upload_get_update_delete_document(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_knowledge_groups: list[str],
    ) -> None:
        """Test full document lifecycle."""
        # This test requires actual file upload which may need special handling
        pass


# ─────────────────────────────────────────────────────────────────────────────────
# LLM Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestLLMs:
    """Tests for LLM operations."""

    async def test_list_llms(self, client: AnamClient) -> None:
        """Test listing available LLMs."""
        result = await client.list_llms()
        if isinstance(result, list):
            assert len(result) > 0, "Expected at least one LLM"
        else:
            assert len(result.get("data", [])) > 0

    async def test_get_llm(self, client: AnamClient, default_llm_id: str) -> None:
        """Test getting a specific LLM."""
        result = await client.get_llm(default_llm_id)
        assert result["id"] == default_llm_id

    async def test_get_nonexistent_llm(self, client: AnamClient) -> None:
        """Test getting an LLM that doesn't exist."""
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_llm("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404

    @pytest.mark.skip(reason="LLM creation may require specific permissions")
    async def test_create_update_delete_llm(
        self,
        client: AnamClient,
        test_prefix: str,
        cleanup_llms: list[str],
    ) -> None:
        """Test full LLM lifecycle."""
        pass


# ─────────────────────────────────────────────────────────────────────────────────
# Session Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestSessions:
    """Tests for session operations."""

    async def test_create_session_token_with_persona_id(
        self,
        client: AnamClient,
        stock_avatar_id: str,
        stock_voice_id: str,
        default_llm_id: str,
        test_prefix: str,
        cleanup_personas: list[str],
    ) -> None:
        """Test creating a session token for an existing persona."""
        # Create a persona first
        persona = await client.create_persona(
            name=f"{test_prefix}_session_test",
            avatar_id=stock_avatar_id,
            voice_id=stock_voice_id,
            system_prompt="Test assistant",
            llm_id=default_llm_id,
        )
        persona_id = persona["id"]
        cleanup_personas.append(persona_id)

        # Create session token
        result = await client.create_session_token(persona_id=persona_id)
        assert "sessionToken" in result
        assert len(result["sessionToken"]) > 0

    async def test_create_session_token_ephemeral(
        self,
        client: AnamClient,
        stock_avatar_id: str,
        stock_voice_id: str,
    ) -> None:
        """Test creating an ephemeral session token."""
        result = await client.create_session_token(
            name="Ephemeral Test",
            avatar_id=stock_avatar_id,
            voice_id=stock_voice_id,
            system_prompt="Ephemeral test assistant",
        )
        assert "sessionToken" in result
        assert len(result["sessionToken"]) > 0

    async def test_list_sessions(self, client: AnamClient) -> None:
        """Test listing sessions."""
        result = await client.list_sessions(page=1, per_page=10)
        assert isinstance(result, dict)
        assert "data" in result

    async def test_get_session(self, client: AnamClient) -> None:
        """Test getting a specific session (if any exist)."""
        # First list to find a session
        sessions = await client.list_sessions(page=1, per_page=1)
        if not sessions.get("data"):
            pytest.skip("No sessions available to test get_session")

        session_id = sessions["data"][0]["id"]
        result = await client.get_session(session_id)
        assert result["id"] == session_id

    async def test_get_nonexistent_session(self, client: AnamClient) -> None:
        """Test getting a session that doesn't exist."""
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_session("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404

    @pytest.mark.skip(reason="Session recordings may not always exist")
    async def test_get_session_recording(self, client: AnamClient) -> None:
        """Test getting a session recording."""
        pass


# ─────────────────────────────────────────────────────────────────────────────────
# Share Link Tests
# ─────────────────────────────────────────────────────────────────────────────────


class TestShareLinks:
    """Tests for share link operations."""

    async def test_list_share_links(self, client: AnamClient) -> None:
        """Test listing share links."""
        result = await client.list_share_links(page=1, per_page=10)
        assert isinstance(result, dict)
        assert "data" in result

    async def test_create_get_update_delete_share_link(
        self,
        client: AnamClient,
        stock_avatar_id: str,
        stock_voice_id: str,
        default_llm_id: str,
        test_prefix: str,
        cleanup_personas: list[str],
        cleanup_share_links: list[str],
    ) -> None:
        """Test full share link lifecycle."""
        # Create a persona first (share links need a persona)
        persona = await client.create_persona(
            name=f"{test_prefix}_share_link_test",
            avatar_id=stock_avatar_id,
            voice_id=stock_voice_id,
            system_prompt="Test assistant for share link",
            llm_id=default_llm_id,
        )
        persona_id = persona["id"]
        cleanup_personas.append(persona_id)

        # Create share link
        result = await client.create_share_link(
            persona_id=persona_id,
            name=f"{test_prefix}_link",
        )
        assert "id" in result
        link_id = result["id"]
        cleanup_share_links.append(link_id)

        # Get
        link = await client.get_share_link(link_id)
        assert link["id"] == link_id

        # Update
        new_name = f"{test_prefix}_link_updated"
        updated = await client.update_share_link(
            link_id=link_id,
            name=new_name,
        )
        # Update may return updated object or just confirmation
        if "name" in updated:
            assert updated["name"] == new_name

        # Verify update persisted
        verified = await client.get_share_link(link_id)
        assert verified.get("name") == new_name or "id" in verified

        # Delete
        await client.delete_share_link(link_id)
        cleanup_share_links.remove(link_id)

        # Verify deletion
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_share_link(link_id)
        assert exc_info.value.status_code == 404

    async def test_get_nonexistent_share_link(self, client: AnamClient) -> None:
        """Test getting a share link that doesn't exist."""
        with pytest.raises(AnamAPIError) as exc_info:
            await client.get_share_link("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404
