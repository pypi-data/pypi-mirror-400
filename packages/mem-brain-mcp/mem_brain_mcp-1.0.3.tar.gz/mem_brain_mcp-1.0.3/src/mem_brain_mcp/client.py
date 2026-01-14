"""HTTP client for Mem-Brain API."""

import logging
from typing import List, Optional, Dict, Any
import httpx

from mem_brain_mcp.config import settings

logger = logging.getLogger(__name__)


class APIClient:
    """HTTP client for interacting with Mem-Brain API."""

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize API client.

        Args:
            api_url: Base URL for the API (defaults to settings.api_url)
            api_key: API key for authentication (defaults to settings.api_key)
        """
        self.api_url = api_url or settings.api_url
        self.api_key = api_key or settings.api_key
        self.base_url = f"{self.api_url}/api/v1"

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            # api_key parameter now holds JWT token - use Bearer authentication
            headers["Authorization"] = f"Bearer {self.api_key}"
            logger.debug(f"Using JWT token authentication: {self.api_key[:20]}...")
        else:
            logger.debug("No authentication token configured for this client instance")
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (without /api/v1 prefix)
            **kwargs: Additional arguments for httpx request

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else "No response body"
                logger.error(f"API request failed: {e.request.method} {e.request.url} - {e.response.status_code}: {error_detail}")
                raise

    async def add_memory(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a new memory.

        Args:
            content: Memory content
            tags: Optional list of tags
            category: Optional category

        Returns:
            Response with memory_id and memory data
        """
        data = {"content": content}
        if tags:
            data["tags"] = tags
        if category:
            data["category"] = category

        return await self._request("POST", "/memories", json=data)

    async def search_memories(
        self,
        query: str,
        k: int = 5
    ) -> Dict[str, Any]:
        """Search memories using semantic similarity.

        Args:
            query: Search query string
            k: Number of results to return (1-100)

        Returns:
            Search results
        """
        data = {"query": query, "k": k}
        return await self._request("POST", "/memories/search", json=data)

    async def get_memories(
        self,
        memory_ids: List[str]
    ) -> Dict[str, Any]:
        """Retrieve multiple memories by ID.

        Args:
            memory_ids: List of memory IDs to retrieve

        Returns:
            Response with memories
        """
        data = {"memory_ids": memory_ids}
        return await self._request("POST", "/memories/batch", json=data)

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update an existing memory.

        Args:
            memory_id: Memory ID to update
            content: New content (optional)
            tags: New tags (optional)

        Returns:
            Updated memory data
        """
        data = {}
        if content is not None:
            data["content"] = content
        if tags is not None:
            data["tags"] = tags

        return await self._request("PUT", f"/memories/{memory_id}", json=data)

    async def delete_memories(
        self,
        memory_id: Optional[str] = None,
        tags: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete memories by ID or filter.

        Args:
            memory_id: Specific memory ID to delete (takes precedence)
            tags: Comma-separated tags for filter-based deletion
            category: Category for filter-based deletion

        Returns:
            Deletion response
        """
        params = {}
        if memory_id:
            params["memory_id"] = memory_id
        if tags:
            params["tags"] = tags
        if category:
            params["category"] = category

        return await self._request("DELETE", "/memories/bulk", params=params)

    async def unlink_memories(
        self,
        memory_id_1: str,
        memory_id_2: str
    ) -> Dict[str, Any]:
        """Remove link between two memories.

        Args:
            memory_id_1: First memory ID
            memory_id_2: Second memory ID

        Returns:
            Unlink response
        """
        data = {
            "memory_id_1": memory_id_1,
            "memory_id_2": memory_id_2
        }
        return await self._request("POST", "/memories/unlink", json=data)

    async def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics.

        Returns:
            Statistics response
        """
        return await self._request("GET", "/stats")

    async def find_path(
        self,
        from_id: str,
        to_id: str
    ) -> Dict[str, Any]:
        """Find shortest path between two memories.

        Args:
            from_id: Source memory ID
            to_id: Target memory ID

        Returns:
            Path response
        """
        params = {"from_id": from_id, "to_id": to_id}
        return await self._request("GET", "/graph/path", params=params)

    async def get_neighborhood(
        self,
        memory_id: str,
        hops: int = 2
    ) -> Dict[str, Any]:
        """Get all memories within N hops of a given memory.

        Args:
            memory_id: Center memory ID
            hops: Number of hops (1-5)

        Returns:
            Neighborhood response
        """
        params = {"memory_id": memory_id, "hops": hops}
        return await self._request("GET", "/graph/neighborhood", params=params)

