"""
Client - Main SDK entry point
"""
from typing import Optional
from .core import HxConfig, TokenManager, HttpClient
from .services.memory import MemoryClient
from .services.knowledge import KnowledgeClient


class Client:
    """
    HexelStudio Python SDK Client.
    
    Provides access to all HexelStudio services.
    
    Configuration via environment variables:
        HX_API_KEY: Required. Your HexelStudio API key.
        HX_BASE_URL: Optional. API base URL (default: https://api.hexelstudio.com)
    
    Note: org_id, workspace_id, and environment_id are automatically extracted
    from the service token claims - no need to configure them separately.
    
    Example:
        from hx import Client
        
        client = Client()
        
        # Search knowledge
        results = client.knowledge.search("ks_support", "refund policy")
        
        # Add memories
        client.memory.add(
            "ms_support",
            messages=[
                {"role": "user", "content": "I prefer email"},
                {"role": "assistant", "content": "Noted!"}
            ],
            user_id="user_123"
        )
    """
    
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize Client.
        
        Args:
            api_key: API key (or set HX_API_KEY env var)
            base_url: API base URL (or set HX_BASE_URL env var)
            timeout: Request timeout in seconds (default 30)
        
        Note: org_id, workspace_id, and environment_id are automatically
        extracted from the service token - no configuration needed.
        """
        # Build config from args/env
        self._config = HxConfig.from_env(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )
        
        # Initialize auth
        self._token_manager = TokenManager(
            self._config.base_url,
            self._config.api_key
        )
        
        # Initialize HTTP client
        self._http = HttpClient(self._config, self._token_manager)
        
        # Initialize service clients
        self._init_services()
    
    def _init_services(self) -> None:
        """Initialize all service clients"""
        self.memory = MemoryClient(self._http)
        self.knowledge = KnowledgeClient(self._http)
        # Future services:
        # self.agents = AgentClient(self._http)
        # self.datasources = DataSourceClient(self._http)
        # self.connectors = ConnectorClient(self._http)
    
    @property
    def config(self) -> HxConfig:
        """Access SDK configuration"""
        return self._config
    
    @property
    def org_id(self) -> str:
        """Get org_id from token claims"""
        return self._http.org_id
    
    @property
    def workspace_id(self) -> str:
        """Get workspace_id from token claims"""
        return self._http.workspace_id
    
    @property
    def environment_id(self) -> str:
        """Get environment_id from token claims"""
        return self._http.environment_id
