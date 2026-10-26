# Bible MCP Server

A Model Context Protocol (MCP) server that provides Bible passage retrieval, built on [mcp-service-kit](https://github.com/geosp/mcp-service-kit).

This server lets AI assistants read Bible passages from various translations. It runs in two modes:

- **`--mode stdio`** (default): MCP over stdin/stdout, for local AI assistant integration
- **`--mode http`**: MCP over streamable HTTP at `/mcp`, for networked access

## Features

### MCP Tools (for AI assistants)
- `get_passage(passage, version)`: retrieves Bible passages. Pass several references separated by semicolons (e.g., "John 3:16; Romans 8:28") to get them all at once. If `version` is omitted, the configured default (ESV) is used.

### Bible Versions
`version` is passed to BibleGateway as-is, so any version abbreviation it offers works (e.g. `ESV`, `NIV`, `KJV`, `NASB`, `LSB`); there is no list to maintain here. See [BibleGateway's versions page](https://www.biblegateway.com/versions/). If a version isn't available, the tool returns `success: false` with the error.

## Installation

### Prerequisites
- Python 3.11+
- `uv` package manager

#### Installing uv

**On Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Alternatively, you can install uv using pip:
```bash
pip install uv
```

After installation, restart your terminal or run `source ~/.bashrc` (Linux/macOS) or restart your command prompt (Windows).

### Step 1: Install Dependencies

```bash
# From this directory
cd mcp-bible

# Install dependencies (including mcp-service-kit from GitHub)
uv sync
```

### Step 2: Configure Environment (optional)

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
vi .env
```

## Usage

### Mode 1: stdio (Default) - Local AI Assistant Integration

```bash
# Default mode - MCP over stdin/stdout
uv run mcp-bible

# Explicitly specify stdio mode
uv run mcp-bible --mode stdio
```

Use this mode to integrate directly with AI assistants such as GitHub Copilot or Claude Desktop.

### Mode 2: http - MCP over HTTP

```bash
uv run mcp-bible --mode http --port 3000 --no-auth
```

This serves MCP at `http://localhost:3000/mcp` for networked AI assistants.

No authentication provider is configured, so HTTP mode needs `--no-auth` (or `MCP_AUTH_ENABLED=false`). Without it, mcp-service-kit refuses to start rather than serve the tools unauthenticated. To protect the endpoint, override `create_auth_provider()` in `mcp_bible/server.py` (see [Authentication](https://github.com/geosp/mcp-service-kit#authentication) in the kit's README).

### Connect an MCP Client

You can test the MCP tools by connecting GitHub Copilot or another MCP client:

```json
// .vscode/mcp.json
{
  "servers": {
    "bible": {
      "type": "http",
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

Then ask Copilot:
- "Show me John 3:16"
- "What does Romans 8 say?"
- "Read Psalm 23 in NIV"

To debug interactively, run `npx @modelcontextprotocol/inspector` and point it at either transport.

### CLI Help and Options

```bash
# See all available options
uv run mcp-bible --help

# Usage examples:
uv run mcp-bible                                  # stdio mode (default)
uv run mcp-bible --mode http --no-auth --port 4000          # HTTP on port 4000
uv run mcp-bible --mode http --no-auth --log-level DEBUG    # verbose logging
```

### Environment Variables

Settings are read from the environment and from `.env`. Command-line flags take precedence.

| Variable                   | Default                                 | Description                          |
|----------------------------|-----------------------------------------|--------------------------------------|
| `MCP_HOST`                 | `0.0.0.0`                               | Host to bind to in HTTP mode (`--host`) |
| `MCP_PORT`                 | `3000`                                  | Port in HTTP mode (`--port`)         |
| `MCP_AUTH_ENABLED`         | `true`                                  | Require an auth provider in HTTP mode; set `false` (or `--no-auth`) to serve without one |
| `BIBLE_API_URL`            | `https://www.biblegateway.com/passage/` | BibleGateway passage URL             |
| `BIBLE_DEFAULT_VERSION`    | `ESV`                                   | Version used when none is requested  |
| `BIBLE_TIMEOUT`            | `30`                                    | HTTP request timeout in seconds      |

The transport is always taken from `--mode`, which defaults to `stdio`.

## Testing

```bash
# Unit and in-memory MCP tests (offline; BibleGateway is mocked)
uv run pytest
```

Live smoke test against a running HTTP server (this calls BibleGateway.com):

```bash
uv run mcp-bible --mode http --port 3000 --no-auth &
uv run python examples/client_example.py "John 3:16"
uv run python examples/client_example.py --url http://localhost:4000/mcp "Romans 8:28"
```

## Project Structure

```
mcp_bible/
├── __init__.py              # Package metadata (version)
├── config.py                # Configuration (BibleAPIConfig + kit's BaseServerConfig)
├── bible_service.py         # Business logic (BibleGateway client and parser)
├── service.py               # MCP service wrapper (automatic feature discovery)
├── server.py                # Server and CLI entry point (mcp-service-kit)
└── features/                # Feature modules
    ├── __init__.py
    └── get_passage/         # Get passage feature
        ├── __init__.py
        ├── instructions.md  # Tool documentation (injected into the docstring)
        ├── models.py        # Feature-specific models
        └── tool.py          # MCP tool definition (uses @inject_docstring)
tests/                       # pytest suite
examples/
└── client_example.py        # Live MCP client smoke test
```

## How It Works

### Features Pattern (Automatic Discovery)

`BibleMCPService` discovers every package under `features/` and calls the `register_tool(mcp, bible_service)` function in its `tool.py`.

**Add a new feature in 3 steps:**

1. **Create feature directory**: `features/my_feature/`
2. **Add instructions.md**: The tool's documentation in markdown
3. **Add tool.py**: With a `register_tool(mcp, service)` function

```python
# features/my_feature/tool.py
from mcp_service_kit.utils import inject_docstring, load_instruction


def register_tool(mcp, bible_service):
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def my_tool(param: str) -> dict:
        """Documentation loaded from instructions.md"""
        return {"result": param}
```

You don't need to register anything by hand.

### 1. Configuration Layer (config.py)

Each section is a pydantic-settings model that reads its own environment variables:

```python
from mcp_service_kit import BaseServerConfig

class BibleAPIConfig(BaseSettings):      # BIBLE_* variables
    api_url: str
    default_version: str

class AppConfig(BaseModel):
    server: BaseServerConfig              # MCP_* variables
    bible_api: BibleAPIConfig
```

### 2. Business Logic Layer (bible_service.py)

Business logic that knows nothing about MCP:

```python
class BibleService:
    def __init__(self, api_config: BibleAPIConfig): ...

    async def fetch_passage(self, passage: str, version: str | None = None) -> dict:
        ...
```

### 3. MCP Service Wrapper (service.py)

Implements the kit's `BaseService` to expose the business logic via MCP:

```python
from mcp_service_kit import BaseService

class BibleMCPService(BaseService):
    def register_mcp_tools(self, mcp: FastMCP) -> None:
        # Automatic feature discovery and registration
```

### 4. Server Implementation (server.py)

Extends the kit's `BaseMCPServer` and builds the CLI with `create_main_with_modes`:

```python
from mcp_service_kit import BaseMCPServer, create_main_with_modes

class BibleMCPServer(BaseMCPServer):
    service_title = ...        # plus service_description, service_version

main = create_main_with_modes(
    BibleMCPServer, create_bible_service, AppConfig, "mcp-bible", "..."
)
```

## Customization

### Add New Configuration

Edit `mcp_bible/config.py`:

```python
class BibleAPIConfig(BaseSettings):
    my_new_field: str = Field(default="value")   # read from BIBLE_MY_NEW_FIELD
```

### Add Middleware or Auth

`BibleMCPServer` can override the kit's hooks: `instructions`, `create_middleware()` (e.g. FastMCP's `ResponseCachingMiddleware`), `create_auth_provider()` and `validate_configuration()`. See [Server hooks](https://github.com/geosp/mcp-service-kit#server-hooks).

## Next Steps

- Add authentication (e.g. a `JWTVerifier` for Authentik via `create_auth_provider()`)
- Add more Bible API sources (Bible API, ESV API)
- Implement passage search and concordance
- Add daily verses and reading plans
- Add Redis caching (`mcp-service-kit[redis]`)
- Add metrics and monitoring

## Learn More

- [mcp-service-kit](https://github.com/geosp/mcp-service-kit)
- [FastMCP Documentation](https://gofastmcp.com)
- [Docker setup](docker/README.md)

## License

This project is provided as-is for use and modification.
