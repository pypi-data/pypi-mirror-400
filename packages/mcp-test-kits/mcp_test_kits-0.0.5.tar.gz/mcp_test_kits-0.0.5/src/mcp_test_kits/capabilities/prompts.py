"""Prompt implementations for MCP Test Kits."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all prompts with the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.prompt(description="A basic prompt with no arguments")
    def simple_prompt() -> str:
        """Return a simple prompt with no arguments."""
        return "You are a helpful assistant. Please respond concisely and accurately."

    @mcp.prompt(description="Generate a greeting message")
    def greeting_prompt(
        name: str = Field(description="Name of the person to greet"),
        style: str = Field(
            default="friendly", description="Greeting style (formal, casual, friendly)"
        ),
    ) -> str:
        """Generate a greeting message."""
        return f"Generate a {style} greeting for {name}."

    @mcp.prompt(description="A template with multiple arguments")
    def template_prompt(
        topic: str = Field(description="Main topic"),
        context: str = Field(default="", description="Additional context"),
        length: str = Field(
            default="medium", description="Desired length (short, medium, long)"
        ),
    ) -> str:
        """Generate a template prompt with multiple arguments."""
        text = f"Write a {length} explanation about {topic}."
        if context:
            text += f" Context: {context}"
        return text

    @mcp.prompt(description="Prompt that returns multiple messages")
    def multi_message_prompt(
        count: str = Field(description="Number of messages to generate"),
    ) -> str:
        """Generate a prompt requesting multiple messages."""
        try:
            num_messages = int(count)
        except ValueError:
            num_messages = 1

        # Clamp to reasonable range
        num_messages = max(1, min(num_messages, 10))

        return f"Generate {num_messages} distinct helpful messages."
