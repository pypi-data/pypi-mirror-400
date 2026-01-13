"""Integration tests via SSE transport - smoke test only."""

from __future__ import annotations

import pytest


class TestSSETransport:
    """Smoke test for SSE transport."""

    @pytest.mark.asyncio
    async def test_sse_connection(self, sse_session):
        """Verify SSE transport connects and can call a tool."""
        async with sse_session as session:
            result = await session.call_tool("echo", {"message": "test"})
            assert result.content[0].text == "test"
