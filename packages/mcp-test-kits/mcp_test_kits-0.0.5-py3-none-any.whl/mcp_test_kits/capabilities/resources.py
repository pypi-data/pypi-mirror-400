"""Resource implementations for MCP Test Kits."""

from __future__ import annotations

import json
import random
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


# Large text content for testing
LARGE_TEXT_CONTENT = (
    """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.

"""
    * 100
)  # Repeat to make it large


def register_resources(mcp: FastMCP) -> None:
    """Register all resources with the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.resource("test://static/greeting")
    def static_greeting() -> str:
        """Return a static greeting message."""
        return "Hello from mcp-test-kits!"

    @mcp.resource("test://static/numbers")
    def static_numbers() -> str:
        """Return a list of numbers as JSON."""
        return json.dumps({"numbers": [1, 2, 3, 4, 5]})

    @mcp.resource("test://dynamic/timestamp")
    def dynamic_timestamp() -> str:
        """Return the current timestamp."""
        now = datetime.now(UTC)
        return json.dumps(
            {
                "timestamp": now.isoformat(),
                "unix": int(now.timestamp()),
            }
        )

    @mcp.resource("test://dynamic/random")
    def dynamic_random() -> str:
        """Return a random number between 0-100."""
        return json.dumps({"random": random.randint(0, 100)})

    @mcp.resource("test://large-text")
    def large_text() -> str:
        """Return a large text resource for testing."""
        return LARGE_TEXT_CONTENT
