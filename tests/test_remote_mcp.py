#!/usr/bin/env python3
"""
Tests for Remote MCP Server Integration
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import aiohttp
from aioresponses import aioresponses

# Add src to path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.remote_mcp_integration import (
    RemoteServerConfig,
    RemoteMCPClient,
    RemoteMCPManager,
    TransportType,
    AuthType,
    OAuthToken,
)


class TestRemoteServerConfig:
    """Test RemoteServerConfig dataclass"""

    def test_basic_config(self):
        """Test basic server configuration"""
        config = RemoteServerConfig(
            name="test-server",
            transport=TransportType.HTTP,
            url="https://api.example.com/mcp",
            auth_type=AuthType.API_KEY,
        )

        assert config.name == "test-server"
        assert config.transport == TransportType.HTTP
        assert config.url == "https://api.example.com/mcp"
        assert config.auth_type == AuthType.API_KEY
        assert config.timeout == 30000
        assert config.retry_attempts == 3
        assert config.tls_verify is True

    def test_config_with_headers(self):
        """Test configuration with custom headers"""
        headers = {"X-API-Key": "test-key", "X-Client-ID": "client-123"}

        config = RemoteServerConfig(
            name="test-server",
            transport=TransportType.SSE,
            url="https://api.example.com/sse",
            auth_type=AuthType.API_KEY,
            headers=headers,
        )

        assert config.headers == headers

    def test_oauth_config(self):
        """Test OAuth configuration"""
        oauth_config = {
            "clientId": "client-id",
            "clientSecret": "client-secret",
            "tokenEndpoint": "https://auth.example.com/token",
            "scope": "read write",
        }

        config = RemoteServerConfig(
            name="oauth-server",
            transport=TransportType.HTTP,
            url="https://api.example.com/mcp",
            auth_type=AuthType.OAUTH2,
            oauth_config=oauth_config,
        )

        assert config.oauth_config == oauth_config


class TestOAuthToken:
    """Test OAuthToken functionality"""

    def test_token_not_expired(self):
        """Test token expiry check when not expired"""
        future_time = datetime.now() + timedelta(hours=1)
        token = OAuthToken(access_token="test-token", token_type="Bearer", expires_at=future_time)

        assert token.is_expired is False
        assert token.needs_refresh is False

    def test_token_expired(self):
        """Test token expiry check when expired"""
        past_time = datetime.now() - timedelta(hours=1)
        token = OAuthToken(access_token="test-token", token_type="Bearer", expires_at=past_time)

        assert token.is_expired is True
        assert token.needs_refresh is True

    def test_token_needs_refresh(self):
        """Test token needs refresh within 5 minutes of expiry"""
        near_future = datetime.now() + timedelta(minutes=3)
        token = OAuthToken(access_token="test-token", token_type="Bearer", expires_at=near_future)

        assert token.is_expired is False
        assert token.needs_refresh is True


class TestRemoteMCPClient:
    """Test RemoteMCPClient functionality"""

    @pytest.fixture
    def client_config(self):
        """Create test client configuration"""
        return RemoteServerConfig(
            name="test-server",
            transport=TransportType.HTTP,
            url="https://api.example.com/mcp",
            auth_type=AuthType.API_KEY,
            headers={"X-API-Key": "test-key"},
        )

    @pytest.mark.asyncio
    async def test_client_initialization(self, client_config):
        """Test client initialization"""
        client = RemoteMCPClient(client_config)

        assert client.config == client_config
        assert client.session is None
        assert client.token is None

    @pytest.mark.asyncio
    async def test_client_connect_http(self, client_config):
        """Test HTTP client connection"""
        client = RemoteMCPClient(client_config)

        with aioresponses() as mocked:
            mocked.get("https://api.example.com/mcp/health", status=200)

            await client.connect()
            assert client.session is not None

            await client.disconnect()

    @pytest.mark.asyncio
    async def test_client_connect_sse(self):
        """Test SSE client connection"""
        config = RemoteServerConfig(
            name="sse-server",
            transport=TransportType.SSE,
            url="https://api.example.com/sse",
            auth_type=AuthType.BEARER,
            headers={"Authorization": "Bearer test-token"},
        )

        client = RemoteMCPClient(config)
        await client.connect()

        assert client.session is not None

        await client.disconnect()

    @pytest.mark.asyncio
    async def test_get_auth_headers_api_key(self, client_config):
        """Test getting API key authentication headers"""
        client = RemoteMCPClient(client_config)
        headers = await client._get_auth_headers()

        assert headers["X-API-Key"] == "test-key"

    @pytest.mark.asyncio
    async def test_get_auth_headers_bearer(self):
        """Test getting bearer token authentication headers"""
        config = RemoteServerConfig(
            name="bearer-server",
            transport=TransportType.HTTP,
            url="https://api.example.com/mcp",
            auth_type=AuthType.BEARER,
            headers={"Authorization": "Bearer test-bearer-token"},
        )

        client = RemoteMCPClient(config)
        headers = await client._get_auth_headers()

        assert headers["Authorization"] == "Bearer test-bearer-token"

    @pytest.mark.asyncio
    async def test_oauth_token_request(self):
        """Test OAuth token request"""
        oauth_config = {
            "clientId": "test-client",
            "clientSecret": "test-secret",
            "tokenEndpoint": "https://auth.example.com/token",
            "scope": "read write",
        }

        config = RemoteServerConfig(
            name="oauth-server",
            transport=TransportType.HTTP,
            url="https://api.example.com/mcp",
            auth_type=AuthType.OAUTH2,
            oauth_config=oauth_config,
        )

        client = RemoteMCPClient(config)

        with aioresponses() as mocked:
            mocked.post(
                "https://auth.example.com/token",
                payload={
                    "access_token": "new-access-token",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "refresh_token": "refresh-token",
                    "scope": "read write",
                },
            )

            token = await client._request_oauth_token()

            assert token.access_token == "new-access-token"
            assert token.refresh_token == "refresh-token"
            assert token.scope == "read write"
            assert not token.is_expired

    @pytest.mark.asyncio
    async def test_send_http_request(self, client_config):
        """Test sending HTTP request"""
        client = RemoteMCPClient(client_config)

        with aioresponses() as mocked:
            # Mock health check
            mocked.get("https://api.example.com/mcp/health", status=200)

            # Mock actual request
            mocked.post(
                "https://api.example.com/mcp",
                payload={"jsonrpc": "2.0", "id": "test-id", "result": {"data": "test-result"}},
            )

            await client.connect()

            result = await client.send_request("testMethod", {"param": "value"})

            assert result == {"data": "test-result"}

            await client.disconnect()

    @pytest.mark.asyncio
    async def test_request_retry_on_error(self, client_config):
        """Test request retry on server error"""
        client_config.retry_attempts = 3
        client = RemoteMCPClient(client_config)

        with aioresponses() as mocked:
            # Mock health check
            mocked.get("https://api.example.com/mcp/health", status=200)

            # Mock failures then success
            mocked.post("https://api.example.com/mcp", status=500)
            mocked.post("https://api.example.com/mcp", status=500)
            mocked.post(
                "https://api.example.com/mcp",
                payload={"jsonrpc": "2.0", "id": "test-id", "result": {"data": "success"}},
            )

            await client.connect()

            result = await client.send_request("testMethod")

            assert result == {"data": "success"}

            await client.disconnect()

    @pytest.mark.asyncio
    async def test_context_manager(self, client_config):
        """Test using client as context manager"""
        with aioresponses() as mocked:
            mocked.get("https://api.example.com/mcp/health", status=200)

            async with RemoteMCPClient(client_config) as client:
                assert client.session is not None

            # Session should be closed after context exit
            assert client.session.closed


class TestRemoteMCPManager:
    """Test RemoteMCPManager functionality"""

    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Create temporary config file"""
        config = {
            "remoteMcpServers": {
                "test-server": {
                    "transport": "http",
                    "url": "https://api.example.com/mcp",
                    "headers": {"X-API-Key": "${TEST_API_KEY}"},
                },
                "oauth-server": {
                    "transport": "sse",
                    "url": "https://oauth.example.com/sse",
                    "authentication": {
                        "type": "oauth2",
                        "clientId": "${OAUTH_CLIENT_ID}",
                        "clientSecret": "${OAUTH_CLIENT_SECRET}",
                        "tokenEndpoint": "https://auth.example.com/token",
                    },
                },
            }
        }

        config_file = tmp_path / "remote-servers.json"
        config_file.write_text(json.dumps(config))

        return str(config_file)

    def test_manager_initialization(self, temp_config_file):
        """Test manager initialization with config file"""
        # Set environment variables
        os.environ["TEST_API_KEY"] = "test-key-123"
        os.environ["OAUTH_CLIENT_ID"] = "client-123"
        os.environ["OAUTH_CLIENT_SECRET"] = "secret-456"

        manager = RemoteMCPManager(temp_config_file)

        assert "test-server" in manager.servers
        assert "oauth-server" in manager.servers

        # Check environment variable expansion
        test_server = manager.servers["test-server"]
        assert test_server.config.headers["X-API-Key"] == "test-key-123"

        # Clean up env vars
        del os.environ["TEST_API_KEY"]
        del os.environ["OAUTH_CLIENT_ID"]
        del os.environ["OAUTH_CLIENT_SECRET"]

    def test_add_server(self):
        """Test adding server to manager"""
        manager = RemoteMCPManager(config_file="nonexistent.json")

        config = {
            "transport": "http",
            "url": "https://api.example.com/mcp",
            "headers": {"X-API-Key": "test-key"},
        }

        manager.add_server("new-server", config)

        assert "new-server" in manager.servers
        server = manager.servers["new-server"]
        assert server.config.name == "new-server"
        assert server.config.transport == TransportType.HTTP

    def test_determine_auth_type(self):
        """Test authentication type determination"""
        manager = RemoteMCPManager(config_file="nonexistent.json")

        # OAuth2
        oauth_config = {"authentication": {"type": "oauth2"}}
        assert manager._determine_auth_type(oauth_config) == AuthType.OAUTH2

        # Bearer token
        bearer_config = {"authentication": {"type": "bearer"}}
        assert manager._determine_auth_type(bearer_config) == AuthType.BEARER

        # API key
        api_key_config = {"authentication": {"type": "api_key"}}
        assert manager._determine_auth_type(api_key_config) == AuthType.API_KEY

        # From headers - Bearer
        header_bearer = {"headers": {"Authorization": "Bearer token"}}
        assert manager._determine_auth_type(header_bearer) == AuthType.BEARER

        # From headers - API key
        header_api = {"headers": {"X-API-Key": "key"}}
        assert manager._determine_auth_type(header_api) == AuthType.API_KEY

        # No auth
        no_auth = {}
        assert manager._determine_auth_type(no_auth) == AuthType.NONE

    def test_expand_env_vars(self):
        """Test environment variable expansion"""
        manager = RemoteMCPManager(config_file="nonexistent.json")

        os.environ["TEST_VAR"] = "expanded-value"

        # Single variable
        result = manager._expand_env_vars("prefix-${TEST_VAR}-suffix")
        assert result == "prefix-expanded-value-suffix"

        # Multiple variables
        os.environ["VAR1"] = "one"
        os.environ["VAR2"] = "two"
        result = manager._expand_env_vars("${VAR1}-${VAR2}")
        assert result == "one-two"

        # No variables
        result = manager._expand_env_vars("no-variables-here")
        assert result == "no-variables-here"

        # Missing variable (keeps original)
        result = manager._expand_env_vars("${MISSING_VAR}")
        assert result == "${MISSING_VAR}"

        # Clean up
        del os.environ["TEST_VAR"]
        del os.environ["VAR1"]
        del os.environ["VAR2"]

    @pytest.mark.asyncio
    async def test_connect_all(self, temp_config_file):
        """Test connecting to all servers"""
        os.environ["TEST_API_KEY"] = "test-key"
        os.environ["OAUTH_CLIENT_ID"] = "client"
        os.environ["OAUTH_CLIENT_SECRET"] = "secret"

        manager = RemoteMCPManager(temp_config_file)

        with aioresponses() as mocked:
            # Mock connections
            mocked.get("https://api.example.com/mcp/health", status=200)
            mocked.post(
                "https://auth.example.com/token",
                payload={"access_token": "token", "expires_in": 3600},
            )

            await manager.connect_all()

            # Check all servers have sessions
            for server in manager.servers.values():
                assert server.session is not None

            await manager.disconnect_all()

        # Clean up
        del os.environ["TEST_API_KEY"]
        del os.environ["OAUTH_CLIENT_ID"]
        del os.environ["OAUTH_CLIENT_SECRET"]

    @pytest.mark.asyncio
    async def test_test_connectivity(self, temp_config_file):
        """Test connectivity testing"""
        os.environ["TEST_API_KEY"] = "test-key"
        os.environ["OAUTH_CLIENT_ID"] = "client"
        os.environ["OAUTH_CLIENT_SECRET"] = "secret"

        manager = RemoteMCPManager(temp_config_file)

        with aioresponses() as mocked:
            # Mock successful connection for test-server
            mocked.get("https://api.example.com/mcp/health", status=200)

            # Mock failed connection for oauth-server
            mocked.post("https://auth.example.com/token", status=401)

            results = await manager.test_connectivity()

            assert results["test-server"] is True
            assert results["oauth-server"] is False

        # Clean up
        del os.environ["TEST_API_KEY"]
        del os.environ["OAUTH_CLIENT_ID"]
        del os.environ["OAUTH_CLIENT_SECRET"]

    def test_get_server(self):
        """Test getting specific server"""
        manager = RemoteMCPManager(config_file="nonexistent.json")

        config = {
            "transport": "http",
            "url": "https://api.example.com/mcp",
            "headers": {"X-API-Key": "test"},
        }

        manager.add_server("test", config)

        server = manager.get_server("test")
        assert server is not None
        assert server.config.name == "test"

        missing = manager.get_server("nonexistent")
        assert missing is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
