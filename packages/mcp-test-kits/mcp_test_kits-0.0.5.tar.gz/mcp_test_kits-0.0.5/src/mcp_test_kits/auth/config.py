"""OAuth configuration model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OAuthConfig(BaseModel):
    """OAuth configuration settings."""

    enabled: bool = False
    """Enable OAuth authentication for HTTP/SSE transports."""

    auto_approve: bool = False
    """Auto-approve consent for testing (skips consent screen)."""

    issuer: str | None = None
    """OAuth issuer URL. Defaults to server URL if not specified."""

    token_expiration: int = Field(default=3600, ge=60, le=86400)
    """Access token TTL in seconds (1 minute to 24 hours)."""

    authorization_code_ttl: int = Field(default=600, ge=60, le=1800)
    """Authorization code TTL in seconds (1 minute to 30 minutes)."""
