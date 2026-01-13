"""Configuration models for MCP Test Kits."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .auth import OAuthConfig


class ServerConfig(BaseModel):
    """Server information configuration."""

    name: str = "mcp-test-kits"
    version: str = "1.0.0"


class NetworkConfig(BaseModel):
    """Network settings for HTTP/SSE transports."""

    host: str = "localhost"
    port: int = Field(default=3000, ge=1, le=65535)


class TransportConfig(BaseModel):
    """Transport configuration."""

    type: Literal["stdio", "http", "sse"] = "stdio"
    network: NetworkConfig = Field(default_factory=NetworkConfig)


class CapabilitiesConfig(BaseModel):
    """Capabilities to enable."""

    tools: bool = True
    resources: bool = True
    prompts: bool = True


class Config(BaseModel):
    """Main configuration model."""

    server: ServerConfig = Field(default_factory=ServerConfig)
    transport: TransportConfig = Field(default_factory=TransportConfig)
    capabilities: CapabilitiesConfig = Field(default_factory=CapabilitiesConfig)
    oauth: OAuthConfig = Field(default_factory=OAuthConfig)
