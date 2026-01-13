"""JWT token creation and validation."""

from __future__ import annotations

import time
import uuid
from typing import Any

import jwt

# Test secret key - DO NOT use in production
SECRET_KEY = "mcp-test-kits-secret-do-not-use-in-production"
ALGORITHM = "HS256"


def create_access_token(
    subject: str,
    scopes: str,
    resource: str,
    issuer: str,
    expiration: int = 3600,
) -> str:
    """Create a JWT access token.

    Args:
        subject: Subject identifier (user ID).
        scopes: Space-separated scopes.
        resource: Target resource URI.
        issuer: OAuth issuer URL.
        expiration: Token TTL in seconds.

    Returns:
        JWT access token string.
    """
    now = int(time.time())
    payload = {
        "iss": issuer,
        "aud": resource,
        "sub": subject,
        "scope": scopes,
        "resource": resource,
        "iat": now,
        "exp": now + expiration,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def validate_token(token: str, issuer: str) -> dict[str, Any]:
    """Validate a JWT access token.

    Per RFC 8707, the audience (aud) claim is the resource URL, which may
    differ from the issuer. We accept both with and without trailing slash
    for robustness.

    Args:
        token: JWT token string.
        issuer: Expected issuer URL.

    Returns:
        Decoded token payload.

    Raises:
        jwt.InvalidTokenError: If token is invalid, expired, or issuer doesn't match.
    """
    # Resource URL may have trailing slash, accept both formats
    valid_audiences = [
        issuer,
        issuer.rstrip("/") + "/",  # With trailing slash
        issuer.rstrip("/"),  # Without trailing slash
    ]

    payload: dict[str, Any] = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        audience=valid_audiences,
        issuer=issuer,
        options={"verify_signature": True, "verify_exp": True},
    )

    return payload
