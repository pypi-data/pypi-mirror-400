"""Shared fixtures for integration tests."""

from __future__ import annotations

import socket
import subprocess
import time
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    """Wait for a TCP port to become available.

    Args:
        host: Hostname to check
        port: Port number to check
        timeout: Maximum time to wait in seconds

    Returns:
        True if port became available, False if timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                if sock.connect_ex((host, port)) == 0:
                    return True
        except Exception:
            pass
        time.sleep(0.1)
    return False


@pytest.fixture
def stdio_session():
    """Return async context manager for an MCP client session connected via stdio."""

    @asynccontextmanager
    async def _session() -> AsyncGenerator[ClientSession]:
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "mcp-test-kits"],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    return _session()


@pytest.fixture
def http_server():
    """Start HTTP server and return base URL."""
    host = "localhost"
    port = 3001

    # Don't pipe - let output go to console for debugging in CI
    proc = subprocess.Popen(
        ["uv", "run", "mcp-test-kits", "--transport", "http", "--port", str(port)],
    )

    try:
        # Wait for port to be ready (up to 10 seconds)
        if not wait_for_port(host, port, timeout=10.0):
            # Check if process crashed
            if proc.poll() is not None:
                raise RuntimeError(
                    f"HTTP server process exited with code {proc.returncode}"
                )
            raise RuntimeError(
                f"HTTP server failed to start on port {port} within 10 seconds"
            )

        yield f"http://{host}:{port}"
    finally:
        # Clean up
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


@pytest.fixture
def sse_server():
    """Start SSE server and return base URL."""
    host = "localhost"
    port = 3002

    # Don't pipe - let output go to console for debugging in CI
    proc = subprocess.Popen(
        ["uv", "run", "mcp-test-kits", "--transport", "sse", "--port", str(port)],
    )

    try:
        # Wait for port to be ready (up to 10 seconds)
        if not wait_for_port(host, port, timeout=10.0):
            # Check if process crashed
            if proc.poll() is not None:
                raise RuntimeError(
                    f"SSE server process exited with code {proc.returncode}"
                )
            raise RuntimeError(
                f"SSE server failed to start on port {port} within 10 seconds"
            )

        yield f"http://{host}:{port}"
    finally:
        # Clean up
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


@pytest.fixture
def http_session(http_server):
    """Return async context manager for an MCP client session connected via HTTP."""

    @asynccontextmanager
    async def _session() -> AsyncGenerator[ClientSession]:
        async with streamable_http_client(f"{http_server}/mcp") as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    return _session()


@pytest.fixture
def sse_session(sse_server):
    """Return async context manager for an MCP client session connected via SSE."""

    @asynccontextmanager
    async def _session() -> AsyncGenerator[ClientSession]:
        async with sse_client(f"{sse_server}/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    return _session()
