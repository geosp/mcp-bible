# MCP Bible Docker Setup

This directory contains Docker Compose configurations that run the MCP Bible server over streamable HTTP (`mcp-bible --mode http --no-auth`). MCP is served at `http://localhost:3000/mcp`.

## Available Setups

### Development Setup (build locally)
- **`docker-compose.yml`**: Builds the image locally and runs the mounted source code

### Production Setups (use published images)
- **`docker-compose.prod.yml`**: Uses the published GHCR image (`:main`)
- **Versioned Releases**: Use semantic version tags for stable releases (e.g., `docker-compose.prod.v1.0.0.yml`). Note that `v1.0.0` predates the mcp-service-kit migration and uses the old `MCP_ONLY` settings.

## Prerequisites

- Docker and Docker Compose installed
- Git (for cloning dependencies)

## Quick Start

### Development Mode (Recommended for local development)

```bash
cd docker
docker-compose up --build -d
```

### Production Mode (Uses published images)

**Note**: Production setups use the published Docker image from GHCR and run the package directly from the GitHub repository using `uvx mcp-bible@git+https://github.com/geosp/mcp-bible.git --mode http --no-auth`.

```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

#### Versioned Releases (Recommended for Production)
For stable production deployments using specific versions:

```bash
cd docker
docker-compose -f docker-compose.prod.v1.0.0.yml up -d
```

### Check Status
```bash
# Development
docker-compose logs -f mcp-bible

# Production
docker-compose -f docker-compose.prod.yml logs -f mcp-bible
```

### Stop Services
```bash
# Development
docker-compose down

# Production
docker-compose -f docker-compose.prod.yml down

# Production versioned
docker-compose -f docker-compose.prod.v1.0.0.yml down
```

## Configuration

### Development Setup (docker-compose.yml)
The service is configured to:
- Build from the parent directory's Dockerfile
- Mount the project directory as `/app` for live code changes
- Expose port 3000 for MCP communication
- Run `mcp-bible --mode http --no-auth` (MCP over streamable HTTP at `/mcp`)
- Use uvx to run the local MCP Bible package

### Production Setup (docker-compose.prod.yml)
The service is configured to:
- Use published image: `ghcr.io/geosp/mcp-bible:main`
- Expose port 3000 for MCP communication
- Run `mcp-bible --mode http --no-auth` (MCP over streamable HTTP at `/mcp`)
- No source code mounting required

## Development

For the development setup, the volume mount lets you change the code without rebuilding the container. Restart the service after changes:

```bash
docker-compose restart mcp-bible
```

**Note**: Production setups use published images and do not support live code reloading.

## Troubleshooting

- If you encounter permission issues, ensure Docker is running and you have proper permissions
- Check the logs with `docker-compose logs mcp-bible` for detailed error messages
- The container uses uv for Python package management, which handles dependencies automatically
- Only the `/mcp` endpoint is served; there is no REST API or `/health` endpoint
- No auth provider is configured, so the compose files pass `--no-auth`; without it the server exits with `Configuration error: HTTP transport has auth enabled...`
- **Production mode**: Uses `uvx` to run the package directly from the GitHub repository (`git+https://github.com/geosp/mcp-bible.git`)
- **Versioned deployments**: Use specific version tags (e.g., `:v1.0.0`) for stable, immutable deployments instead of `:main` for bleeding-edge

## Environment Variables

You can add environment variables in the `docker-compose.yml` files under the `environment` section if needed for configuration. See the main [README](../README.md#environment-variables) for the full list.

- `MCP_PORT`: Port to listen on inside the container (default `3000`)
- `BIBLE_DEFAULT_VERSION`: Version used when none is requested (default `ESV`)
- `UV_CACHE_DIR=/tmp/uv-cache`: Sets the cache directory for uv package manager

## Advanced: LXC Environment Setup

If you're running in an LXC container (advanced users), you may need special configuration:

### Prerequisites for LXC
- Podman with podman-compose installed
- LXC container configured for privileged operations

### LXC Configuration
Add these lines to your LXC config file:

```
lxc.cap.drop =
lxc.mount.auto = proc:rw sys:rw
```

### Running in LXC
Use `sudo` with podman-compose commands:

```bash
# Development mode
sudo podman-compose up --build -d
sudo podman-compose logs -f mcp-bible
sudo podman-compose down

# Production mode
sudo podman-compose -f docker-compose.prod.yml up -d
sudo podman-compose -f docker-compose.prod.yml logs -f mcp-bible
sudo podman-compose -f docker-compose.prod.yml down

# Production versioned mode
sudo podman-compose -f docker-compose.prod.v1.0.0.yml up -d
sudo podman-compose -f docker-compose.prod.v1.0.0.yml logs -f mcp-bible
sudo podman-compose -f docker-compose.prod.v1.0.0.yml down
```

If you encounter container build failures in LXC, the privileged configuration above should resolve the `/proc` mount permission errors.

## Claude Desktop Integration

To use the MCP Bible server with Claude Desktop, you'll need to install and configure [MCP Bridge](https://github.com/geosp/mcp-bridge), which allows Claude Desktop to connect to remote MCP servers over HTTP/SSE.

### Prerequisites

- Claude Desktop installed
- MCP Bridge installed from GitHub:
  ```bash
  uv pip install git+https://github.com/geosp/mcp-bridge.git
  ```

### Setup Steps

1. **Start your MCP Bible server** using one of the Docker configurations above
2. **Initialize MCP Bridge configuration**:
   ```bash
   mcp-bridge init --name bible
   ```
3. **Edit the configuration file** at `~/.config/mcp-bridge/bible.json`:
   ```json
   {
     "url": "http://localhost:3000/mcp"
   }
   ```
   Adjust the URL if your server is running on a different host/port.

4. **Configure Claude Desktop** by editing the configuration file:

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

   Add the MCP server configuration:
   ```json
   {
     "mcpServers": {
       "bible": {
         "command": "mcp-bridge",
         "args": ["--config", "bible.json"]
       }
     }
   }
   ```

5. **Restart Claude Desktop**

### Testing the Integration

You can test the bridge connection before configuring Claude Desktop:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | mcp-bridge --config bible.json
```

This should return a JSON response from your MCP Bible server.

### Troubleshooting

- **Bridge not connecting**: Verify your MCP Bible server is running and accessible at the configured URL
- **Claude Desktop not finding tools**: Check that the bridge configuration is correct and Claude Desktop has been restarted

Once configured, Claude Desktop will have access to all Bible passage retrieval tools provided by your MCP server!

## Semantic Versioning & Releases

The project uses [semantic versioning](https://semver.org/) for stable releases. Version tags follow the format `vMAJOR.MINOR.PATCH` (e.g., `v1.0.0`).

### Release Process

1. **Create a Git tag** for the release:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions automatically**:
   - Builds and pushes Docker images with version tags
   - Creates multiple tags: `v1.0.0`, `v1.0`, `v1`, `latest`

3. **Use versioned images** in production:
   ```bash
   # Instead of :main, use specific version
   docker-compose -f docker-compose.prod.v1.0.0.yml up -d
   ```

### Available Version Tags

When you create a semantic version tag like `v1.2.3`, the following Docker image tags are created:
- `ghcr.io/geosp/mcp-bible:v1.2.3` (full version)
- `ghcr.io/geosp/mcp-bible:v1.2` (major.minor)
- `ghcr.io/geosp/mcp-bible:v1` (major only)
- `ghcr.io/geosp/mcp-bible:latest` (latest release)

### Creating Versioned Compose Files

To create a versioned compose file for any release:

```bash
# Replace VERSION with your desired version (e.g., v1.0.0)
VERSION=v1.0.0

# Copy the template
cp docker-compose.prod.yml docker-compose.prod.${VERSION}.yml

# Edit the image tag (change :main to :VERSION)
# You can do this manually or use sed:
sed -i "s|ghcr.io/geosp/mcp-bible:main|ghcr.io/geosp/mcp-bible:${VERSION}|g" docker-compose.prod.${VERSION}.yml
```

This creates `docker-compose.prod.v1.0.0.yml` that uses the stable `v1.0.0` image instead of the `main` branch.

### Branch vs Release Strategy

- **Branch-based** (`:main`): Latest development version, updated on every push
- **Release-based** (`:v1.0.0`): Stable, immutable versions for production

Use branch-based for development/testing, release-based for production stability.