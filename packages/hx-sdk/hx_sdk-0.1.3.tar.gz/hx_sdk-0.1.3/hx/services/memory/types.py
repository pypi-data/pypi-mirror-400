"""
Memory Service Types
"""
from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime


class Message(TypedDict, total=False):
    """Chat message for memory extraction"""
    role: str  # Required: user, assistant, system
    content: str  # Required: message content


class MemoryEntry(TypedDict, total=False):
    """Memory entry returned from API"""
    id: str
    memory: str
    hash: Optional[str]
    user_id: Optional[str]
    agent_id: Optional[str]
    run_id: Optional[str]
    metadata: Dict[str, Any]
    created_at: Optional[str]
    updated_at: Optional[str]


class MemorySearchResult(TypedDict, total=False):
    """Memory search result with score"""
    id: str
    memory: str
    score: float
    user_id: Optional[str]
    agent_id: Optional[str]
    run_id: Optional[str]
    metadata: Dict[str, Any]
    created_at: Optional[str]


class MemoryAddResponse(TypedDict):
    """Response from adding memories"""
    results: List[Dict[str, Any]]
    message: str


class MemoryListResponse(TypedDict):
    """Response from listing memories"""
    results: List[MemoryEntry]
    count: int


class MemorySearchResponse(TypedDict):
    """Response from searching memories"""
    results: List[MemorySearchResult]
    count: int
    query: str
