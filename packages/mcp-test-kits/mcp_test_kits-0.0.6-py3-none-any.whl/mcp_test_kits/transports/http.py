"""HTTP transport for MCP Test Kits (Streamable HTTP)."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from ..config import Config


async def run_http_server(
    mcp: FastMCP, config: Config, log_level: str = "info"
) -> None:
    """Run the MCP server over HTTP transport (Streamable HTTP).

    Args:
        mcp: FastMCP server instance.
        config: Server configuration.
        log_level: Log level (debug, info, warn, error).
    """
    host = config.transport.network.host
    port = config.transport.network.port

    # Log to stderr for stdio compatibility
    print(f"Starting MCP HTTP server at http://{host}:{port}/mcp", file=sys.stderr)

    if config.oauth.enabled:
        print(
            f"OAuth enabled - authorize at http://{host}:{port}/oauth/authorize",
            file=sys.stderr,
        )
        # Import OAuth components
        from starlette.applications import Starlette
        from starlette.middleware import Middleware

        from ..auth.middleware import OAuthMiddleware
        from ..auth.oauth_endpoints import register_oauth_routes
        from ..auth.well_known import register_well_known_routes

        # Get MCP app from FastMCP with /mcp path - must be created first for lifespan
        mcp_app = mcp.http_app(path="/mcp")

        # Create Starlette app with OAuth middleware and MCP lifespan
        app = Starlette(
            middleware=[Middleware(OAuthMiddleware, config=config)],
            lifespan=mcp_app.lifespan,
        )

        # Register OAuth routes
        register_well_known_routes(app, config)
        register_oauth_routes(app, config)

        # Mount MCP app at root (path is already configured)
        app.mount("/", mcp_app)

        # Run with Uvicorn
        import uvicorn

        await uvicorn.Server(
            uvicorn.Config(app, host=host, port=port, log_level=log_level)
        ).serve()
    else:
        # Use FastMCP's built-in HTTP transport support
        await mcp.run_async(transport="http", host=host, port=port, show_banner=False)
