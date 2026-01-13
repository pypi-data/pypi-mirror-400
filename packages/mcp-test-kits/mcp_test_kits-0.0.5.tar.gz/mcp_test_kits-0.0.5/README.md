# MCP Test Kits - Python

Build from source using FastMCP.

## Build

```bash
cd python
uv sync
```

---

## stdio

```json
{
  "mcpServers": {
    "mcp-test-kits": {
      "command": "uv",
      "args": ["run", "mcp-test-kits"],
      "cwd": "/path/to/mcp-test-kits/python",
      "transport": "stdio"
    }
  }
}
```

---

## HTTP

Start server:
```bash
uv run mcp-test-kits --transport http --port 3000
```

MCP client config:
```json
{
  "mcpServers": {
    "mcp-test-kits": {
      "url": "http://localhost:3000/mcp",
      "transport": "http"
    }
  }
}
```

### With OAuth

Start server:
```bash
uv run mcp-test-kits --transport http --port 3000 --enable-oauth
# or auto-approve for testing
uv run mcp-test-kits --transport http --port 3000 --enable-oauth --oauth-auto-approve
```

MCP client config (OAuth discovery automatic):
```json
{
  "mcpServers": {
    "mcp-test-kits": {
      "url": "http://localhost:3000/mcp",
      "transport": "http"
    }
  }
}
```

Or with pre-obtained token:
```json
{
  "mcpServers": {
    "mcp-test-kits": {
      "url": "http://localhost:3000/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
      }
    }
  }
}
```

---

## SSE

Start server:
```bash
uv run mcp-test-kits --transport sse --port 3000
```

MCP client config:
```json
{
  "mcpServers": {
    "mcp-test-kits": {
      "url": "http://localhost:3000/sse",
      "transport": "sse"
    }
  }
}
```

### With OAuth

Start server:
```bash
uv run mcp-test-kits --transport sse --port 3000 --enable-oauth
# or auto-approve for testing
uv run mcp-test-kits --transport sse --port 3000 --enable-oauth --oauth-auto-approve
```

MCP client config (OAuth discovery automatic):
```json
{
  "mcpServers": {
    "mcp-test-kits": {
      "url": "http://localhost:3000/sse",
      "transport": "sse"
    }
  }
}
```

Or with pre-obtained token:
```json
{
  "mcpServers": {
    "mcp-test-kits": {
      "url": "http://localhost:3000/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
      }
    }
  }
}
```

---

## Test with MCP Inspector

```bash
# stdio
npx @modelcontextprotocol/inspector uv run mcp-test-kits

# HTTP (start server first: uv run mcp-test-kits --transport http --port 3000)
npx @modelcontextprotocol/inspector --transport http --server-url http://localhost:3000/mcp

# SSE (start server first: uv run mcp-test-kits --transport sse --port 3000)
npx @modelcontextprotocol/inspector --transport sse --server-url http://localhost:3000/sse
```

---

## Development

```bash
uv sync --all-extras
uv run pytest
uv run mypy src --check-untyped-defs
uv run ruff check src
```
