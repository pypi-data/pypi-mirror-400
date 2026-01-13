"""Entry point for MCP Test Kits server."""

from __future__ import annotations

import argparse
import asyncio
import sys

from .config import Config
from .server import create_server
from .transports import run_http_server, run_sse_server, run_stdio_server


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="mcp-test-kits",
        description="MCP Test Kits - A comprehensive MCP testing server",
        epilog="""
Examples:
  # Run with stdio (default)
  mcp-test-kits

  # Run with HTTP transport
  mcp-test-kits --transport http --port 3000

  # Run with only tools (no resources or prompts)
  mcp-test-kits --no-resources --no-prompts
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--transport",
        "-t",
        type=str,
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=3000,
        help="Port to listen on (default: 3000)",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        type=str,
        choices=["debug", "info", "warn", "error"],
        default="info",
        help="Log level (default: info)",
    )
    # Capability flags (use --no-X to disable)
    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Disable tools capability",
    )
    parser.add_argument(
        "--no-resources",
        action="store_true",
        help="Disable resources capability",
    )
    parser.add_argument(
        "--no-prompts",
        action="store_true",
        help="Disable prompts capability",
    )
    # OAuth flags
    parser.add_argument(
        "--enable-oauth",
        action="store_true",
        help="Enable OAuth authentication (HTTP/SSE only)",
    )
    parser.add_argument(
        "--oauth-auto-approve",
        action="store_true",
        help="Auto-approve OAuth consent for testing (requires --enable-oauth)",
    )
    parser.add_argument(
        "--oauth-issuer",
        type=str,
        help="OAuth issuer URL (default: server URL)",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s 1.0.0",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Build config from CLI args
    config = Config()
    config.transport.type = args.transport
    config.transport.network.host = args.host
    config.transport.network.port = args.port
    config.capabilities.tools = not args.no_tools
    config.capabilities.resources = not args.no_resources
    config.capabilities.prompts = not args.no_prompts
    config.oauth.enabled = args.enable_oauth
    config.oauth.auto_approve = args.oauth_auto_approve
    if args.oauth_issuer:
        config.oauth.issuer = args.oauth_issuer

    # Create server
    mcp = create_server(config)

    # Run with appropriate transport
    async def run() -> None:
        if args.transport == "stdio":
            await run_stdio_server(mcp, config)
        elif args.transport == "http":
            await run_http_server(mcp, config, log_level=args.log_level)
        elif args.transport == "sse":
            await run_sse_server(mcp, config, log_level=args.log_level)
        else:
            print(f"Unknown transport type: {args.transport}", file=sys.stderr)
            sys.exit(1)

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
