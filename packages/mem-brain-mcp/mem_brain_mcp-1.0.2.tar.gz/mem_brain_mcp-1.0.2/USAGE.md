# How to Use Mem-Brain MCP Server with JWT Authentication

## Quick Start Guide

### 1. Start the Mem-Brain API Server

First, make sure your API server is running:

```bash
cd /Users/rakshithg/Documents/Meyra/mem-brain-api
uvicorn mem_brain_api.main:app --reload
```

The API should be running on `http://localhost:8000`

### 2. Start the MCP Server

In a new terminal:

```bash
cd /Users/rakshithg/Documents/Meyra/mem-brain-mcp

# Set environment variables
export API_BASE_URL=http://localhost:8000

# Run the MCP server
uv run python -m mem_brain_mcp.server
```

Or create a `.env` file:

```env
API_BASE_URL=http://localhost:8000
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8100
LOG_LEVEL=INFO
```

The MCP server will start on `http://localhost:8100/mcp`

### 3. Configure Your MCP Client

#### Option A: Use Login Tool (Recommended)

You can use the built-in `login` tool in your MCP client:

1. Connect to the MCP server
2. Call the `login` tool with your credentials:
   ```
   login(email="test@example.com", password="TestPassword123")
   ```
3. The tool will return your JWT token
4. Configure your client to use this token in subsequent requests

#### Option B: Configure JWT Token Directly

If you already have a JWT token (from login or signup), configure your MCP client:

**For Cursor IDE** (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mem-brain": {
      "url": "http://localhost:8100/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
      }
    }
  }
}
```

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "mem-brain": {
      "url": "http://localhost:8100/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
      }
    }
  }
}
```

### 4. Get Your JWT Token

You can get a JWT token in several ways:

#### Method 1: Use the Signup Tool

```bash
# Via MCP client
signup(
  email="your@email.com",
  password="SecurePass123",
  full_name="Your Name",
  organization_name="My Organization"
)
```

#### Method 2: Use the Login Tool

```bash
# Via MCP client
login(email="test@example.com", password="TestPassword123")
```

#### Method 3: Use the API Directly

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

This returns:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Copy the `access_token` value and use it in your MCP client configuration.

### 5. Use Memory Tools

Once authenticated, you can use all memory tools:

- `add_memory` - Create a new memory
- `search_memories` - Search memories semantically
- `get_memories` - Get specific memories by ID
- `update_memory` - Update a memory
- `delete_memories` - Delete memories
- `get_stats` - Get memory system statistics
- `find_path` - Find paths between memories
- `get_neighborhood` - Get memory neighborhoods

## Example Workflow

1. **Start API**: `uvicorn mem_brain_api.main:app --reload`
2. **Start MCP Server**: `uv run python -m mem_brain_mcp.server`
3. **In your MCP client**, call:
   ```
   login(email="test@example.com", password="TestPassword123")
   ```
4. **Use memory tools**:
   ```
   add_memory(content="I love Python programming", tags=["coding", "python"])
   search_memories(query="programming", k=5)
   ```

## Troubleshooting

### "No authentication token provided"

Make sure you've:
1. Called `login` or `signup` to get a token
2. Configured your MCP client with the token in headers
3. Used the format: `Authorization: Bearer YOUR_TOKEN`

### "Invalid or expired token"

Your token has expired (default: 30 minutes). Call `login` again to get a new token.

### "Connection refused"

Make sure:
1. The API server is running on port 8000
2. The MCP server is running on port 8100
3. Both servers are accessible from your MCP client

## Security Notes

- **Never commit tokens** to version control
- **Use HTTPS in production**
- **Rotate tokens regularly**
- **Each user should have their own token** for proper isolation

