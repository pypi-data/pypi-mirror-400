"""MCP Server for Mem-Brain API using FastMCP."""

import logging
from typing import Any, Dict, List, Optional, Union
import httpx
from fastmcp import FastMCP
from fastmcp.server.context import request_ctx
from fastmcp.exceptions import ToolError
from fastmcp.prompts.prompt import PromptMessage, TextContent
from starlette.requests import Request
from starlette.responses import JSONResponse

from mem_brain_mcp.client import APIClient
from mem_brain_mcp.config import settings

# The comprehensive agent instructions (embedded for MCP distribution)
AGENT_INSTRUCTIONS = """You are an intelligent assistant with a persistent, evolving memory graph.

## 🎯 CORE DIRECTIVE
**Synthesize**, don't just retrieve. Connect user's request to their past preferences, habits, and constraints.

## 🔍 MEMORY WORKFLOW

**1. SEARCH FIRST & SMART** — Before answering personal questions, call `search_memories`.
   - **Formulate specific, natural language queries**, NOT simple keywords.
     - ❌ `query="maga"` (Weak)
     - ✅ `query="Who is Maga and what is his relationship to me?"` (Strong - matches both memory content & link descriptions)
   - Check `related_memories` field — these are auto-expanded graph neighbors.
   - Synthesize: If "coffee" result links to "acid reflux", suggest cold brew.

**2. PATTERN RECOGNITION** — Don't just echo memories back.
   - ❌ "I see a memory that says you like navy"
   - ✅ "This matches the navy aesthetic you've been leaning into"

**3. PASSIVE STORAGE** — When user reveals preferences, store the **FACT** (not conversation).
   - User: "I think I wanna try that sushi spot" → Store: "User interested in new sushi restaurant"

**4. KEEP IT CURRENT** — If user contradicts a past memory, use `update_memory`.

---

## 🛠️ TOOLS

### Core Operations

| Tool | When to Use |
|------|-------------|
| `search_memories(query, k=5)` | Before answering ANY personal question |
| `get_memories(memory_ids)` | Need full details for specific IDs |
| `add_memory(content, tags=[], category="")` | User reveals preference/goal/fact |
| `update_memory(memory_id, content=..., tags=...)` | Information evolves or changes |
| `delete_memories(memory_id)` | Memory is wrong or user requests deletion |
| `unlink_memories(id1, id2)` | Connection no longer relevant |
| `get_stats()` | User asks "how much do you remember?" |

### Graph Intelligence (Advanced)

| Tool | Purpose | Example |
|------|---------|---------|
| `find_path(from_id, to_id)` | Explain connections | "How is coffee related to health?" → Shows: Coffee→Caffeine→Health |
| `get_neighborhood(memory_id, hops=2)` | Deep context | Get 2-hop radius around a memory |

---

## 📝 STORAGE GUIDELINES

**Write FACTS, not conversation:**
- ✅ "User prefers dark mode interfaces"
- ❌ "You said you like dark mode"

**Tagging patterns:**
- Domain: `health`, `work`, `finance`, `tech`, `food`, `travel`
- Type: `preference`, `constraint`, `goal`, `fact`, `event`
- Priority: `important`, `routine`, `temporary`

**Avoiding duplicates:**
1. If you already searched → check if memory exists before adding
2. If similar memory exists → `update_memory` instead
3. If you haven't searched → just add it, evolution handles linking

---

## 🔄 CHANGING PREFERENCES

| Signal | Action |
|--------|--------|
| "I'm trying X", "exploring Y" | ADD new memory (temporary exploration) |
| "I no longer like X", "I switched to Y" | UPDATE existing memory (permanent change) |
| Contradictory with equal weight | ADD with temporal context ("as of 2025") |

---

## ⚡ ARCHITECTURE (Brief)

- **Graph Structure**: Memories = nodes, links = edges
- **Search**: Semantic similarity (70%) + importance/connections (30%)
- **Auto-linking**: System creates links for narrative/causal connections
- **User isolation**: Separate database per user

---

## ✅ BEST PRACTICES

| DO | DON'T |
|----|-------|
| Search before answering personal Q's | Guess without searching |
| Check `related_memories` field | Ignore graph connections |
| Store explicit facts | Store vague conversation |
| Update when info changes | Create duplicates |
| Synthesize across memories | Just list facts |

**Remember:** You're not a database. Connect the dots to provide thoughtful, personalized responses."""


def _get_request_token() -> Optional[str]:
    """Extract JWT token from request headers.
    
    Returns:
        JWT token string if found, None otherwise
    """
    try:
        ctx = request_ctx.get()
        if hasattr(ctx, 'request') and hasattr(ctx.request, 'headers'):
            headers = ctx.request.headers
            # Try Authorization Bearer token (primary method)
            auth_header = headers.get('authorization', '') or headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                return auth_header[7:]
            # Fallback to X-API-Key header (for backward compatibility)
            api_key = headers.get('x-api-key') or headers.get('X-API-Key')
            if api_key:
                return api_key
    except Exception as e:
        logger.debug(f"Could not extract token from request: {e}")
    return None


logger = logging.getLogger(__name__)


async def _get_api_client() -> APIClient:
    """Get API client with per-request JWT token."""
    token = _get_request_token()
    if token:
        return APIClient(api_key=token)  # api_key parameter now holds JWT token
    # Fallback to config API key (for single-user scenarios)
    if settings.api_key:
        logger.debug("Using config API key as fallback")
        return api_client  # Global instance
    # No token available
    raise ToolError("No authentication token provided. Please login using the login tool or configure your JWT token in your MCP client headers.")


# Initialize FastMCP server
mcp = FastMCP("Mem-Brain MCP")

# Initialize API client
api_client = APIClient()


async def _get_dynamic_context() -> str:
    """Fetch dynamic context (core identity + recent memories) from API."""
    try:
        # Get core identity
        client = await _get_api_client()
        identity_response = await client._request("POST", "/memories/search", json={
            "query": "user name location job identity", "k": 10
        })

        identity_memories = []
        for mem in identity_response.get("results", []):
            tags = mem.get('tags', [])
            if any(tag in tags for tag in {'user_info', 'name', 'location', 'job', 'core_identity', 'identity', 'personal'}):
                identity_memories.append(mem)

        identity_section = ""
        if identity_memories:
            identity_section = "## 🧬 Core Identity\n"
            for memory in identity_memories[:3]:
                identity_section += f"- {memory['content']}\n"

        # Get recent context
        recent_response = await client._request("POST", "/memories/search", json={
            "query": "recent context", "k": 3
        })

        recent_section = ""
        if recent_response.get("results"):
            recent_section = "## 🕐 Recent Context\n"
            for memory in recent_response.get("results", [])[:3]:
                content = memory['content']
                truncated = content[:100] + '...' if len(content) > 100 else content
                recent_section += f"- {truncated}\n"

        return f"""### 🧠 YOUR BRAIN (Current Working Context)
{identity_section if identity_section else "*No core identity established yet*"}
{recent_section if recent_section else "*No recent context*"}

---

"""
    except Exception as e:
        logger.warning(f"Could not fetch dynamic context: {e}")
        return """### 🧠 YOUR BRAIN (Current Working Context)
*Context loading failed - API may be unavailable*

---

"""


# ============================================================================
# RESOURCES (Documentation that LLMs can read)
# ============================================================================

@mcp.resource("mem-brain://docs/workflow-guide")
def workflow_guide() -> str:
    """Complete guide to the memory workflow: search strategies, pattern recognition, storage guidelines, and best practices."""
    return """# A-Mem Workflow Guide

## 🎯 CORE DIRECTIVE
**Synthesize**, don't just retrieve. Connect user's request to their past preferences, habits, and constraints.

## 🔍 MEMORY WORKFLOW

**1. SEARCH FIRST & SMART** — Before answering personal questions, call `search_memories`.
   - **Formulate specific, natural language queries**, NOT simple keywords.
     - ❌ `query="maga"` (Weak)
     - ✅ `query="Who is Maga and what is his relationship to me?"` (Strong - matches both memory content & link descriptions)
   - Check `related_memories` field — these are auto-expanded graph neighbors.
   - Synthesize: If "coffee" result links to "acid reflux", suggest cold brew.

**2. PATTERN RECOGNITION** — Don't just echo memories back.
   - ❌ "I see a memory that says you like navy"
   - ✅ "This matches the navy aesthetic you've been leaning into"

**3. PASSIVE STORAGE** — When user reveals preferences, store the **FACT** (not conversation).
   - User: "I think I wanna try that sushi spot" → Store: "User interested in new sushi restaurant"

**4. KEEP IT CURRENT** — If user contradicts a past memory, use `update_memory`.

## ✅ BEST PRACTICES

| DO | DON'T |
|----|-------|
| Search before answering personal Q's | Guess without searching |
| Check `related_memories` field | Ignore graph connections |
| Store explicit facts | Store vague conversation |
| Update when info changes | Create duplicates |
| Synthesize across memories | Just list facts |

**Remember:** You're not a database. Connect the dots to provide thoughtful, personalized responses.
"""


@mcp.resource("mem-brain://docs/tool-reference")
def tool_reference() -> str:
    """Detailed reference for when and how to use each memory tool effectively."""
    return """# Tool Usage Reference

## Core Operations

### `search_memories(query, k=5)`
**When to Use**: Before answering ANY personal question
**Critical**: Formulate specific, natural language queries, NOT simple keywords
- ✅ Good: "Who is Maga and what is their relationship to me?"
- ❌ Bad: "maga"

### `get_memories(memory_ids)`
**When to Use**: Need full details for specific IDs identified from search results

### `add_memory(content, tags=[], category="")`
**When to Use**: User reveals preference/goal/fact
**Storage Rule**: Store FACTS, not conversation
- ✅ "User prefers dark mode interfaces"
- ❌ "You said you like dark mode"

### `update_memory(memory_id, content=..., tags=...)`
**When to Use**: Information evolves or changes, user contradicts past memory

### `delete_memories(memory_id)`
**When to Use**: Memory is wrong or user explicitly requests deletion

### `unlink_memories(id1, id2)`
**When to Use**: Connection no longer relevant or accurate

### `get_stats()`
**When to Use**: User asks "how much do you remember?" or wants overview

## Graph Intelligence

### `find_path(from_id, to_id)`
**Purpose**: Explain connections between memories
**Example**: "How is coffee related to health?" → Shows path: Coffee→Caffeine→Health

### `get_neighborhood(memory_id, hops=2)`
**Purpose**: Get deep context around a memory
**Use Case**: Understanding relationships around important memories
"""


@mcp.resource("mem-brain://docs/storage-guidelines")
def storage_guidelines() -> str:
    """Best practices for storing facts, tagging patterns, and avoiding duplicates."""
    return """# Storage Guidelines

## Write FACTS, not conversation

- ✅ "User prefers dark mode interfaces"
- ❌ "You said you like dark mode"

## Tagging Patterns

**Domains**: `health`, `work`, `finance`, `tech`, `food`, `travel`
**Types**: `preference`, `constraint`, `goal`, `fact`, `event`
**Priority**: `important`, `routine`, `temporary`

## Avoiding Duplicates

1. If you already searched → check if memory exists before adding
2. If similar memory exists → `update_memory` instead
3. If you haven't searched → just add it, evolution handles linking

## Changing Preferences

| Signal | Action |
|--------|--------|
| "I'm trying X", "exploring Y" | ADD new memory (temporary exploration) |
| "I no longer like X", "I switched to Y" | UPDATE existing memory (permanent change) |
| Contradictory with equal weight | ADD with temporal context ("as of 2025") |

## Architecture

- **Graph Structure**: Memories = nodes, links = edges
- **Search**: Semantic similarity (70%) + importance/connections (30%)
- **Auto-linking**: System creates links for narrative/causal connections
- **User isolation**: Separate database per user
"""


# ============================================================================
# PROMPTS (Bootstrap Intelligence)
# ============================================================================

@mcp.prompt
async def setup_personal_memory() -> PromptMessage:
    """Initializes the assistant with the user's identity, recent context, and memory management rules. Run this once at the start of a session."""
    context_section = await _get_dynamic_context()
    
    full_instructions = f"""{context_section}{AGENT_INSTRUCTIONS}

**Note**: For detailed tool usage, see resource: `mem-brain://docs/tool-reference`
For storage guidelines, see resource: `mem-brain://docs/storage-guidelines`
"""
    
    return PromptMessage(
        role="system",
        content=TextContent(type="text", text=full_instructions)
    )


@mcp.prompt
async def refresh_context() -> PromptMessage:
    """Refreshes the assistant's context with updated core identity and recent memories. Use when context feels stale."""
    context_section = await _get_dynamic_context()
    
    return PromptMessage(
        role="system",
        content=TextContent(
            type="text",
            text=f"""{context_section}

**Context refreshed.** Continue using memory tools as before.
"""
        )
    )


# ============================================================================
# TOOLS (Operations)
# ============================================================================

@mcp.tool()
async def get_agent_instructions(include_dynamic_context: bool = True) -> str:
    """Get comprehensive system prompt and best practices for using the memory system effectively. This contains the intelligence for smart memory management, search strategies, and agent workflows."""
    if include_dynamic_context:
        context_section = await _get_dynamic_context()
    else:
        context_section = ""
    
    return context_section + AGENT_INSTRUCTIONS


@mcp.tool()
async def add_memory(
    content: str,
    tags: Optional[List[str]] = None,
    category: Optional[str] = None
) -> str:
    """Create a new memory with content, optional tags, and category. Use this when user reveals preferences, goals, or facts. Store FACTS, not conversation. Examples: 'User prefers dark mode' vs 'You said you like dark mode'. See mem-brain://docs/storage-guidelines for tagging patterns. DO NOT store conversation snippets - only store factual information.
    
    IMPORTANT: Before creating a new memory, you MUST first search existing memories using search_memories() to check if a similar memory already exists. This prevents duplicates and helps maintain memory quality. Only create a new memory if no similar memory is found.
    
    Parameters:
        content (str, REQUIRED): The memory content to store. Must be a non-empty string. 
            - Cannot be None, empty string, or whitespace-only
            - Example: "User prefers Python over JavaScript"
            - Example: "User prefers dark mode interfaces"
        
        tags (list[str], optional): List of tags to categorize the memory. 
            - Can be None (default) or a list of strings
            - Example: ["coding", "preferences"]
            - Example: ["personal", "pets", "animals"]
            - If you pass a single string, it will be converted to a list
        
        category (str, optional): Category name for the memory.
            - Can be None (default) or a non-empty string
            - Example: "interests"
            - Example: "preferences"
    
    Returns:
        str: A formatted string with the memory ID and details of the created memory.
    
    Common Errors and Solutions:
        - Error: "Tool call arguments for mcp were invalid"
          Solution: Ensure 'content' parameter is provided as a string. Example: add_memory(content="User prefers dark mode")
        
        - Error: "The 'content' parameter cannot be empty"
          Solution: Provide non-empty content. Example: add_memory(content="User loves Python programming")
        
        - Error: "tags must be a list"
          Solution: Pass tags as a list. Example: add_memory(content="...", tags=["coding"]) not tags="coding"
    
    Example workflow:
        1. search_memories(query="User prefers Python")  # Check for existing memories
        2. If no similar memory found, then: add_memory(content="User prefers Python over JavaScript", tags=["coding", "preferences"])
    
    Examples:
        # Basic usage (required parameter only)
        add_memory(content="User prefers dark mode")
        
        # With tags
        add_memory(content="User loves Python programming", tags=["coding", "preferences"])
        
        # With tags and category
        add_memory(
            content="User loves working with TypeScript",
            tags=["coding", "typescript"],
            category="interests"
        )
        
        # Tags as empty list (treated as None)
        add_memory(content="User prefers coffee", tags=[])
    """
    # Validate parameters with detailed error messages
    if content is None:
        raise ToolError(
            "The 'content' parameter is required but was not provided.\n"
            "Example: add_memory(content=\"User prefers dark mode\")\n"
            "Example: add_memory(content=\"User loves Python programming\", tags=[\"coding\"])"
        )
    
    if not isinstance(content, str):
        raise ToolError(
            f"The 'content' parameter must be a string, but got {type(content).__name__}.\n"
            f"Received: {repr(content)}\n"
            "Example: add_memory(content=\"User prefers dark mode\")"
        )
    
    content_str = str(content).strip()
    if not content_str:
        raise ToolError(
            "The 'content' parameter cannot be empty or whitespace-only.\n"
            "Please provide a non-empty string with actual content.\n"
            "Example: add_memory(content=\"User prefers dark mode\")\n"
            "Example: add_memory(content=\"User loves Python programming\")"
        )

    try:
        logger.info(f"add_memory called - content length: {len(content_str)}, tags: {tags}, category: {category}")
        logger.debug(f"add_memory full content: {content_str[:100]}...")
        
        # Normalize tags: convert empty list to None, ensure it's a list if provided
        normalized_tags = None
        if tags is not None:
            if isinstance(tags, list):
                # Validate list contents are strings
                if tags:
                    invalid_items = [item for item in tags if not isinstance(item, str)]
                    if invalid_items:
                        raise ToolError(
                            f"The 'tags' parameter must be a list of strings, but found non-string items: {invalid_items}\n"
                            f"Example: add_memory(content=\"...\", tags=[\"coding\", \"preferences\"])\n"
                            f"Example: add_memory(content=\"...\", tags=[\"personal\", \"pets\"])"
                        )
                normalized_tags = tags if tags else None  # Empty list becomes None
            elif isinstance(tags, str):
                # Handle case where tags might be passed as a single string
                normalized_tags = [tags]
            else:
                raise ToolError(
                    f"The 'tags' parameter must be a list of strings or None, but got {type(tags).__name__}.\n"
                    f"Received: {repr(tags)}\n"
                    "Example: add_memory(content=\"...\", tags=[\"coding\", \"preferences\"])\n"
                    "Example: add_memory(content=\"...\", tags=None)  # or omit tags parameter"
                )
        
        # Normalize category: convert empty string to None
        normalized_category = category.strip() if category and isinstance(category, str) and category.strip() else None

        client = await _get_api_client()
        logger.debug(f"Calling API client.add_memory with content='{content_str[:50]}...', tags={normalized_tags}, category={normalized_category}")
        
        result = await client.add_memory(content_str, normalized_tags, normalized_category)
        
        logger.info(f"Memory created successfully: {result.get('memory_id', 'unknown')}")
        memory = result.get('memory')
        if memory:
            return f"Memory created: {result.get('memory_id', 'unknown')}\n{_format_memory(memory)}"
        return f"Memory created: {result.get('memory_id', 'unknown')}"
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        elif e.response.status_code == 400:
            raise ToolError(f"Invalid request: {error_detail}")
        raise ToolError(f"Failed to create memory: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_memory: {e}", exc_info=True)
        raise ToolError(f"Error creating memory: {str(e)}")


@mcp.tool()
async def search_memories(query: str, k: int = 5) -> str:
    """Search memories using semantic similarity. CRITICAL: Formulate specific, natural language queries, NOT simple keywords. Examples: ✅ 'Who is Maga and what is their relationship to me?' vs ❌ 'maga'. Check related_memories field for graph connections and synthesize across results. See mem-brain://docs/workflow-guide for search strategies. DO NOT use vague keywords - always use full questions.
    
    Parameters:
        query (str, REQUIRED): Search query string. Use natural language questions, not keywords.
            - Example: "Who is Rakshith and what did he build?"
            - Example: "What are the user's preferences for programming languages?"
            - Example: "Tell me about memories related to the Dubai presentation"
        
        k (int, optional): Number of results to return. Default is 5.
            - Must be between 1 and 100
            - Example: 5 (default)
            - Example: 10
    
    Returns:
        str: Formatted search results with memory nodes and relationship edges.
    
    Common Errors and Solutions:
        - Error: "Query cannot be empty"
          Solution: Provide a non-empty search query. Example: search_memories(query="What is the user's name?")
        
        - Error: "k must be between 1 and 100"
          Solution: Provide k between 1 and 100. Example: search_memories(query="...", k=10)
    
    Examples:
        # Basic search
        search_memories(query="Who is Rakshith?")
        
        # Search with more results
        search_memories(query="What are the user's programming preferences?", k=10)
        
        # Complex query
        search_memories(query="Tell me about memories related to mem-brain and its features")
    """
    # Validate parameters with detailed error messages
    if query is None:
        raise ToolError(
            "The 'query' parameter is required but was not provided.\n"
            "Example: search_memories(query=\"Who is Rakshith?\")\n"
            "Example: search_memories(query=\"What are the user's preferences?\")"
        )
    
    if not isinstance(query, str):
        raise ToolError(
            f"The 'query' parameter must be a string, but got {type(query).__name__}.\n"
            f"Received: {repr(query)}\n"
            "Example: search_memories(query=\"Who is Rakshith?\")"
        )
    
    query_str = query.strip()
    if not query_str:
        raise ToolError(
            "The 'query' parameter cannot be empty or whitespace-only.\n"
            "Provide a natural language question or search query.\n"
            "Example: search_memories(query=\"Who is Rakshith?\")\n"
            "Example: search_memories(query=\"What are the user's preferences?\")"
        )
    
    if not isinstance(k, int):
        raise ToolError(
            f"The 'k' parameter must be an integer, but got {type(k).__name__}.\n"
            f"Received: {repr(k)}\n"
            "Example: search_memories(query=\"...\", k=10)"
        )
    
    if not (1 <= k <= 100):
        raise ToolError(
            f"The 'k' parameter must be between 1 and 100, but got {k}.\n"
            "Example: search_memories(query=\"...\", k=5)\n"
            "Example: search_memories(query=\"...\", k=10)"
        )

    try:
        logger.info(f"search_memories called - query length: {len(query_str)}, k: {k}")
        client = await _get_api_client()
        result = await client.search_memories(query_str, k)
        return f"Found {result.get('count', 0)} results:\n{_format_search_results(result.get('results', []))}"
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        raise ToolError(f"Failed to search memories: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_memories: {e}", exc_info=True)
        raise ToolError(f"Error searching memories: {str(e)}")


@mcp.tool()
async def get_memories(memory_ids: List[str]) -> str:
    """Retrieve one or more memories by ID. Use this when you need full details for specific memories identified from search results.
    
    Parameters:
        memory_ids (list[str], REQUIRED): List of memory IDs to retrieve. Must be a non-empty list.
            - Example: ["480c1f76-bcdf-4491-8781-24510db992e3"]
            - Example: ["480c1f76-...", "300d9716-...", "6fb6b23f-..."]
            - Get memory IDs from search_memories() results
    
    Returns:
        str: Formatted details of the retrieved memories.
    
    Common Errors and Solutions:
        - Error: "memory_ids cannot be empty"
          Solution: Provide a list with at least one memory ID. Example: get_memories(memory_ids=["480c1f76-..."])
        
        - Error: "Memory IDs cannot be empty"
          Solution: Ensure all IDs in the list are non-empty strings. Example: get_memories(memory_ids=["480c1f76-..."])
        
        - Error: "memory_ids must be a list"
          Solution: Pass memory_ids as a list. Example: get_memories(memory_ids=["..."]) not memory_ids="..."
    
    Examples:
        # Get single memory
        get_memories(memory_ids=["480c1f76-bcdf-4491-8781-24510db992e3"])
        
        # Get multiple memories
        get_memories(memory_ids=["480c1f76-...", "300d9716-...", "6fb6b23f-..."])
    """
    # Validate parameters with detailed error messages
    if memory_ids is None:
        raise ToolError(
            "The 'memory_ids' parameter is required but was not provided.\n"
            "Example: get_memories(memory_ids=[\"480c1f76-bcdf-4491-8781-24510db992e3\"])\n"
            "Example: get_memories(memory_ids=[\"480c1f76-...\", \"300d9716-...\"])"
        )
    
    if not isinstance(memory_ids, list):
        raise ToolError(
            f"The 'memory_ids' parameter must be a list of strings, but got {type(memory_ids).__name__}.\n"
            f"Received: {repr(memory_ids)}\n"
            "Example: get_memories(memory_ids=[\"480c1f76-...\"])"
        )
    
    if not memory_ids:
        raise ToolError(
            "The 'memory_ids' parameter cannot be an empty list.\n"
            "Provide at least one memory ID.\n"
            "Example: get_memories(memory_ids=[\"480c1f76-bcdf-4491-8781-24510db992e3\"])"
        )
    
    # Validate each memory ID in the list
    validated_ids = []
    for i, memory_id in enumerate(memory_ids):
        if memory_id is None:
            raise ToolError(
                f"Memory ID at index {i} is None. All memory IDs must be non-empty strings.\n"
                "Example: get_memories(memory_ids=[\"480c1f76-...\"])"
            )
        if not isinstance(memory_id, str):
            raise ToolError(
                f"Memory ID at index {i} must be a string, but got {type(memory_id).__name__}.\n"
                f"Received: {repr(memory_id)}\n"
                "Example: get_memories(memory_ids=[\"480c1f76-...\"])"
            )
        memory_id_str = memory_id.strip()
        if not memory_id_str:
            raise ToolError(
                f"Memory ID at index {i} cannot be empty or whitespace-only.\n"
                "Get memory IDs from search_memories() or get_memories() results.\n"
                "Example: get_memories(memory_ids=[\"480c1f76-bcdf-4491-8781-24510db992e3\"])"
            )
        validated_ids.append(memory_id_str)

    try:
        logger.info(f"get_memories called - count: {len(validated_ids)}")
        client = await _get_api_client()
        result = await client.get_memories(validated_ids)
        memories = result.get("memories", [])
        return f"Retrieved {len(memories)} memories:\n{_format_memories_list(memories)}"
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        elif e.response.status_code == 404:
            raise ToolError(f"One or more memories not found.\nVerify the memory IDs are correct by searching for them first.")
        raise ToolError(f"Failed to get memories: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_memories: {e}", exc_info=True)
        raise ToolError(f"Error getting memories: {str(e)}")


@mcp.tool()
async def update_memory(
    memory_id: str,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """Update an existing memory when information evolves or changes. Use this when user contradicts a past memory ('I no longer like X') or when details need updating.
    
    Parameters:
        memory_id (str, REQUIRED): The ID of the memory to update. Must be a non-empty string.
            - Example: "480c1f76-bcdf-4491-8781-24510db992e3"
            - Get memory IDs from search_memories() or get_memories() results
        
        content (str, optional): New content for the memory. 
            - Can be None (to keep existing content) or a non-empty string
            - If provided, must not be empty or whitespace-only
            - Example: "User no longer likes TypeScript, prefers Python"
        
        tags (list[str], optional): New tags for the memory.
            - Can be None (to keep existing tags) or a list of strings
            - Example: ["coding", "python"]
            - Example: ["preferences", "updated"]
    
    Returns:
        str: A formatted string with the updated memory details.
    
    Common Errors and Solutions:
        - Error: "Tool call arguments for mcp were invalid"
          Solution: Ensure 'memory_id' parameter is provided as a string. Example: update_memory(memory_id="...")
        
        - Error: "memory_id cannot be empty"
          Solution: Provide a valid memory ID from search results. Example: update_memory(memory_id="480c1f76-...")
        
        - Error: "At least one of 'content' or 'tags' must be provided"
          Solution: Provide content or tags to update. Example: update_memory(memory_id="...", content="New content")
    
    Examples:
        # Update content only
        update_memory(memory_id="480c1f76-...", content="User prefers Python over JavaScript")
        
        # Update tags only
        update_memory(memory_id="480c1f76-...", tags=["coding", "preferences"])
        
        # Update both content and tags
        update_memory(
            memory_id="480c1f76-...",
            content="User no longer likes TypeScript",
            tags=["coding", "python"]
        )
    """
    # Validate parameters with detailed error messages
    if memory_id is None:
        raise ToolError(
            "The 'memory_id' parameter is required but was not provided.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: update_memory(memory_id=\"480c1f76-bcdf-4491-8781-24510db992e3\", content=\"New content\")"
        )
    
    if not isinstance(memory_id, str):
        raise ToolError(
            f"The 'memory_id' parameter must be a string, but got {type(memory_id).__name__}.\n"
            f"Received: {repr(memory_id)}\n"
            "Example: update_memory(memory_id=\"480c1f76-...\", content=\"New content\")"
        )
    
    memory_id_str = memory_id.strip()
    if not memory_id_str:
        raise ToolError(
            "The 'memory_id' parameter cannot be empty or whitespace-only.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: update_memory(memory_id=\"480c1f76-bcdf-4491-8781-24510db992e3\", content=\"New content\")"
        )
    
    # Validate that at least one update parameter is provided
    if content is None and tags is None:
        raise ToolError(
            "At least one of 'content' or 'tags' must be provided to update the memory.\n"
            "Example: update_memory(memory_id=\"...\", content=\"New content\")\n"
            "Example: update_memory(memory_id=\"...\", tags=[\"new\", \"tags\"])"
        )
    
    # Validate content if provided
    if content is not None:
        if not isinstance(content, str):
            raise ToolError(
                f"The 'content' parameter must be a string or None, but got {type(content).__name__}.\n"
                f"Received: {repr(content)}\n"
                "Example: update_memory(memory_id=\"...\", content=\"New content\")"
            )
        content_str = str(content).strip()
        if not content_str:
            raise ToolError(
                "The 'content' parameter cannot be empty or whitespace-only.\n"
                "Provide a non-empty string or omit the parameter to keep existing content.\n"
                "Example: update_memory(memory_id=\"...\", content=\"New content\")"
            )
    else:
        content_str = None
    
    # Validate tags if provided
    normalized_tags = None
    if tags is not None:
        if isinstance(tags, list):
            # Validate list contents are strings
            if tags:
                invalid_items = [item for item in tags if not isinstance(item, str)]
                if invalid_items:
                    raise ToolError(
                        f"The 'tags' parameter must be a list of strings, but found non-string items: {invalid_items}\n"
                        "Example: update_memory(memory_id=\"...\", tags=[\"coding\", \"preferences\"])\n"
                        "Example: update_memory(memory_id=\"...\", tags=None)  # or omit tags parameter"
                    )
            normalized_tags = tags if tags else None  # Empty list becomes None
        elif isinstance(tags, str):
            # Handle case where tags might be passed as a single string
            normalized_tags = [tags]
        else:
            raise ToolError(
                f"The 'tags' parameter must be a list of strings or None, but got {type(tags).__name__}.\n"
                f"Received: {repr(tags)}\n"
                "Example: update_memory(memory_id=\"...\", tags=[\"coding\", \"preferences\"])\n"
                "Example: update_memory(memory_id=\"...\", tags=None)  # or omit tags parameter"
            )

    try:
        logger.info(f"update_memory called - memory_id: {memory_id_str}, content length: {len(content_str) if content_str else 0}, tags: {normalized_tags}")
        
        client = await _get_api_client()
        result = await client.update_memory(memory_id_str, content_str, normalized_tags)
        memory = result.get('memory')
        if memory:
            return f"Memory updated:\n{_format_memory(memory)}"
        return f"Memory {memory_id_str} updated"
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        elif e.response.status_code == 400:
            raise ToolError(f"Invalid request: {error_detail}\nExample: update_memory(memory_id=\"...\", content=\"New content\")")
        elif e.response.status_code == 404:
            raise ToolError(f"Memory not found: {memory_id_str}\nVerify the memory_id is correct by searching for it first.")
        raise ToolError(f"Failed to update memory: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_memory: {e}", exc_info=True)
        raise ToolError(f"Error updating memory: {str(e)}")


@mcp.tool()
async def delete_memories(
    memory_id: Optional[str] = None,
    tags: Optional[str] = None,
    category: Optional[str] = None
) -> str:
    """Delete memories by ID or by filter (tags/category). If memory_id is provided, it takes precedence over filters. Use for removing wrong memories or when user explicitly requests deletion.
    
    Parameters:
        memory_id (str, optional): Specific memory ID to delete. Takes precedence over filters.
            - Example: "480c1f76-bcdf-4491-8781-24510db992e3"
            - Get memory IDs from search_memories() or get_memories() results
        
        tags (str, optional): Comma-separated tags for filter-based deletion.
            - Example: "coding,preferences"
            - Example: "personal,pets"
            - Only used if memory_id is not provided
        
        category (str, optional): Category name for filter-based deletion.
            - Example: "interests"
            - Example: "preferences"
            - Only used if memory_id is not provided
    
    Returns:
        str: A message indicating how many memories were deleted and their IDs.
    
    Common Errors and Solutions:
        - Error: "At least one parameter must be provided"
          Solution: Provide memory_id, tags, or category. Example: delete_memories(memory_id="...")
        
        - Error: "memory_id cannot be empty"
          Solution: Provide a valid memory ID or omit the parameter. Example: delete_memories(memory_id="480c1f76-...")
    
    Examples:
        # Delete by memory ID
        delete_memories(memory_id="480c1f76-bcdf-4491-8781-24510db992e3")
        
        # Delete by tags
        delete_memories(tags="coding,preferences")
        
        # Delete by category
        delete_memories(category="interests")
    """
    # Validate that at least one parameter is provided
    if memory_id is None and tags is None and category is None:
        raise ToolError(
            "At least one parameter (memory_id, tags, or category) must be provided to delete memories.\n"
            "Example: delete_memories(memory_id=\"480c1f76-bcdf-4491-8781-24510db992e3\")\n"
            "Example: delete_memories(tags=\"coding,preferences\")\n"
            "Example: delete_memories(category=\"interests\")"
        )
    
    # Validate memory_id if provided
    if memory_id is not None:
        if not isinstance(memory_id, str):
            raise ToolError(
                f"The 'memory_id' parameter must be a string or None, but got {type(memory_id).__name__}.\n"
                f"Received: {repr(memory_id)}\n"
                "Example: delete_memories(memory_id=\"480c1f76-bcdf-4491-8781-24510db992e3\")"
            )
        memory_id_str = memory_id.strip()
        if not memory_id_str:
            raise ToolError(
                "The 'memory_id' parameter cannot be empty or whitespace-only.\n"
                "Get memory IDs from search_memories() or get_memories() results.\n"
                "Example: delete_memories(memory_id=\"480c1f76-bcdf-4491-8781-24510db992e3\")"
            )
    else:
        memory_id_str = None
    
    # Validate tags if provided
    if tags is not None:
        if not isinstance(tags, str):
            raise ToolError(
                f"The 'tags' parameter must be a string or None, but got {type(tags).__name__}.\n"
                f"Received: {repr(tags)}\n"
                "Example: delete_memories(tags=\"coding,preferences\")"
            )
        tags_str = tags.strip()
        if not tags_str:
            raise ToolError(
                "The 'tags' parameter cannot be empty or whitespace-only.\n"
                "Provide comma-separated tags or omit the parameter.\n"
                "Example: delete_memories(tags=\"coding,preferences\")"
            )
    else:
        tags_str = None
    
    # Validate category if provided
    if category is not None:
        if not isinstance(category, str):
            raise ToolError(
                f"The 'category' parameter must be a string or None, but got {type(category).__name__}.\n"
                f"Received: {repr(category)}\n"
                "Example: delete_memories(category=\"interests\")"
            )
        category_str = category.strip()
        if not category_str:
            raise ToolError(
                "The 'category' parameter cannot be empty or whitespace-only.\n"
                "Provide a category name or omit the parameter.\n"
                "Example: delete_memories(category=\"interests\")"
            )
    else:
        category_str = None
    
    try:
        logger.info(f"delete_memories called - memory_id: {memory_id_str}, tags: {tags_str}, category: {category_str}")
        client = await _get_api_client()
        result = await client.delete_memories(memory_id_str, tags_str, category_str)
        deleted_ids = result.get('memory_ids', [])[:10]
        return f"Deleted {result.get('deleted_count', 0)} memories. IDs: {', '.join(deleted_ids)}"
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        elif e.response.status_code == 404:
            raise ToolError(f"Memory not found: {memory_id_str}\nVerify the memory_id is correct by searching for it first.")
        raise ToolError(f"Failed to delete memories: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_memories: {e}", exc_info=True)
        raise ToolError(f"Error deleting memories: {str(e)}")


@mcp.tool()
async def unlink_memories(memory_id_1: str, memory_id_2: str) -> str:
    """Remove link between two memories when the connection is no longer relevant or accurate.
    
    Parameters:
        memory_id_1 (str, REQUIRED): First memory ID in the link to remove.
            - Example: "480c1f76-bcdf-4491-8781-24510db992e3"
            - Get memory IDs from search_memories() or get_memories() results
        
        memory_id_2 (str, REQUIRED): Second memory ID in the link to remove.
            - Example: "300d9716-a3a6-44d3-b0f4-b28002a65da8"
            - Get memory IDs from search_memories() or get_memories() results
    
    Returns:
        str: Confirmation message that the memories were unlinked.
    
    Common Errors and Solutions:
        - Error: "memory_id_1 cannot be empty"
          Solution: Provide a valid memory ID. Example: unlink_memories(memory_id_1="480c1f76-...", memory_id_2="300d9716-...")
        
        - Error: "memory_id_2 cannot be empty"
          Solution: Provide a valid memory ID. Example: unlink_memories(memory_id_1="480c1f76-...", memory_id_2="300d9716-...")
    
    Examples:
        # Unlink two memories
        unlink_memories(
            memory_id_1="480c1f76-bcdf-4491-8781-24510db992e3",
            memory_id_2="300d9716-a3a6-44d3-b0f4-b28002a65da8"
        )
    """
    # Validate parameters with detailed error messages
    if memory_id_1 is None:
        raise ToolError(
            "The 'memory_id_1' parameter is required but was not provided.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: unlink_memories(memory_id_1=\"480c1f76-...\", memory_id_2=\"300d9716-...\")"
        )
    
    if not isinstance(memory_id_1, str):
        raise ToolError(
            f"The 'memory_id_1' parameter must be a string, but got {type(memory_id_1).__name__}.\n"
            f"Received: {repr(memory_id_1)}\n"
            "Example: unlink_memories(memory_id_1=\"480c1f76-...\", memory_id_2=\"300d9716-...\")"
        )
    
    memory_id_1_str = memory_id_1.strip()
    if not memory_id_1_str:
        raise ToolError(
            "The 'memory_id_1' parameter cannot be empty or whitespace-only.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: unlink_memories(memory_id_1=\"480c1f76-bcdf-4491-8781-24510db992e3\", memory_id_2=\"300d9716-...\")"
        )
    
    if memory_id_2 is None:
        raise ToolError(
            "The 'memory_id_2' parameter is required but was not provided.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: unlink_memories(memory_id_1=\"480c1f76-...\", memory_id_2=\"300d9716-...\")"
        )
    
    if not isinstance(memory_id_2, str):
        raise ToolError(
            f"The 'memory_id_2' parameter must be a string, but got {type(memory_id_2).__name__}.\n"
            f"Received: {repr(memory_id_2)}\n"
            "Example: unlink_memories(memory_id_1=\"480c1f76-...\", memory_id_2=\"300d9716-...\")"
        )
    
    memory_id_2_str = memory_id_2.strip()
    if not memory_id_2_str:
        raise ToolError(
            "The 'memory_id_2' parameter cannot be empty or whitespace-only.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: unlink_memories(memory_id_1=\"480c1f76-...\", memory_id_2=\"300d9716-a3a6-44d3-b0f4-b28002a65da8\")"
        )
    
    # Ensure the IDs are different
    if memory_id_1_str == memory_id_2_str:
        raise ToolError(
            "memory_id_1 and memory_id_2 must be different.\n"
            "You cannot unlink a memory from itself.\n"
            "Example: unlink_memories(memory_id_1=\"480c1f76-...\", memory_id_2=\"300d9716-...\")"
        )

    try:
        logger.info(f"unlink_memories called - memory_id_1: {memory_id_1_str}, memory_id_2: {memory_id_2_str}")
        client = await _get_api_client()
        result = await client.unlink_memories(memory_id_1_str, memory_id_2_str)
        return result.get("message", "Memories unlinked")
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        elif e.response.status_code == 404:
            raise ToolError(f"One or both memories not found.\nVerify the memory IDs are correct by searching for them first.")
        raise ToolError(f"Failed to unlink memories: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in unlink_memories: {e}", exc_info=True)
        raise ToolError(f"Error unlinking memories: {str(e)}")


@mcp.tool()
async def get_stats() -> str:
    """Get memory system statistics including total memories, links, and top tags. Use this when user asks 'how much do you remember?' or wants an overview of their memory system.
    
    Returns:
        str: Formatted statistics including total memories, links, and top tags.
    
    Examples:
        # Get statistics
        get_stats()
    """
    try:
        logger.info("get_stats called")
        client = await _get_api_client()
        result = await client.get_stats()
        top_tags = ', '.join([f"{tag}({count})" for tag, count in result.get('top_tags', [])[:10]])
        return f"""Memory System Statistics:
Total Memories: {result.get('total_memories', 0)}
Total Links: {result.get('total_links', 0)}
Average Links per Memory: {result.get('avg_links_per_memory', 0):.2f}
Top Tags: {top_tags}"""
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        raise ToolError(f"Failed to get stats: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_stats: {e}", exc_info=True)
        raise ToolError(f"Error getting stats: {str(e)}")


@mcp.tool()
async def find_path(from_id: str, to_id: str) -> str:
    """Find shortest path between two memories in the memory graph. Use this to explain connections between seemingly unrelated memories.
    
    Parameters:
        from_id (str, REQUIRED): Source memory ID to start the path from.
            - Example: "480c1f76-bcdf-4491-8781-24510db992e3"
            - Get memory IDs from search_memories() or get_memories() results
        
        to_id (str, REQUIRED): Target memory ID to find path to.
            - Example: "300d9716-a3a6-44d3-b0f4-b28002a65da8"
            - Get memory IDs from search_memories() or get_memories() results
    
    Returns:
        str: The shortest path between the two memories, or a message if no path exists.
    
    Common Errors and Solutions:
        - Error: "from_id cannot be empty"
          Solution: Provide a valid memory ID. Example: find_path(from_id="480c1f76-...", to_id="300d9716-...")
        
        - Error: "to_id cannot be empty"
          Solution: Provide a valid memory ID. Example: find_path(from_id="480c1f76-...", to_id="300d9716-...")
    
    Examples:
        # Find path between two memories
        find_path(
            from_id="480c1f76-bcdf-4491-8781-24510db992e3",
            to_id="300d9716-a3a6-44d3-b0f4-b28002a65da8"
        )
    """
    # Validate parameters with detailed error messages
    if from_id is None:
        raise ToolError(
            "The 'from_id' parameter is required but was not provided.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: find_path(from_id=\"480c1f76-...\", to_id=\"300d9716-...\")"
        )
    
    if not isinstance(from_id, str):
        raise ToolError(
            f"The 'from_id' parameter must be a string, but got {type(from_id).__name__}.\n"
            f"Received: {repr(from_id)}\n"
            "Example: find_path(from_id=\"480c1f76-...\", to_id=\"300d9716-...\")"
        )
    
    from_id_str = from_id.strip()
    if not from_id_str:
        raise ToolError(
            "The 'from_id' parameter cannot be empty or whitespace-only.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: find_path(from_id=\"480c1f76-bcdf-4491-8781-24510db992e3\", to_id=\"300d9716-...\")"
        )
    
    if to_id is None:
        raise ToolError(
            "The 'to_id' parameter is required but was not provided.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: find_path(from_id=\"480c1f76-...\", to_id=\"300d9716-...\")"
        )
    
    if not isinstance(to_id, str):
        raise ToolError(
            f"The 'to_id' parameter must be a string, but got {type(to_id).__name__}.\n"
            f"Received: {repr(to_id)}\n"
            "Example: find_path(from_id=\"480c1f76-...\", to_id=\"300d9716-...\")"
        )
    
    to_id_str = to_id.strip()
    if not to_id_str:
        raise ToolError(
            "The 'to_id' parameter cannot be empty or whitespace-only.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: find_path(from_id=\"480c1f76-...\", to_id=\"300d9716-a3a6-44d3-b0f4-b28002a65da8\")"
        )

    try:
        logger.info(f"find_path called - from_id: {from_id_str}, to_id: {to_id_str}")
        client = await _get_api_client()
        result = await client.find_path(from_id_str, to_id_str)
        if result.get("status") == "success":
            path_text = f"Path found (length: {result.get('length', 0)}):\n"
            for mem in result.get("memories", []):
                path_text += f"  - {mem.get('id', 'unknown')}: {mem.get('content', '')[:100]}\n"
            return path_text
        return result.get("message", "No path found")
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        elif e.response.status_code == 404:
            raise ToolError(f"One or both memories not found.\nVerify the memory IDs are correct by searching for them first.")
        raise ToolError(f"Failed to find path: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in find_path: {e}", exc_info=True)
        raise ToolError(f"Error finding path: {str(e)}")


@mcp.tool()
async def get_neighborhood(memory_id: str, hops: int = 2) -> str:
    """Get all memories within N hops of a given memory. Use this for deep context and understanding relationships around important memories.
    
    Parameters:
        memory_id (str, REQUIRED): Center memory ID to get neighborhood around.
            - Example: "480c1f76-bcdf-4491-8781-24510db992e3"
            - Get memory IDs from search_memories() or get_memories() results
        
        hops (int, optional): Number of hops to traverse. Default is 2.
            - Must be between 1 and 5
            - 1 hop = direct connections only
            - 2 hops = direct connections + their connections
            - Example: 2 (default)
            - Example: 3
    
    Returns:
        str: Formatted list of memories in the neighborhood with their hop distances.
    
    Common Errors and Solutions:
        - Error: "memory_id cannot be empty"
          Solution: Provide a valid memory ID. Example: get_neighborhood(memory_id="480c1f76-...")
        
        - Error: "hops must be between 1 and 5"
          Solution: Provide hops between 1 and 5. Example: get_neighborhood(memory_id="...", hops=3)
    
    Examples:
        # Get neighborhood with default 2 hops
        get_neighborhood(memory_id="480c1f76-bcdf-4491-8781-24510db992e3")
        
        # Get neighborhood with 3 hops
        get_neighborhood(memory_id="480c1f76-bcdf-4491-8781-24510db992e3", hops=3)
        
        # Get direct connections only (1 hop)
        get_neighborhood(memory_id="480c1f76-bcdf-4491-8781-24510db992e3", hops=1)
    """
    # Validate parameters with detailed error messages
    if memory_id is None:
        raise ToolError(
            "The 'memory_id' parameter is required but was not provided.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: get_neighborhood(memory_id=\"480c1f76-bcdf-4491-8781-24510db992e3\")"
        )
    
    if not isinstance(memory_id, str):
        raise ToolError(
            f"The 'memory_id' parameter must be a string, but got {type(memory_id).__name__}.\n"
            f"Received: {repr(memory_id)}\n"
            "Example: get_neighborhood(memory_id=\"480c1f76-bcdf-4491-8781-24510db992e3\")"
        )
    
    memory_id_str = memory_id.strip()
    if not memory_id_str:
        raise ToolError(
            "The 'memory_id' parameter cannot be empty or whitespace-only.\n"
            "Get memory IDs from search_memories() or get_memories() results.\n"
            "Example: get_neighborhood(memory_id=\"480c1f76-bcdf-4491-8781-24510db992e3\")"
        )
    
    if not isinstance(hops, int):
        raise ToolError(
            f"The 'hops' parameter must be an integer, but got {type(hops).__name__}.\n"
            f"Received: {repr(hops)}\n"
            "Example: get_neighborhood(memory_id=\"...\", hops=2)"
        )
    
    if not (1 <= hops <= 5):
        raise ToolError(
            f"The 'hops' parameter must be between 1 and 5, but got {hops}.\n"
            "Example: get_neighborhood(memory_id=\"...\", hops=2)\n"
            "Example: get_neighborhood(memory_id=\"...\", hops=3)"
        )

    try:
        logger.info(f"get_neighborhood called - memory_id: {memory_id_str}, hops: {hops}")
        client = await _get_api_client()
        result = await client.get_neighborhood(memory_id_str, hops)
        neighborhood_text = f"Neighborhood (hops={result.get('hops', 2)}, total={result.get('total_in_neighborhood', 0)}):\n"
        for mem in result.get("neighborhood", []):
            hop_dist = mem.get("hop_distance", 0)
            is_center = " (center)" if mem.get("is_center") else ""
            neighborhood_text += f"  [{hop_dist}]{is_center} {mem.get('id', 'unknown')}: {mem.get('content', '')[:100]}\n"
        return neighborhood_text
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else "Unknown error"
        logger.error(f"API error: {e.response.status_code} - {error_detail}")
        if e.response.status_code == 401:
            raise ToolError("Authentication failed. Please login using the 'login' tool or configure your JWT token in the MCP client headers.")
        elif e.response.status_code == 404:
            raise ToolError(f"Memory not found: {memory_id_str}\nVerify the memory_id is correct by searching for it first.")
        raise ToolError(f"Failed to get neighborhood: HTTP {e.response.status_code} - {error_detail}")
    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_neighborhood: {e}", exc_info=True)
        raise ToolError(f"Error getting neighborhood: {str(e)}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_memory(memory: Optional[Dict[str, Any]]) -> str:
    """Format a single memory for display."""
    if not memory:
        return "Memory data not available"
    
    lines = [
        f"ID: {memory.get('id', 'unknown')}",
        f"Content: {memory.get('content', '')[:200]}",
        f"Tags: {', '.join(memory.get('tags', []))}",
        f"Context: {memory.get('context', 'N/A')}",
        f"Links: {len(memory.get('links', []))} connections"
    ]
    
    # Add evolution history if available
    evolution_history = memory.get('evolution_history', [])
    if evolution_history:
        lines.append(f"Evolution History: {len(evolution_history)} version(s)")
        # Show current version first
        current_content = memory.get('content', '')
        lines.append(f"  Current Version: {current_content}")
        lines.append("")
        # Show historical versions (oldest to newest)
        for i, entry in enumerate(evolution_history, 1):
            if entry.get('type') == 'content_update':
                old_content = entry.get('old_content', '')
                timestamp = entry.get('timestamp', 'unknown')
                lines.append(f"  Version {i} ({timestamp}): {old_content}")
            elif entry.get('type') == 'evolution':
                old_context = entry.get('old_context', 'N/A')
                new_context = entry.get('new_context', 'N/A')
                timestamp = entry.get('timestamp', 'unknown')
                lines.append(f"  Evolution {i} ({timestamp}): Context '{old_context}' → '{new_context}'")
    
    return "\n".join(lines)


def _format_memories_list(memories: List[Dict[str, Any]]) -> str:
    """Format a list of memories for display."""
    if not memories:
        return "No memories found"
    
    formatted = []
    for i, mem in enumerate(memories, 1):
        formatted.append(f"{i}. {_format_memory(mem)}")
    return "\n\n".join(formatted)


def _format_search_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found"
    
    formatted = []
    for i, result in enumerate(results, 1):
        if result.get("type") == "memory_node":
            formatted.append(f"{i}. Memory Node (score: {result.get('semantic_score', 0):.3f})")
            formatted.append(f"   {_format_memory(result)}")
            related = result.get("related_memories", [])
            if related:
                formatted.append(f"   Related: {len(related)} memories")
        elif result.get("type") == "relationship_edge":
            formatted.append(f"{i}. Relationship Edge (score: {result.get('score', 0):.3f})")
            source = result.get('source', {})
            target = result.get('target', {})
            
            # Show source node data
            formatted.append(f"   Source Node:")
            formatted.append(f"     ID: {source.get('id', 'unknown')}")
            formatted.append(f"     Content: {source.get('content', 'N/A')}")
            if source.get('context') and source.get('context') != 'General':
                formatted.append(f"     Context: {source.get('context', 'N/A')}")
            if source.get('tags'):
                formatted.append(f"     Tags: {', '.join(source.get('tags', []))}")
            if source.get('keywords'):
                formatted.append(f"     Keywords: {', '.join(source.get('keywords', []))}")
            
            # Show target node data
            formatted.append(f"   Target Node:")
            formatted.append(f"     ID: {target.get('id', 'unknown')}")
            formatted.append(f"     Content: {target.get('content', 'N/A')}")
            if target.get('context') and target.get('context') != 'General':
                formatted.append(f"     Context: {target.get('context', 'N/A')}")
            if target.get('tags'):
                formatted.append(f"     Tags: {', '.join(target.get('tags', []))}")
            if target.get('keywords'):
                formatted.append(f"     Keywords: {', '.join(target.get('keywords', []))}")
        formatted.append("")
    
    return "\n".join(formatted)


# Add health check endpoint for load balancers
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for load balancers."""
    return JSONResponse(
        content={"status": "healthy", "service": "mem-brain-mcp"},
        status_code=200
    )


def run_server():
    """Run the FastMCP server with HTTP transport."""
    logger.info(f"Starting Mem-Brain MCP Server on {settings.mcp_server_host}:{settings.mcp_server_port}")
    logger.info(f"API URL: {settings.api_url}")
    logger.info(f"API Key: {'***' if settings.api_key else 'Not set'}")
    
    # Configure CORS for browser-based and MCP clients
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins for MCP clients
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=[
                "mcp-protocol-version",
                "mcp-session-id",
                "Authorization",
                "Content-Type",
                "Accept",
            ],
            expose_headers=["mcp-session-id"],
        )
    ]
    
    # Use http_app with CORS middleware and run with uvicorn
    # Note: http_app() handles the /mcp path automatically
    app = mcp.http_app(middleware=middleware, path="/mcp")
    
    # Import uvicorn (should be available via FastMCP dependencies)
    try:
        import uvicorn
    except ImportError:
        # Fallback: use mcp.run if uvicorn not available
        logger.warning("uvicorn not available, using mcp.run() without CORS")
        mcp.run(
            transport="http",
            host=settings.mcp_server_host,
            port=settings.mcp_server_port,
            path="/mcp"
        )
        return
    
    uvicorn.run(
        app,
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
    )
