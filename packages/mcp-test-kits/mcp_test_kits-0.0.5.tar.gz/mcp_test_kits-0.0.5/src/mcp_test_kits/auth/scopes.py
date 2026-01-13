"""OAuth scope parsing and validation."""

from __future__ import annotations


def parse_scopes(scope_string: str) -> list[str]:
    """Parse space-separated scope string into list.

    Args:
        scope_string: Space-separated scopes.

    Returns:
        List of individual scopes.
    """
    return scope_string.split() if scope_string else []


def has_required_scope(token_scopes: list[str], required_scope: str) -> bool:
    """Check if token has required scope (exact or wildcard match).

    Args:
        token_scopes: List of scopes from token.
        required_scope: Required scope to check.

    Returns:
        True if token has required scope, False otherwise.
    """
    # Exact match
    if required_scope in token_scopes:
        return True

    # Wildcard match (e.g., mcp:tools:* covers mcp:tools:echo)
    scope_parts = required_scope.split(":")
    for token_scope in token_scopes:
        if token_scope.endswith(":*"):
            # Check if wildcard scope is a prefix
            prefix = token_scope[:-2]  # Remove :*
            required_prefix = ":".join(scope_parts[:-1])  # Remove last part
            if required_prefix == prefix:
                return True

    return False


def get_required_scope_for_tool(tool_name: str) -> str:
    """Get required scope for a specific tool.

    Args:
        tool_name: Tool name.

    Returns:
        Required scope string.
    """
    return f"mcp:tools:{tool_name}"


def get_required_scope_for_resource(uri: str) -> str:
    """Get required scope for a resource URI.

    Args:
        uri: Resource URI.

    Returns:
        Required scope string.
    """
    # For simplicity, require mcp:resources:* for all resources
    return "mcp:resources:*"


def get_required_scope_for_prompt(prompt_name: str) -> str:
    """Get required scope for a specific prompt.

    Args:
        prompt_name: Prompt name.

    Returns:
        Required scope string.
    """
    return "mcp:prompts:*"


def get_all_supported_scopes() -> list[str]:
    """Get list of all supported scopes.

    Returns:
        List of supported scope strings.
    """
    return [
        "mcp:tools:*",
        "mcp:tools:echo",
        "mcp:tools:add",
        "mcp:tools:multiply",
        "mcp:tools:reverse_string",
        "mcp:tools:generate_uuid",
        "mcp:tools:get_timestamp",
        "mcp:tools:sample_error",
        "mcp:tools:long_running_task",
        "mcp:resources:*",
        "mcp:prompts:*",
    ]
