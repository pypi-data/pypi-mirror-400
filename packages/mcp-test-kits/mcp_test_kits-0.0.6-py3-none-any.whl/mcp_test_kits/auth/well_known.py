"""Well-known OAuth discovery endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .scopes import get_all_supported_scopes

if TYPE_CHECKING:
    from ..config import Config


def protected_resource_metadata(request: Request) -> JSONResponse:
    """OAuth Protected Resource Metadata endpoint (RFC 9728).

    Returns metadata about the protected MCP server.
    """
    config: Config = request.app.state.config
    issuer = _get_issuer(config, request)

    return JSONResponse(
        {
            "resource": issuer,
            "authorization_servers": [issuer],
            "bearer_methods_supported": ["header"],
            "resource_documentation": f"{issuer}/docs",
            "scopes_supported": get_all_supported_scopes(),
        }
    )


def authorization_server_metadata(request: Request) -> JSONResponse:
    """OAuth Authorization Server Metadata endpoint (RFC 8414).

    Returns metadata about the OAuth authorization server.
    """
    config: Config = request.app.state.config
    issuer = _get_issuer(config, request)

    return JSONResponse(
        {
            "issuer": issuer,
            "authorization_endpoint": f"{issuer}/oauth/authorize",
            "token_endpoint": f"{issuer}/oauth/token",
            "revocation_endpoint": f"{issuer}/oauth/revoke",
            "registration_endpoint": f"{issuer}/oauth/register",
            "code_challenge_methods_supported": ["S256"],
            "grant_types_supported": ["authorization_code"],
            "response_types_supported": ["code"],
            "token_endpoint_auth_methods_supported": ["none"],
            "client_id_metadata_document_supported": True,
            "scopes_supported": get_all_supported_scopes(),
        }
    )


def _get_issuer(config: Config, request: Request) -> str:
    """Get OAuth issuer URL.

    Args:
        config: Server configuration.
        request: HTTP request.

    Returns:
        Issuer URL.
    """
    if config.oauth.issuer:
        return config.oauth.issuer

    # Build issuer from request
    host = config.transport.network.host
    port = config.transport.network.port
    scheme = request.url.scheme

    # Use localhost if host is 0.0.0.0
    if host in ("0.0.0.0", ""):
        host = "localhost"

    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        return f"{scheme}://{host}"
    return f"{scheme}://{host}:{port}"


def register_well_known_routes(app: Starlette, config: Config) -> None:
    """Register well-known OAuth discovery routes.

    Args:
        app: Starlette application.
        config: Server configuration.
    """
    app.state.config = config
    app.routes.extend(
        [
            Route(
                "/.well-known/oauth-protected-resource",
                protected_resource_metadata,
                methods=["GET"],
            ),
            Route(
                "/.well-known/oauth-authorization-server",
                authorization_server_metadata,
                methods=["GET"],
            ),
        ]
    )
