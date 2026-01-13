"""
HTTP Client - single request wrapper for all API calls
"""
import requests
from typing import Optional, Dict, Any
from .auth import TokenManager
from .config import HxConfig
from ..exceptions import HxAPIError


class HttpClient:
    """
    Internal HTTP client. All service clients use this.
    Handles auth headers, retries on 401, and error parsing.
    """
    
    def __init__(self, config: HxConfig, token_manager: TokenManager):
        self._config = config
        self._token_manager = token_manager
    
    @property
    def config(self) -> HxConfig:
        return self._config
    
    @property
    def org_id(self) -> str:
        """Get org_id from token claims"""
        return self._token_manager.org_id
    
    @property
    def workspace_id(self) -> str:
        """Get workspace_id from token claims"""
        return self._token_manager.workspace_id
    
    @property
    def environment_id(self) -> str:
        """Get environment_id from token claims"""
        return self._token_manager.environment_id
    
    def request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        _retry: bool = True
    ) -> Dict[str, Any]:
        """
        Make an authenticated API request.
        Auto-retries once on 401 after token refresh.
        """
        token = self._token_manager.get_token()
        
        request_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if headers:
            request_headers.update(headers)
        
        url = f"{self._config.base_url}{path}"
        
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                json=json_body,
                params=params,
                timeout=self._config.timeout
            )
        except requests.RequestException as e:
            raise HxAPIError(f"Request failed: {e}")
        
        # Retry once on 401
        if resp.status_code == 401 and _retry:
            self._token_manager.invalidate()
            return self.request(method, path, json_body, params, headers, _retry=False)
        
        # Handle errors
        if not resp.ok:
            self._raise_error(resp)
        
        # Handle 204 No Content
        if resp.status_code == 204:
            return {"success": True}
        
        # Handle empty response
        if not resp.content:
            return {"success": True}
        
        return resp.json()
    
    def _raise_error(self, resp: requests.Response) -> None:
        """Parse and raise appropriate error"""
        try:
            body = resp.json()
            detail = body.get("detail", resp.text)
        except Exception:
            body = {}
            detail = resp.text
        
        raise HxAPIError(
            f"API error: {resp.status_code} - {detail}",
            status_code=resp.status_code,
            response=body if body else {"detail": detail}
        )
    
    # ============== Path Builders ==============
    
    def build_path(self, plane: str, resource: str, include_tenant: bool = True) -> str:
        """
        Build API path for a given plane.
        
        Args:
            plane: API plane (runtime, data, control)
            resource: Resource path
            include_tenant: Whether to include org/workspace/env in path
        """
        if include_tenant:
            return (
                f"/{plane}/v1/organizations/{self.org_id}"
                f"/workspaces/{self.workspace_id}"
                f"/environments/{self.environment_id}"
                f"/{resource}"
            )
        return f"/{plane}/v1/{resource}"
