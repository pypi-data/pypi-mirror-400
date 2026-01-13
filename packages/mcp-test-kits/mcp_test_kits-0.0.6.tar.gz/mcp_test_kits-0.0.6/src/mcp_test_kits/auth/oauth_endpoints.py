"""OAuth authorization endpoints (/oauth/authorize, /oauth/token, /oauth/revoke)."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.routing import Route

from .jwt_handler import create_access_token
from .pkce import verify_code_challenge
from .token_store import (
    delete_authorization_code,
    get_authorization_code,
    register_client,
    revoke_token,
    store_access_token,
    store_authorization_code,
)

if TYPE_CHECKING:
    from ..config import Config


async def authorize_get(request: Request) -> Response:
    """Handle GET /oauth/authorize - Show consent or auto-approve.

    Query parameters:
        - client_id: Client identifier
        - redirect_uri: Callback URL
        - response_type: Must be 'code'
        - scope: Space-separated scopes
        - state: CSRF token (recommended)
        - code_challenge: PKCE S256 challenge
        - code_challenge_method: Must be 'S256'
        - resource: Target resource URI
    """
    config: Config = request.app.state.config

    # Parse and validate query parameters
    params = dict(request.query_params)
    errors = _validate_authorize_params(params)
    if errors:
        return _error_redirect(
            params.get("redirect_uri"), errors[0], params.get("state")
        )

    # Auto-approve mode (for testing)
    if config.oauth.auto_approve:
        code = secrets.token_urlsafe(32)
        store_authorization_code(
            code=code,
            client_id=params["client_id"],
            redirect_uri=params["redirect_uri"],
            scope=params["scope"],
            code_challenge=params["code_challenge"],
            code_challenge_method=params["code_challenge_method"],
            resource=params["resource"],
            state=params.get("state"),
            ttl=config.oauth.authorization_code_ttl,
        )
        return _success_redirect(params["redirect_uri"], code, params.get("state"))

    # Show consent form
    return _render_consent_form(params)


async def authorize_post(request: Request) -> Response:
    """Handle POST /oauth/authorize - Process consent form submission."""
    config: Config = request.app.state.config
    form_data = await request.form()
    params: dict[str, str] = {k: str(v) for k, v in form_data.items()}
    action = params.get("action")

    # User denied
    if action == "deny":
        return _error_redirect(
            params.get("redirect_uri"),
            "access_denied",
            params.get("state"),
            "User denied consent",
        )

    # User approved
    if action == "approve":
        code = secrets.token_urlsafe(32)
        store_authorization_code(
            code=code,
            client_id=params["client_id"],
            redirect_uri=params["redirect_uri"],
            scope=params["scope"],
            code_challenge=params["code_challenge"],
            code_challenge_method=params["code_challenge_method"],
            resource=params["resource"],
            state=params.get("state"),
            ttl=config.oauth.authorization_code_ttl,
        )
        return _success_redirect(params["redirect_uri"], code, params.get("state"))

    return HTMLResponse("Invalid action", status_code=400)


async def token_post(request: Request) -> Response:
    """Handle POST /oauth/token - Exchange authorization code for access token.

    Form parameters:
        - grant_type: Must be 'authorization_code'
        - code: Authorization code
        - client_id: Client identifier
        - redirect_uri: Must match authorization request
        - code_verifier: PKCE verifier
        - resource: Target resource URI
    """
    config: Config = request.app.state.config
    form_data = await request.form()
    params: dict[str, str] = {k: str(v) for k, v in form_data.items()}

    # Validate grant_type
    if params.get("grant_type") != "authorization_code":
        return _token_error("unsupported_grant_type")

    # Get authorization code
    code = params.get("code")
    if not code:
        return _token_error("invalid_request", "Missing code parameter")

    auth_data = get_authorization_code(code)
    if not auth_data:
        return _token_error("invalid_grant", "Invalid or expired authorization code")

    # Validate client_id
    if params.get("client_id") != auth_data.client_id:
        return _token_error("invalid_client")

    # Validate redirect_uri
    if params.get("redirect_uri") != auth_data.redirect_uri:
        return _token_error("invalid_grant", "Redirect URI mismatch")

    # Validate PKCE verifier
    code_verifier = params.get("code_verifier")
    if not code_verifier:
        return _token_error("invalid_request", "Missing code_verifier")

    if not verify_code_challenge(code_verifier, auth_data.code_challenge):
        return _token_error("invalid_grant", "Invalid code_verifier")

    # Delete authorization code (one-time use)
    delete_authorization_code(code)

    # Get issuer
    issuer = config.oauth.issuer or _build_issuer(config, request)

    # Create access token
    access_token = create_access_token(
        subject="test-user",
        scopes=auth_data.scope,
        resource=auth_data.resource,
        issuer=issuer,
        expiration=config.oauth.token_expiration,
    )

    # Store token metadata (for revocation)
    import jwt

    decoded = jwt.decode(access_token, options={"verify_signature": False})
    store_access_token(
        jti=decoded["jti"],
        subject=decoded["sub"],
        scopes=auth_data.scope,
        resource=auth_data.resource,
        expires_in=config.oauth.token_expiration,
    )

    return Response(
        content=f'{{"access_token":"{access_token}","token_type":"Bearer","expires_in":{config.oauth.token_expiration},"scope":"{auth_data.scope}"}}',
        media_type="application/json",
    )


async def revoke_post(request: Request) -> Response:
    """Handle POST /oauth/revoke - Revoke access token.

    Form parameters:
        - token: Access token to revoke
        - token_type_hint: Optional hint ('access_token')
    """
    form_data = await request.form()
    token_value = form_data.get("token")

    if token_value and isinstance(token_value, str):
        # Extract jti from token
        import jwt

        try:
            decoded = jwt.decode(token_value, options={"verify_signature": False})
            jti = decoded.get("jti")
            if jti:
                revoke_token(jti)
        except Exception:
            pass  # Ignore errors per RFC 7009

    # Always return 200 OK (per RFC 7009)
    return Response(status_code=200)


async def register_post(request: Request) -> Response:
    """Handle POST /oauth/register - Dynamic Client Registration (RFC 7591).

    JSON body parameters:
        - client_name: Human-readable client name (required)
        - redirect_uris: Array of redirect URIs (required)
        - grant_types: Array of grant types (optional, default: ["authorization_code"])
        - response_types: Array of response types (optional, default: ["code"])
        - token_endpoint_auth_method: Auth method (optional, default: "none")
    """
    import json
    import uuid

    try:
        body = await request.json()
    except Exception:
        return _registration_error("invalid_request", "Invalid JSON body")

    # Validate required fields
    client_name = body.get("client_name")
    redirect_uris = body.get("redirect_uris")

    if not client_name or not isinstance(client_name, str):
        return _registration_error("invalid_request", "Missing or invalid client_name")

    if not redirect_uris or not isinstance(redirect_uris, list) or not redirect_uris:
        return _registration_error(
            "invalid_request", "Missing or invalid redirect_uris"
        )

    # Validate redirect URIs
    for uri in redirect_uris:
        if not isinstance(uri, str) or not uri.startswith(("http://", "https://")):
            return _registration_error(
                "invalid_redirect_uri", f"Invalid redirect URI: {uri}"
            )

    # Extract optional fields with defaults
    grant_types = body.get("grant_types", ["authorization_code"])
    response_types = body.get("response_types", ["code"])
    token_endpoint_auth_method = body.get("token_endpoint_auth_method", "none")

    # Validate grant_types and response_types
    if not isinstance(grant_types, list) or "authorization_code" not in grant_types:
        return _registration_error(
            "invalid_request", "Only authorization_code grant type supported"
        )

    if not isinstance(response_types, list) or "code" not in response_types:
        return _registration_error(
            "invalid_request", "Only code response type supported"
        )

    # Generate unique client_id
    client_id = str(uuid.uuid4())

    # Register client
    client_data = register_client(
        client_id=client_id,
        client_name=client_name,
        redirect_uris=redirect_uris,
        grant_types=grant_types,
        response_types=response_types,
        token_endpoint_auth_method=token_endpoint_auth_method,
    )

    # Return client registration response
    response_body = {
        "client_id": client_data.client_id,
        "client_name": client_data.client_name,
        "redirect_uris": client_data.redirect_uris,
        "grant_types": client_data.grant_types,
        "response_types": client_data.response_types,
        "token_endpoint_auth_method": client_data.token_endpoint_auth_method,
        "client_id_issued_at": client_data.client_id_issued_at,
    }

    return Response(
        content=json.dumps(response_body),
        status_code=201,
        media_type="application/json",
    )


def _validate_authorize_params(params: dict[str, str]) -> list[str]:
    """Validate authorization request parameters."""
    errors = []

    required = [
        "client_id",
        "redirect_uri",
        "response_type",
        "scope",
        "code_challenge",
        "code_challenge_method",
        "resource",
    ]
    for param in required:
        if not params.get(param):
            errors.append(f"invalid_request: Missing {param}")

    if params.get("response_type") != "code":
        errors.append("unsupported_response_type")

    if params.get("code_challenge_method") != "S256":
        errors.append("invalid_request: Only S256 code_challenge_method supported")

    return errors


def _success_redirect(
    redirect_uri: str, code: str, state: str | None
) -> RedirectResponse:
    """Redirect with authorization code."""
    params = {"code": code}
    if state:
        params["state"] = state
    return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=302)


def _error_redirect(
    redirect_uri: str | None,
    error: str,
    state: str | None = None,
    error_description: str | None = None,
) -> Response:
    """Redirect with OAuth error."""
    if not redirect_uri:
        return HTMLResponse(f"Error: {error}", status_code=400)

    params = {"error": error}
    if error_description:
        params["error_description"] = error_description
    if state:
        params["state"] = state

    return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=302)


def _token_error(error: str, error_description: str | None = None) -> Response:
    """Return OAuth token error response."""
    response_data = {"error": error}
    if error_description:
        response_data["error_description"] = error_description

    import json

    return Response(
        content=json.dumps(response_data),
        status_code=400,
        media_type="application/json",
    )


def _registration_error(error: str, error_description: str | None = None) -> Response:
    """Return OAuth client registration error response."""
    response_data = {"error": error}
    if error_description:
        response_data["error_description"] = error_description

    import json

    return Response(
        content=json.dumps(response_data),
        status_code=400,
        media_type="application/json",
    )


def _render_consent_form(params: dict[str, str]) -> HTMLResponse:
    """Render consent form HTML."""
    import html as html_module

    # Escape all user-controlled values to prevent HTML injection
    client_id = html_module.escape(params["client_id"])
    redirect_uri = html_module.escape(params["redirect_uri"])
    resource = html_module.escape(params["resource"])
    scope = html_module.escape(params["scope"])
    state = html_module.escape(params.get("state", ""))
    code_challenge = html_module.escape(params["code_challenge"])
    code_challenge_method = html_module.escape(params["code_challenge_method"])
    scopes_html = "<br>".join(
        f"• {html_module.escape(s)}" for s in params["scope"].split()
    )

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <title>OAuth Authorization</title>
  <style>
    body {{ font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
    .scopes {{ margin: 20px 0; }}
    button {{ margin: 10px 10px 10px 0; padding: 10px 20px; font-size: 16px; cursor: pointer; }}
    .approve {{ background: #28a745; color: white; border: none; }}
    .deny {{ background: #dc3545; color: white; border: none; }}
  </style>
</head>
<body>
  <h1>Authorization Request</h1>
  <p><strong>Client:</strong> {client_id}</p>
  <p><strong>Redirect URI:</strong> {redirect_uri}</p>
  <p><strong>Resource:</strong> {resource}</p>

  <div class="scopes">
    <strong>Requested Scopes:</strong><br>
    {scopes_html}
  </div>

  <form method="POST" action="/oauth/authorize">
    <input type="hidden" name="client_id" value="{client_id}">
    <input type="hidden" name="redirect_uri" value="{redirect_uri}">
    <input type="hidden" name="scope" value="{scope}">
    <input type="hidden" name="state" value="{state}">
    <input type="hidden" name="code_challenge" value="{code_challenge}">
    <input type="hidden" name="code_challenge_method" value="{code_challenge_method}">
    <input type="hidden" name="resource" value="{resource}">

    <button type="submit" name="action" value="approve" class="approve">Approve</button>
    <button type="submit" name="action" value="deny" class="deny">Deny</button>
  </form>
</body>
</html>
"""
    return HTMLResponse(html_content)


def _build_issuer(config: Config, request: Request) -> str:
    """Build issuer URL from config and request."""
    host = config.transport.network.host
    port = config.transport.network.port
    scheme = request.url.scheme

    if host in ("0.0.0.0", ""):
        host = "localhost"

    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        return f"{scheme}://{host}"
    return f"{scheme}://{host}:{port}"


def register_oauth_routes(app: Starlette, config: Config) -> None:
    """Register OAuth endpoint routes.

    Args:
        app: Starlette application.
        config: Server configuration.
    """
    app.state.config = config
    app.routes.extend(
        [
            Route("/oauth/authorize", authorize_get, methods=["GET"]),
            Route("/oauth/authorize", authorize_post, methods=["POST"]),
            Route("/oauth/token", token_post, methods=["POST"]),
            Route("/oauth/revoke", revoke_post, methods=["POST"]),
            Route("/oauth/register", register_post, methods=["POST"]),
        ]
    )
