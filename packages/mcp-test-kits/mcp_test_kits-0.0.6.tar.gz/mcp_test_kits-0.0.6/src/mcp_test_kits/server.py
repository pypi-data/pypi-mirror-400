"""FastMCP server setup for MCP Test Kits."""

from __future__ import annotations

from fastmcp import FastMCP

from .capabilities.prompts import register_prompts
from .capabilities.resources import register_resources
from .capabilities.tools import register_tools
from .config import Config


def create_server(config: Config) -> FastMCP:
    """Create and configure the FastMCP server.

    Args:
        config: Server configuration.

    Returns:
        Configured FastMCP server instance.
    """
    mcp = FastMCP(
        name=config.server.name,
    )

    # Register capabilities based on config
    if config.capabilities.tools:
        register_tools(mcp)

    if config.capabilities.resources:
        register_resources(mcp)

    if config.capabilities.prompts:
        register_prompts(mcp)

    return mcp
