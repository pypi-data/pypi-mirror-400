"""
Token Manager - handles service token lifecycle
"""
import time
import base64
import json
import requests
from typing import Optional, Dict, Any
from ..exceptions import HxAuthError


class TokenManager:
    """
    Manages service token acquisition and refresh.
    Tokens are cached in memory and auto-refreshed before expiry.
    
    Also extracts org_id, workspace_id, environment_id from token claims.
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._token: Optional[str] = None
        self._exp: int = 0
        self._claims: Dict[str, Any] = {}
    
    def _decode_jwt(self, jwt: str) -> Dict[str, Any]:
        """Decode JWT payload and return claims"""
        try:
            payload = jwt.split(".")[1]
            padded = payload + "=" * (-len(payload) % 4)
            decoded = base64.urlsafe_b64decode(padded)
            return json.loads(decoded)
        except Exception as e:
            raise HxAuthError(f"Failed to decode token: {e}")
    
    def get_token(self) -> str:
        """
        Get a valid service token.
        Refreshes automatically if token is missing or expires within 60s.
        """
        now = int(time.time())
        
        if not self._token or now >= self._exp - 60:
            self._refresh()
        
        return self._token
    
    @property
    def org_id(self) -> str:
        """Get org_id from token claims"""
        if not self._claims:
            self.get_token()  # Ensure token is fetched
        return self._claims.get("org_id", "")
    
    @property
    def workspace_id(self) -> str:
        """Get workspace_id from token claims"""
        if not self._claims:
            self.get_token()
        return self._claims.get("workspace_id", "")
    
    @property
    def environment_id(self) -> str:
        """Get environment_id from token claims"""
        if not self._claims:
            self.get_token()
        return self._claims.get("environment_id", "")
    
    def _refresh(self) -> None:
        """Fetch a new service token from control plane"""
        try:
            resp = requests.post(
                f"{self._base_url}/control/v1/identity/service-tokens",
                headers={"X-API-Key": self._api_key},
                timeout=self._timeout
            )
            
            if resp.status_code == 401:
                raise HxAuthError("Invalid API key")
            
            if resp.status_code not in (200, 201):
                raise HxAuthError(f"Token request failed: {resp.status_code} {resp.text}")
            
            data = resp.json()
            token = data.get("access_token")
            
            if not token:
                raise HxAuthError("No access_token in response")
            
            self._token = token
            self._claims = self._decode_jwt(token)
            self._exp = self._claims.get("exp", 0)
            
        except requests.RequestException as e:
            raise HxAuthError(f"Token request failed: {e}")
    
    def invalidate(self) -> None:
        """Force token refresh on next request"""
        self._token = None
        self._exp = 0
        self._claims = {}
