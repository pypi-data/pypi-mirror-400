"""Integration tests via HTTP transport."""

from __future__ import annotations

import pytest


class TestHTTPTransport:
    """Test HTTP transport."""

    @pytest.mark.asyncio
    async def test_http_connection(self, http_session):
        """Verify HTTP transport connects and can call a tool."""
        async with http_session as session:
            result = await session.call_tool("echo", {"message": "test"})
            assert result.content[0].text == "test"
