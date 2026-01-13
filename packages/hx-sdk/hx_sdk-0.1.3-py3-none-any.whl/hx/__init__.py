"""
HexelStudio Python SDK

Usage:
    from hx import Client
    
    client = Client()
    
    # Knowledge search
    results = client.knowledge.search("ks_support", "refund policy")
    
    # Memory operations
    client.memory.add("ms_support", messages=[...], user_id="user_123")
    memories = client.memory.search("ms_support", "preferences", user_id="user_123")
"""
from .client import Client
from .exceptions import (
    HxError,
    HxAuthError,
    HxAPIError,
    HxConfigError,
    HxValidationError,
    HxNotFoundError,
    HxRateLimitError,
)

__version__ = "0.1.2"

__all__ = [
    "Client",
    "HxError",
    "HxAuthError",
    "HxAPIError",
    "HxConfigError",
    "HxValidationError",
    "HxNotFoundError",
    "HxRateLimitError",
]
