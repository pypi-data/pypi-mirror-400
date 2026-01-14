# Troubleshooting Mem-Brain MCP Server

## Common Issues

### Issue: `add_memory` fails with "content parameter not being passed correctly"

**Symptoms:**
- Error message suggests parameters aren't formatted properly
- Tool call fails even with valid content

**Solutions:**

1. **Ensure content is a string, not an object:**
   ```python
   # ✅ Correct
   add_memory(content="I love Python programming")
   
   # ❌ Wrong - don't pass as object
   add_memory({"content": "I love Python"})
   ```

2. **Use named parameters:**
   ```python
   # ✅ Correct
   add_memory(
       content="User prefers dark mode",
       tags=["preferences", "ui"],
       category="settings"
   )
   
   # ⚠️ May work but not recommended
   add_memory("User prefers dark mode", ["preferences"], "settings")
   ```

3. **Check parameter types:**
   - `content`: Must be a **string** (required)
   - `tags`: Must be a **list of strings** or `None` (optional)
   - `category`: Must be a **string** or `None` (optional)

4. **Example correct calls:**
   ```python
   # Minimal call
   add_memory(content="User loves TypeScript")
   
   # With tags
   add_memory(
       content="User prefers Python over JavaScript",
       tags=["coding", "preferences"]
   )
   
   # Full call
   add_memory(
       content="User works primarily with backend systems",
       tags=["coding", "backend"],
       category="interests"
   )
   ```

### Issue: Authentication errors

**Symptoms:**
- "Authentication failed" errors
- "No authentication token provided"

**Solutions:**

1. **Make sure you've logged in:**
   ```python
   login(email="your@email.com", password="yourpassword")
   ```

2. **Or configure token in MCP client:**
   ```json
   {
     "mcpServers": {
       "mem-brain": {
         "url": "http://localhost:8100/mcp",
         "headers": {
           "Authorization": "Bearer YOUR_JWT_TOKEN"
         }
       }
     }
   }
   ```

3. **Token expired?** Tokens expire after 30 minutes. Call `login` again.

### Issue: Search returns no results

**Possible causes:**
- No memories match your query
- Memories exist but don't match semantically
- Try broader queries

**Solutions:**
- Try different search terms
- Check if memories exist: `get_stats()`
- Use `get_memories()` to see what's stored

### Issue: Connection refused

**Check:**
1. API server is running: `curl http://localhost:8000/health`
2. MCP server is running: `curl http://localhost:8100/health`
3. Ports are correct in configuration

## Debug Mode

Enable debug logging to see what's happening:

```bash
export LOG_LEVEL=DEBUG
uv run python -m mem_brain_mcp
```

This will show:
- All tool calls with parameters
- API requests and responses
- Authentication details
- Error stack traces

## Testing Tools Manually

You can test the API directly to verify it's working:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123"}'

# Add memory (use token from login)
curl -X POST http://localhost:8000/api/v1/memories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"content": "Test memory", "tags": ["test"]}'
```

If this works but MCP doesn't, the issue is in the MCP tool definition or parameter passing.

