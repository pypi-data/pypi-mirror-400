"""
Memory Client - Memory Store runtime operations
"""
from typing import Optional, Dict, Any, List
from ...core.base import BaseClient
from .types import Message


class MemoryClient(BaseClient):
    """
    Memory operations for HexelStudio Memory Stores.
    
    All operations require a store_id (memory store identifier).
    """
    
    PLANE = "runtime"
    
    def add(
        self,
        store_id: str,
        messages: List[Message],
        *,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add memories from conversation messages.
        
        Args:
            store_id: Memory store identifier
            messages: List of messages with 'role' and 'content' keys
            user_id: Optional user identifier for memory scoping
            agent_id: Optional agent identifier for memory scoping
            run_id: Optional run/session identifier
            metadata: Optional metadata to attach to memories
        
        Returns:
            Response with processed memory results
        """
        body: Dict[str, Any] = {"messages": messages}
        
        if user_id:
            body["user_id"] = user_id
        if agent_id:
            body["agent_id"] = agent_id
        if run_id:
            body["run_id"] = run_id
        if metadata:
            body["metadata"] = metadata
        
        return self._http.request(
            "POST",
            self._path(f"memory-stores/{store_id}/memories"),
            body
        )
    
    def search(
        self,
        store_id: str,
        query: str,
        *,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Search memories by semantic similarity.
        
        Args:
            store_id: Memory store identifier
            query: Search query text
            user_id: Filter by user
            agent_id: Filter by agent
            run_id: Filter by run/session
            filters: Additional metadata filters
            top_k: Number of results (1-100, default 10)
        
        Returns:
            Search results with scores
        """
        body: Dict[str, Any] = {"query": query, "top_k": top_k}
        
        if user_id:
            body["user_id"] = user_id
        if agent_id:
            body["agent_id"] = agent_id
        if run_id:
            body["run_id"] = run_id
        if filters:
            body["filters"] = filters
        
        return self._http.request(
            "POST",
            self._path(f"memory-stores/{store_id}/memories/search"),
            body
        )
    
    def get(self, store_id: str, memory_id: str) -> Dict[str, Any]:
        """Get a specific memory by ID."""
        return self._http.request(
            "GET",
            self._path(f"memory-stores/{store_id}/memories/{memory_id}")
        )
    
    def list(
        self,
        store_id: str,
        *,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all memories in a store, optionally filtered."""
        params = {}
        if user_id:
            params["user_id"] = user_id
        if agent_id:
            params["agent_id"] = agent_id
        if run_id:
            params["run_id"] = run_id
        
        return self._http.request(
            "GET",
            self._path(f"memory-stores/{store_id}/memories"),
            params=params if params else None
        )
    
    def update(
        self,
        store_id: str,
        memory_id: str,
        data: str,
        *,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update a memory's content."""
        body: Dict[str, Any] = {"data": data}
        if metadata:
            body["metadata"] = metadata
        
        return self._http.request(
            "PUT",
            self._path(f"memory-stores/{store_id}/memories/{memory_id}"),
            body
        )
    
    def delete(self, store_id: str, memory_id: str) -> Dict[str, Any]:
        """Delete a specific memory."""
        return self._http.request(
            "DELETE",
            self._path(f"memory-stores/{store_id}/memories/{memory_id}")
        )
    
    def delete_all(
        self,
        store_id: str,
        *,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete all memories matching the filter criteria."""
        body = {}
        if user_id:
            body["user_id"] = user_id
        if agent_id:
            body["agent_id"] = agent_id
        if run_id:
            body["run_id"] = run_id
        
        return self._http.request(
            "DELETE",
            self._path(f"memory-stores/{store_id}/memories"),
            body if body else None
        )
    
    def history(self, store_id: str, memory_id: str) -> Dict[str, Any]:
        """Get the change history for a memory."""
        return self._http.request(
            "GET",
            self._path(f"memory-stores/{store_id}/memories/{memory_id}/history")
        )
    
    def reset(self, store_id: str) -> Dict[str, Any]:
        """Reset all memories in a store. WARNING: Deletes ALL memories."""
        return self._http.request(
            "POST",
            self._path(f"memory-stores/{store_id}/reset")
        )
