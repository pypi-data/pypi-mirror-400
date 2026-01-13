#!/usr/bin/env python3
"""Extract specification from MCP Test Kits server.

This script extracts the tools, resources, and prompts specification
from the Python implementation and outputs JSON that can be compared
against the shared specification.

Usage:
    uv run python -m mcp_test_kits.extract_spec > extracted_spec.json
    # Or compare directly:
    uv run python -m mcp_test_kits.extract_spec --compare
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from .config import Config
from .server import create_server


async def extract_tools_spec(mcp: FastMCP) -> list[dict[str, Any]]:
    """Extract tool specifications from server."""
    tools: list[dict[str, Any]] = []
    # get_tools() returns dict[str, Tool] (async)
    tools_dict = await mcp._tool_manager.get_tools()
    for name, tool in tools_dict.items():
        tools.append(
            {
                "name": name,
                "description": tool.description or "",
            }
        )
    return sorted(tools, key=lambda t: t["name"])


async def extract_resources_spec(mcp: FastMCP) -> list[dict[str, Any]]:
    """Extract resource specifications from server."""
    resources: list[dict[str, Any]] = []
    # get_resources() returns dict[str, Resource] (async)
    resources_dict = await mcp._resource_manager.get_resources()
    for uri, resource in resources_dict.items():
        resources.append(
            {
                "uri": str(uri),
                "name": resource.name or "",
                "mimeType": resource.mime_type or "text/plain",
            }
        )
    return sorted(resources, key=lambda r: r["uri"])


async def extract_prompts_spec(mcp: FastMCP) -> list[dict[str, Any]]:
    """Extract prompt specifications from server."""
    prompts: list[dict[str, Any]] = []
    # get_prompts() returns dict[str, Prompt] (async)
    prompts_dict = await mcp._prompt_manager.get_prompts()
    for name, prompt in prompts_dict.items():
        args: list[dict[str, Any]] = []
        if hasattr(prompt, "arguments") and prompt.arguments:
            for arg in prompt.arguments:
                args.append(
                    {
                        "name": arg.name,
                        "description": arg.description or "",
                        "required": arg.required if hasattr(arg, "required") else False,
                    }
                )
        prompts.append(
            {
                "name": name,
                "description": prompt.description or "",
                "arguments": args,
            }
        )
    return sorted(prompts, key=lambda p: p["name"])


async def extract_spec() -> dict[str, Any]:
    """Extract full specification from server."""
    config = Config()
    mcp = create_server(config)

    return {
        "tools": await extract_tools_spec(mcp),
        "resources": await extract_resources_spec(mcp),
        "prompts": await extract_prompts_spec(mcp),
    }


def load_shared_spec() -> dict[str, Any]:
    """Load shared specification from JSON files."""
    shared_dir = Path(__file__).parent.parent.parent.parent / "shared" / "test-data"

    tools: list[dict[str, Any]] = []
    resources: list[dict[str, Any]] = []
    prompts: list[dict[str, Any]] = []

    tools_file = shared_dir / "tools.json"
    if tools_file.exists():
        with open(tools_file) as f:
            data = json.load(f)
            tools = data.get("tools", [])

    resources_file = shared_dir / "resources.json"
    if resources_file.exists():
        with open(resources_file) as f:
            data = json.load(f)
            resources = data.get("resources", [])

    prompts_file = shared_dir / "prompts.json"
    if prompts_file.exists():
        with open(prompts_file) as f:
            data = json.load(f)
            prompts = data.get("prompts", [])

    return {
        "tools": sorted(tools, key=lambda t: t["name"]),
        "resources": sorted(resources, key=lambda r: r["uri"]),
        "prompts": sorted(prompts, key=lambda p: p["name"]),
    }


def compare_specs(
    extracted: dict[str, Any], shared: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Compare extracted spec against shared spec."""
    results: dict[str, dict[str, Any]] = {
        "tools": {"match": True, "missing": [], "extra": []},
        "resources": {"match": True, "missing": [], "extra": []},
        "prompts": {"match": True, "missing": [], "extra": []},
    }

    # Compare tools by name
    extracted_tool_names = {t["name"] for t in extracted["tools"]}
    shared_tool_names = {t["name"] for t in shared["tools"]}

    results["tools"]["missing"] = list(shared_tool_names - extracted_tool_names)
    results["tools"]["extra"] = list(extracted_tool_names - shared_tool_names)
    missing_tools: list[str] = results["tools"]["missing"]
    extra_tools: list[str] = results["tools"]["extra"]
    results["tools"]["match"] = len(missing_tools) == 0 and len(extra_tools) == 0

    # Compare resources by URI
    extracted_resource_uris = {r["uri"] for r in extracted["resources"]}
    shared_resource_uris = {r["uri"] for r in shared["resources"]}

    results["resources"]["missing"] = list(
        shared_resource_uris - extracted_resource_uris
    )
    results["resources"]["extra"] = list(extracted_resource_uris - shared_resource_uris)
    missing_resources: list[str] = results["resources"]["missing"]
    extra_resources: list[str] = results["resources"]["extra"]
    results["resources"]["match"] = (
        len(missing_resources) == 0 and len(extra_resources) == 0
    )

    # Compare prompts by name
    extracted_prompt_names = {p["name"] for p in extracted["prompts"]}
    shared_prompt_names = {p["name"] for p in shared["prompts"]}

    results["prompts"]["missing"] = list(shared_prompt_names - extracted_prompt_names)
    results["prompts"]["extra"] = list(extracted_prompt_names - shared_prompt_names)
    missing_prompts: list[str] = results["prompts"]["missing"]
    extra_prompts: list[str] = results["prompts"]["extra"]
    results["prompts"]["match"] = len(missing_prompts) == 0 and len(extra_prompts) == 0

    return results


async def async_main(args: argparse.Namespace) -> None:
    """Async main function."""
    extracted = await extract_spec()

    if args.compare:
        shared = load_shared_spec()
        results = compare_specs(extracted, shared)

        all_match = all(r["match"] for r in results.values())

        output = {
            "status": "pass" if all_match else "fail",
            "comparison": results,
        }

        output_str = json.dumps(output, indent=2)

        if args.output:
            args.output.write_text(output_str)
        else:
            print(output_str)

        sys.exit(0 if all_match else 1)
    else:
        output_str = json.dumps(extracted, indent=2)

        if args.output:
            args.output.write_text(output_str)
        else:
            print(output_str)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract MCP Test Kits specification")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare extracted spec against shared spec",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file (default: stdout)",
    )
    args = parser.parse_args()

    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
