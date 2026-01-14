# Mem-Brain MCP Server

MCP (Model Context Protocol) server that exposes Mem-Brain API functionality as standardized tools for AI agents. Built with [FastMCP](https://gofastmcp.com) for production-ready HTTP/SSE transport.

## Features

- **Memory Management**: Create, read, update, and delete memories
- **Semantic Search**: Search memories using vector similarity
- **Graph Operations**: Find paths and neighborhoods in the memory graph
- **Statistics**: Get insights about your memory system
- **Link Management**: Link and unlink memories
- **HTTP/SSE Transport**: Run independently, accessible remotely
- **CLI Interface**: Packaged for easy global execution

## Installation

### From PyPI (Recommended)

Install from PyPI using `pip` or `uv`:

```bash
# Using pip
pip install mem-brain-mcp

# Using uv
uv pip install mem-brain-mcp
```

Then run globally:

```bash
mem-brain-mcp
```

### Instant Execution with uvx

You can run the MCP server instantly without manual installation using `uvx`:

```bash
# Run using uvx (uses default API URL)
uvx mem-brain-mcp

# Override API URL or set JWT token if needed
export API_BASE_URL=http://your-custom-api-url.com
export MEMBRAIN_API_KEY=your-jwt-token-here
uvx mem-brain-mcp
```

### From Source

1. Install using `uv` (recommended) or `pip`:

```bash
cd mem-brain-mcp
uv pip install .
```

2. Run globally:

```bash
mem-brain-mcp
```

## Configuration

The server reads configuration from environment variables or a `.env` file in the current working directory. Most settings have sensible defaults:

```env
# API Configuration (optional - defaults to production API)
API_BASE_URL=http://membrain-api-alb-1094729422.ap-south-1.elb.amazonaws.com
# NOTE: MEMBRAIN_API_KEY is actually a JWT access token (from login/signup)
# Per-user JWT tokens are typically configured in MCP clients via headers
MEMBRAIN_API_KEY=your_jwt_token_here  # Optional: fallback for single-user scenarios

# MCP Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8100

# Logging
LOG_LEVEL=INFO
```

**Note**: The `API_BASE_URL` defaults to the production Mem-Brain API endpoint, so you typically don't need to set it unless you're using a custom API instance.

## Per-User JWT Token Configuration

Each user must configure their own JWT access token in their MCP client for proper user isolation. The server extracts tokens from request headers. Get your JWT token by logging in or signing up to the Mem-Brain API.

### Cursor IDE (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "mem-brain": {
      "url": "http://localhost:8100/mcp",
      "headers": {
        "Authorization": "Bearer your-jwt-token"
      }
    }
  }
}
```

### Claude Desktop

#### Option 1: Native Remote (Pro/Team plans)
Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mem-brain": {
      "url": "http://your-deployed-url/mcp",
      "headers": {
        "Authorization": "Bearer your-jwt-token"
      }
    }
  }
}
```

#### Option 2: via CLI (Any plan)
```json
{
  "mcpServers": {
    "mem-brain": {
      "command": "uvx",
      "args": ["mem-brain-mcp"]
    }
  }
}
```

**Note**: After installing from PyPI, you can also use `mem-brain-mcp` directly. The API URL is set by default, but you can override it if needed:
```json
{
  "mcpServers": {
    "mem-brain": {
      "command": "mem-brain-mcp",
      "env": {
        "API_BASE_URL": "http://your-custom-api-url"
      }
    }
  }
}
```

## AWS ECS Deployment

The MCP server can be deployed to AWS ECS (Fargate) with an Application Load Balancer.

### Quick Start

1. **Set up security groups** (see [aws/security-groups.md](./aws/security-groups.md))
2. **Deploy using the script:**

```bash
cd mem-brain-mcp/aws
./deploy.sh ap-south-1 membrain-mcp membrain-cluster membrain-mcp
```

For detailed instructions, see [aws/DEPLOYMENT.md](./aws/DEPLOYMENT.md).

## Development

### Running Tests
```bash
pytest
```

### Build and Publish
```bash
# Build the wheel
python3 -m build

# Upload to PyPI
twine upload dist/*
```

## License

Same as Mem-Brain API project.
