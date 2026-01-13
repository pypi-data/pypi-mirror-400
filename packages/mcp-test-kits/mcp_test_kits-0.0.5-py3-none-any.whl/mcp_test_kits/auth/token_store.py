"""In-memory token and authorization code storage."""

from __future__ import annotations

import time
from dataclasses import dataclass

# In-memory storage
_authorization_codes: dict[str, AuthCodeData] = {}
_access_tokens: dict[str, TokenData] = {}
_revoked_tokens: set[str] = set()
_registered_clients: dict[str, ClientData] = {}


@dataclass
class AuthCodeData:
    """Authorization code data."""

    client_id: str
    redirect_uri: str
    scope: str
    code_challenge: str
    code_challenge_method: str
    resource: str
    state: str | None
    created_at: float


@dataclass
class TokenData:
    """Access token metadata."""

    jti: str
    subject: str
    scopes: str
    resource: str
    created_at: float
    expires_at: float


@dataclass
class ClientData:
    """Registered client metadata."""

    client_id: str
    client_name: str
    redirect_uris: list[str]
    grant_types: list[str]
    response_types: list[str]
    token_endpoint_auth_method: str
    client_id_issued_at: int


def store_authorization_code(
    code: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    code_challenge: str,
    code_challenge_method: str,
    resource: str,
    state: str | None,
    ttl: int,
) -> None:
    """Store an authorization code.

    Args:
        code: Authorization code.
        client_id: Client identifier.
        redirect_uri: Redirect URI.
        scope: Requested scopes.
        code_challenge: PKCE code challenge.
        code_challenge_method: PKCE method (S256).
        resource: Target resource URI.
        state: CSRF state parameter.
        ttl: Time to live in seconds.
    """
    _authorization_codes[code] = AuthCodeData(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        resource=resource,
        state=state,
        created_at=time.time(),
    )
    # Clean up expired codes
    _cleanup_expired_codes()


def get_authorization_code(code: str) -> AuthCodeData | None:
    """Retrieve authorization code data.

    Args:
        code: Authorization code.

    Returns:
        Authorization code data or None if not found.
    """
    return _authorization_codes.get(code)


def delete_authorization_code(code: str) -> None:
    """Delete an authorization code (one-time use).

    Args:
        code: Authorization code.
    """
    _authorization_codes.pop(code, None)


def store_access_token(
    jti: str,
    subject: str,
    scopes: str,
    resource: str,
    expires_in: int,
) -> None:
    """Store access token metadata.

    Args:
        jti: JWT ID (unique token identifier).
        subject: Subject (user ID).
        scopes: Space-separated scopes.
        resource: Target resource URI.
        expires_in: Expiration time in seconds.
    """
    now = time.time()
    _access_tokens[jti] = TokenData(
        jti=jti,
        subject=subject,
        scopes=scopes,
        resource=resource,
        created_at=now,
        expires_at=now + expires_in,
    )
    # Clean up expired tokens
    _cleanup_expired_tokens()


def revoke_token(token_jti: str) -> None:
    """Revoke an access token.

    Args:
        token_jti: JWT ID to revoke.
    """
    _revoked_tokens.add(token_jti)


def is_token_revoked(token_jti: str) -> bool:
    """Check if a token is revoked.

    Args:
        token_jti: JWT ID to check.

    Returns:
        True if revoked, False otherwise.
    """
    return token_jti in _revoked_tokens


def _cleanup_expired_codes() -> None:
    """Remove expired authorization codes."""
    now = time.time()
    expired = [
        code
        for code, data in _authorization_codes.items()
        if now - data.created_at > 600  # 10 minutes default
    ]
    for code in expired:
        del _authorization_codes[code]


def _cleanup_expired_tokens() -> None:
    """Remove expired access tokens."""
    now = time.time()
    expired = [jti for jti, data in _access_tokens.items() if now > data.expires_at]
    for jti in expired:
        del _access_tokens[jti]
        _revoked_tokens.discard(jti)


def register_client(
    client_id: str,
    client_name: str,
    redirect_uris: list[str],
    grant_types: list[str],
    response_types: list[str],
    token_endpoint_auth_method: str,
) -> ClientData:
    """Register a new OAuth client.

    Args:
        client_id: Unique client identifier.
        client_name: Human-readable client name.
        redirect_uris: List of allowed redirect URIs.
        grant_types: List of allowed grant types.
        response_types: List of allowed response types.
        token_endpoint_auth_method: Token endpoint authentication method.

    Returns:
        Registered client data.
    """
    client_data = ClientData(
        client_id=client_id,
        client_name=client_name,
        redirect_uris=redirect_uris,
        grant_types=grant_types,
        response_types=response_types,
        token_endpoint_auth_method=token_endpoint_auth_method,
        client_id_issued_at=int(time.time()),
    )
    _registered_clients[client_id] = client_data
    return client_data


def get_client(client_id: str) -> ClientData | None:
    """Retrieve registered client data.

    Args:
        client_id: Client identifier.

    Returns:
        Client data or None if not found.
    """
    return _registered_clients.get(client_id)
