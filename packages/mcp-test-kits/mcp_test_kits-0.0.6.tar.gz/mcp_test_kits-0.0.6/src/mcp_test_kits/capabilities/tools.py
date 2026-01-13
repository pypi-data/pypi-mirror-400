"""Tool implementations for MCP Test Kits."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """Register all tools with the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.tool(description="Returns the input message unchanged")
    def echo(message: str) -> str:
        """Echo the input message."""
        return message

    @mcp.tool(description="Adds two numbers together")
    def add(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    @mcp.tool(description="Multiplies two numbers")
    def multiply(x: float, y: float) -> float:
        """Multiply two numbers."""
        return x * y

    @mcp.tool(description="Reverses a string")
    def reverse_string(text: str) -> str:
        """Reverse the input string."""
        return text[::-1]

    @mcp.tool(description="Generates a random UUID")
    def generate_uuid() -> str:
        """Generate a random UUID."""
        return str(uuid.uuid4())

    @mcp.tool(description="Returns the current timestamp")
    def get_timestamp(format: str = "iso") -> str | int:
        """Get the current timestamp.

        Args:
            format: 'unix' for Unix timestamp, 'iso' for ISO format.
        """
        now = datetime.now(UTC)
        if format == "unix":
            return int(now.timestamp())
        return now.isoformat()

    @mcp.tool(description="Always throws an error (for testing error handling)")
    def sample_error(error_message: str = "This is a test error") -> str:
        """Raise a sample error for testing."""
        raise ValueError(error_message)

    @mcp.tool(description="Simulates a long-running operation")
    async def long_running_task(duration: float) -> str:
        """Simulate a long-running task.

        Args:
            duration: Duration in seconds (max 10).
        """
        # Clamp duration to max 10 seconds
        actual_duration = min(max(duration, 0), 10)
        await asyncio.sleep(actual_duration)
        return f"Task completed after {actual_duration} seconds"
