# SearxNG MCP Server

A Model Context Protocol (MCP) server that provides search capabilities through [SearxNG](https://docs.searxng.org/), the privacy-respecting metasearch engine.

PyPi: https://pypi.org/project/searxng-mcp-server/#description

## Usage

### Using uvx

You can also just pip install this but we recommend using `uv`.

```bash
# With command line argument (stdio transport)
uvx searxng-mcp-server --searxng-url https://searx.be

# With environment variable (stdio transport)
SEARXNG_URL=https://searx.be uvx searxng-mcp-server

# With HTTP transport on port 8080
uvx searxng-mcp-server --searxng-url https://searx.be --port 8080

# With HTTP transport using environment variable
SEARXNG_URL=https://searx.be MCP_PORT=8080 uvx searxng-mcp-server
```

**Package link**: [https://pypi.org/project/searxng-mcp-server/](https://pypi.org/project/searxng-mcp-server/)

### Using Docker/Podman

```bash
# With command line argument (stdio transport)
podman run --rm -i docker.io/icewreck/searxng-mcp-server:latest --searxng-url https://searx.be

# With environment variable (stdio transport)
podman run --rm -i -e SEARXNG_URL=https://searx.be docker.io/icewreck/searxng-mcp-server:latest

# With HTTP transport on port 8080
podman run --rm -i -e SEARXNG_URL=https://searx.be -p 8080:8080 docker.io/icewreck/searxng-mcp-server:latest --port 8080
```

### Usage as Library

You can also use the SearxNG client directly in your Python projects. The client is fully async and requires `async/await` syntax.

For detailed examples, see the `examples/client_example.py` file in the repository.

The SearxNGClient can be easily integrated into custom AI agents as a search tool. All search methods are async and return structured response objects.

## Available Tools

- **`search_web`**: General web search with language and time filtering
- **`search_images`**: Image search across multiple search engines
- **`search_videos`**: Video search from various platforms
- **`search_news`**: News search with time range filtering
- **`fetch_url`**: Fetch content from a URL and convert it to markdown

## Configuration

The server requires a SearxNG instance URL. You can provide it via:

- **Environment Variable**: `SEARXNG_URL=https://your-searxng-instance.com`
- **Command Line Argument**: `--searxng-url https://your-searxng-instance.com`

By default, the server uses stdio transport. To enable HTTP transport, set a port:

- **Environment Variable**: `MCP_PORT=8080`
- **Command Line Argument**: `--port 8080`

When a port is provided, the server listens on `http://0.0.0.0:<port>` using the streamable-http transport.

Optional: `SEARXNG_TIMEOUT` (default: 30), `SEARXNG_USER_AGENT`, `LOG_LEVEL`
