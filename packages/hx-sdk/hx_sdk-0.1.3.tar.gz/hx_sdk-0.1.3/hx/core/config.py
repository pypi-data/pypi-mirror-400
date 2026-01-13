"""
SDK Configuration
"""
import os
from dataclasses import dataclass, field
from typing import Optional
from ..exceptions import HxConfigError


@dataclass
class HxConfig:
    """
    SDK configuration container.
    
    Only api_key is required - org/workspace/env are extracted from the 
    service token after authentication.
    """
    api_key: str
    base_url: str = "https://api.hexelstudio.com"
    timeout: int = 30
    # These are populated from JWT claims after token fetch
    org_id: str = field(default="")
    workspace_id: str = field(default="")
    environment_id: str = field(default="")
    
    @classmethod
    def from_env(
        cls,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30
    ) -> "HxConfig":
        """
        Create config from args or environment variables.
        
        Environment variables:
            HX_API_KEY: Required
            HX_BASE_URL: Optional (default: https://api.hexelstudio.com)
        
        Note: org_id, workspace_id, and environment_id are automatically
        extracted from the service token claims after authentication.
        """
        resolved_api_key = api_key or os.getenv("HX_API_KEY")
        resolved_base_url = base_url or os.getenv("HX_BASE_URL", "https://api.hexelstudio.com")
        
        if not resolved_api_key:
            raise HxConfigError(
                "Missing required configuration: HX_API_KEY. "
                "Set via constructor arg or environment variable."
            )
        
        return cls(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
            timeout=timeout
        )
