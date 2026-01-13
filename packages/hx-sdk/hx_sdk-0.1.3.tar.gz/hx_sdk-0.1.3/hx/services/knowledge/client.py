"""
Knowledge Client - Knowledge Store runtime operations
"""
from typing import Optional, Dict, Any
from ...core.base import BaseClient


class KnowledgeClient(BaseClient):
    """
    Knowledge operations for HexelStudio Knowledge Stores.
    
    SDK supports search operations only.
    Knowledge store creation and document management are control-plane operations.
    """
    
    PLANE = "runtime"
    
    def search(
        self,
        store_id: str,
        query: str,
        *,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search a knowledge store by semantic similarity.
        
        Args:
            store_id: Knowledge store identifier
            query: Search query text (1-10000 chars)
            top_k: Number of results to return (1-100, default 10)
            score_threshold: Minimum similarity score (0.0-1.0)
            metadata_filter: Filter results by metadata fields
        
        Returns:
            Search response with results, scores, and latency
        """
        body: Dict[str, Any] = {
            "query": query,
            "top_k": top_k
        }
        
        if score_threshold is not None:
            body["score_threshold"] = score_threshold
        if metadata_filter:
            body["metadata_filter"] = metadata_filter
        
        return self._http.request(
            "POST",
            self._path(f"knowledge-stores/{store_id}/search"),
            body
        )
