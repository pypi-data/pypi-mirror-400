"""
Base Client - abstract base for all service clients
"""
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .http import HttpClient


class BaseClient(ABC):
    """
    Base class for all service clients.
    
    Provides common functionality and access to HTTP client.
    Extend this for each new service (memory, knowledge, agents, etc.)
    """
    
    # Override in subclass to set the API plane
    PLANE: str = "runtime"
    
    def __init__(self, http: "HttpClient"):
        self._http = http
    
    def _path(self, resource: str, include_tenant: bool = True) -> str:
        """Build path for this service's plane"""
        return self._http.build_path(self.PLANE, resource, include_tenant)
