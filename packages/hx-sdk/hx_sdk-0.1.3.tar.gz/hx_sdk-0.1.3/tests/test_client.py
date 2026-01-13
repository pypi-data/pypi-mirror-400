"""
SDK Client Tests
"""
import pytest
from hx import Client, HxConfigError


def test_missing_config_raises_error():
    """Client should fail fast if required config is missing"""
    with pytest.raises(HxConfigError) as exc:
        Client()
    
    assert "HX_API_KEY" in str(exc.value)


def test_client_init_with_args():
    """Client should accept config via constructor"""
    client = Client(
        api_key="test_key",
        org_id="org_123",
        workspace_id="ws_456",
        environment_id="env_789",
        base_url="https://test.hexelstudio.com"
    )
    
    assert client.config.api_key == "test_key"
    assert client.config.org_id == "org_123"
    assert client.config.workspace_id == "ws_456"
    assert client.config.environment_id == "env_789"
    assert client.config.base_url == "https://test.hexelstudio.com"


def test_client_has_service_clients():
    """Client should expose service clients"""
    client = Client(
        api_key="test_key",
        org_id="org_123",
        workspace_id="ws_456",
        environment_id="env_789"
    )
    
    assert hasattr(client, "memory")
    assert hasattr(client, "knowledge")
