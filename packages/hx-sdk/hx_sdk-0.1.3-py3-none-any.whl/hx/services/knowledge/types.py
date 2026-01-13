"""
Knowledge Service Types
"""
from typing import TypedDict, List, Dict, Any


class SearchResult(TypedDict, total=False):
    """Single search result"""
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class SearchResponse(TypedDict):
    """Knowledge search response"""
    results: List[SearchResult]
    count: int
    query: str
    knowledge_store_id: str
    latency_ms: int
