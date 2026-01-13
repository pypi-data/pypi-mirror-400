"""OAuth authentication middleware for Starlette."""

from __future__ import annotations

from typing import TYPE_CHECKING

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .jwt_handler import validate_token
from .token_store import is_token_revoked

if TYPE_CHECKING:
    from starlette.types import ASGIApp

    from ..config import Config


class OAuthMiddleware(BaseHTTPMiddleware):
    """OAuth authentication middleware.

    Validates Bearer tokens on all requests except OAuth endpoints.
    """

    def __init__(self, app: ASGIApp, config: Config) -> None:
        """Initialize OAuth middleware.

        Args:
            app: ASGI application.
            config: Server configuration.
        """
        super().__init__(app)
        self.config = config

    async def dispatch(self, request: Request, call_next):  # type: ignore
        """Process request with OAuth validation.

        Args:
            request: HTTP request.
            call_next: Next middleware/handler.

        Returns:
            HTTP response.
        """
        # Skip OAuth-related endpoints
        if request.url.path.startswith(("/.well-known", "/oauth")):
            return await call_next(request)

        # Get issuer
        issuer = self.config.oauth.issuer or self._build_issuer(request)

        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return self._unauthorized_response(issuer)

        # Extract token
        token = auth_header[7:]  # Remove "Bearer " prefix

        # Validate token
        try:
            payload = validate_token(token, issuer)
        except jwt.InvalidTokenError:
            return self._unauthorized_response(issuer, "Invalid token")

        # Check if token is revoked
        jti = payload.get("jti")
        if jti and is_token_revoked(jti):
            return self._unauthorized_response(issuer, "Token revoked")

        # Attach token payload to request state
        request.state.oauth_token = payload

        return await call_next(request)

    def _unauthorized_response(self, issuer: str, error: str | None = None) -> Response:
        """Return 401 Unauthorized response with WWW-Authenticate header.

        Args:
            issuer: OAuth issuer URL.
            error: Optional error message.

        Returns:
            401 response.
        """
        www_authenticate = (
            f'Bearer realm="{issuer}", '
            f'resource_metadata="{issuer}/.well-known/oauth-protected-resource"'
        )

        if error:
            www_authenticate += f', error="invalid_token", error_description="{error}"'

        return JSONResponse(
            {"error": "unauthorized", "message": "Valid Bearer token required"},
            status_code=401,
            headers={"WWW-Authenticate": www_authenticate},
        )

    def _build_issuer(self, request: Request) -> str:
        """Build issuer URL from config and request.

        Args:
            request: HTTP request.

        Returns:
            Issuer URL.
        """
        host = self.config.transport.network.host
        port = self.config.transport.network.port
        scheme = request.url.scheme

        if host in ("0.0.0.0", ""):
            host = "localhost"

        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            return f"{scheme}://{host}"
        return f"{scheme}://{host}:{port}"
