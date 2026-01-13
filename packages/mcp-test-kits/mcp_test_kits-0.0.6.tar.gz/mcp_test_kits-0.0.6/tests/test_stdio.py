"""Integration tests via stdio transport."""

from __future__ import annotations

import uuid

import pytest


class TestStdioTools:
    """Test tools via stdio transport."""

    @pytest.mark.asyncio
    async def test_echo(self, stdio_session):
        """Test echo tool."""
        async with stdio_session as session:
            result = await session.call_tool("echo", {"message": "hello"})
            assert result.content[0].text == "hello"

    @pytest.mark.asyncio
    async def test_add(self, stdio_session):
        """Test add tool."""
        async with stdio_session as session:
            result = await session.call_tool("add", {"a": 5, "b": 3})
            assert float(result.content[0].text) == 8.0

    @pytest.mark.asyncio
    async def test_multiply(self, stdio_session):
        """Test multiply tool."""
        async with stdio_session as session:
            result = await session.call_tool("multiply", {"x": 4, "y": 7})
            assert float(result.content[0].text) == 28.0

    @pytest.mark.asyncio
    async def test_reverse_string(self, stdio_session):
        """Test reverse_string tool."""
        async with stdio_session as session:
            result = await session.call_tool("reverse_string", {"text": "hello"})
            assert result.content[0].text == "olleh"

    @pytest.mark.asyncio
    async def test_generate_uuid(self, stdio_session):
        """Test generate_uuid tool."""
        async with stdio_session as session:
            result = await session.call_tool("generate_uuid", {})
            uuid.UUID(result.content[0].text)  # Should not raise

    @pytest.mark.asyncio
    async def test_get_timestamp(self, stdio_session):
        """Test get_timestamp tool."""
        async with stdio_session as session:
            result = await session.call_tool("get_timestamp", {"format": "iso"})
            assert "T" in result.content[0].text

    @pytest.mark.asyncio
    async def test_sample_error(self, stdio_session):
        """Test sample_error tool returns error."""
        async with stdio_session as session:
            result = await session.call_tool("sample_error", {})
            assert result.isError is True


class TestStdioResources:
    """Test resources via stdio transport."""

    @pytest.mark.asyncio
    async def test_list_resources(self, stdio_session):
        """Test listing resources."""
        async with stdio_session as session:
            result = await session.list_resources()
            uris = [str(r.uri) for r in result.resources]
            assert "test://static/greeting" in uris

    @pytest.mark.asyncio
    async def test_read_static_greeting(self, stdio_session):
        """Test reading static greeting."""
        async with stdio_session as session:
            result = await session.read_resource("test://static/greeting")
            assert "Hello" in result.contents[0].text

    @pytest.mark.asyncio
    async def test_read_dynamic_timestamp(self, stdio_session):
        """Test reading dynamic timestamp."""
        async with stdio_session as session:
            result = await session.read_resource("test://dynamic/timestamp")
            assert "T" in result.contents[0].text


class TestStdioPrompts:
    """Test prompts via stdio transport."""

    @pytest.mark.asyncio
    async def test_list_prompts(self, stdio_session):
        """Test listing prompts."""
        async with stdio_session as session:
            result = await session.list_prompts()
            names = [p.name for p in result.prompts]
            assert "simple_prompt" in names

    @pytest.mark.asyncio
    async def test_simple_prompt(self, stdio_session):
        """Test getting simple prompt."""
        async with stdio_session as session:
            result = await session.get_prompt("simple_prompt", {})
            assert len(result.messages) >= 1

    @pytest.mark.asyncio
    async def test_greeting_prompt(self, stdio_session):
        """Test greeting prompt with argument."""
        async with stdio_session as session:
            result = await session.get_prompt("greeting_prompt", {"name": "Alice"})
            assert "Alice" in result.messages[0].content.text
