"""
Async HTTP client for the Nowledge Mem REST API.
"""

import os
from typing import Any

import httpx

DEFAULT_API_URL = "http://127.0.0.1:14242"


class ApiClient:
    """Async HTTP client for communicating with the Nowledge Mem server."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.environ.get("NMEM_API_URL", DEFAULT_API_URL)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # =========================================================================
    # Health & Status
    # =========================================================================

    async def get_health(self) -> dict[str, Any]:
        """Get server health status."""
        client = await self._get_client()
        try:
            response = await client.get("/health")
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            return {"status": "offline", "error": "Cannot connect to server"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        client = await self._get_client()
        try:
            response = await client.get("/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Memories
    # =========================================================================

    async def list_memories(
        self,
        limit: int = 20,
        offset: int = 0,
        importance_min: float = 0.0,
    ) -> dict[str, Any]:
        """List memories with pagination."""
        client = await self._get_client()
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if importance_min > 0:
            params["importance_min"] = importance_min
        response = await client.get("/memories", params=params)
        response.raise_for_status()
        return response.json()

    async def search_memories(
        self,
        query: str,
        limit: int = 20,
        labels: list[str] | None = None,
        importance_min: float = 0.0,
        mode: str = "deep",
    ) -> dict[str, Any]:
        """Search memories with filters."""
        client = await self._get_client()
        params: dict[str, Any] = {"q": query, "limit": limit, "mode": mode}
        if labels:
            params["labels"] = labels
        if importance_min > 0:
            params["importance_min"] = importance_min
        response = await client.get("/memories/search", params=params)
        response.raise_for_status()
        return response.json()

    async def get_memory(self, memory_id: str) -> dict[str, Any]:
        """Get a single memory by ID."""
        client = await self._get_client()
        response = await client.get(f"/memories/{memory_id}")
        response.raise_for_status()
        return response.json()

    async def create_memory(
        self,
        content: str,
        title: str | None = None,
        importance: float = 0.5,
        source: str = "tui",
    ) -> dict[str, Any]:
        """Create a new memory."""
        client = await self._get_client()
        payload = {"content": content, "importance": importance, "source": source}
        if title:
            payload["title"] = title
        response = await client.post("/memories", json=payload)
        response.raise_for_status()
        return response.json()

    async def delete_memory(self, memory_id: str) -> dict[str, Any]:
        """Delete a memory."""
        client = await self._get_client()
        response = await client.delete(f"/memories/{memory_id}")
        response.raise_for_status()
        return response.json()

    async def update_memory(
        self,
        memory_id: str,
        title: str | None = None,
        content: str | None = None,
        importance: float | None = None,
    ) -> dict[str, Any]:
        """Update a memory."""
        client = await self._get_client()
        payload: dict[str, Any] = {"memory_id": memory_id}
        if title is not None:
            payload["title"] = title
        if content is not None:
            payload["content"] = content
        if importance is not None:
            payload["importance"] = importance
        response = await client.patch(f"/memories/{memory_id}", json=payload)
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Threads
    # =========================================================================

    async def list_threads(self, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        """List threads with pagination."""
        client = await self._get_client()
        params = {"limit": limit, "offset": offset}
        response = await client.get("/threads", params=params)
        response.raise_for_status()
        return response.json()

    async def search_threads(self, query: str, limit: int = 20) -> dict[str, Any]:
        """Search threads."""
        client = await self._get_client()
        params = {"query": query, "limit": limit}
        response = await client.get("/threads/search", params=params)
        response.raise_for_status()
        return response.json()

    async def get_thread(self, thread_id: str) -> dict[str, Any]:
        """Get a thread with messages."""
        client = await self._get_client()
        response = await client.get(f"/threads/{thread_id}")
        response.raise_for_status()
        return response.json()

    async def delete_thread(
        self, thread_id: str, cascade: bool = False
    ) -> dict[str, Any]:
        """Delete a thread."""
        client = await self._get_client()
        params = {"cascade_delete_memories": cascade}
        response = await client.delete(f"/threads/{thread_id}", params=params)
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Graph
    # =========================================================================

    async def search_graph(
        self, query: str, limit: int = 30, depth: int = 2
    ) -> dict[str, Any]:
        """Search the knowledge graph."""
        client = await self._get_client()
        params = {"query": query, "limit": limit, "depth": depth}
        response = await client.get("/graph/search", params=params)
        response.raise_for_status()
        return response.json()

    async def get_graph_sample(
        self, limit: int = 100, depth: int = 1
    ) -> dict[str, Any]:
        """Get a sample of the graph for visualization."""
        client = await self._get_client()
        params = {"limit": limit, "depth": depth}
        response = await client.get("/graph/sample", params=params)
        response.raise_for_status()
        return response.json()

    async def get_graph_analysis(self) -> dict[str, Any]:
        """Get graph analysis including communities and centrality."""
        client = await self._get_client()
        response = await client.get("/graph/analysis")
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Labels
    # =========================================================================

    async def list_labels(self) -> list[dict[str, Any]]:
        """List all labels."""
        client = await self._get_client()
        response = await client.get("/labels")
        response.raise_for_status()
        data = response.json()
        return data.get("labels", [])
