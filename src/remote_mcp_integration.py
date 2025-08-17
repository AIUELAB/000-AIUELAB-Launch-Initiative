#!/usr/bin/env python3
"""
Remote MCP Server Integration Module

Provides utilities for connecting to and managing remote MCP servers
with support for SSE/HTTP transports and OAuth 2.0 authentication.
"""

import json
import os
import time
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import logging
from urllib.parse import urlencode, urlparse
import hashlib
import secrets
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransportType(Enum):
    """MCP Transport protocols"""

    SSE = "sse"
    HTTP = "http"
    STDIO = "stdio"


class AuthType(Enum):
    """Authentication types for remote servers"""

    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


@dataclass
class RemoteServerConfig:
    """Configuration for a remote MCP server"""

    name: str
    transport: TransportType
    url: str
    auth_type: AuthType
    headers: Optional[Dict[str, str]] = None
    oauth_config: Optional[Dict[str, str]] = None
    timeout: int = 30000
    retry_attempts: int = 3
    tls_verify: bool = True


@dataclass
class OAuthToken:
    """OAuth token information"""

    access_token: str
    token_type: str
    expires_at: datetime
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now() >= self.expires_at

    @property
    def needs_refresh(self) -> bool:
        """Check if token needs refresh (5 minutes before expiry)"""
        return datetime.now() >= (self.expires_at - timedelta(minutes=5))


class RemoteMCPClient:
    """Client for connecting to remote MCP servers"""

    def __init__(self, config: RemoteServerConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[OAuthToken] = None
        self.sse_client = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self):
        """Establish connection to remote server"""
        headers = self.config.headers or {}

        # Add authentication headers
        auth_headers = await self._get_auth_headers()
        headers.update(auth_headers)

        # Create session
        connector = aiohttp.TCPConnector(ssl=self.config.tls_verify)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout / 1000)

        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers)

        # Connect based on transport type
        if self.config.transport == TransportType.SSE:
            await self._connect_sse()
        elif self.config.transport == TransportType.HTTP:
            await self._test_connection()

        logger.info(f"Connected to {self.config.name} via {self.config.transport.value}")

    async def disconnect(self):
        """Close connection to remote server"""
        if self.sse_client:
            self.sse_client.close()
        if self.session:
            await self.session.close()
        logger.info(f"Disconnected from {self.config.name}")

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        headers = {}

        if self.config.auth_type == AuthType.API_KEY:
            if self.config.headers and "X-API-Key" in self.config.headers:
                headers["X-API-Key"] = self.config.headers["X-API-Key"]

        elif self.config.auth_type == AuthType.BEARER:
            if self.config.headers and "Authorization" in self.config.headers:
                headers["Authorization"] = self.config.headers["Authorization"]

        elif self.config.auth_type == AuthType.OAUTH2:
            token = await self._get_oauth_token()
            headers["Authorization"] = f"Bearer {token.access_token}"

        return headers

    async def _get_oauth_token(self) -> OAuthToken:
        """Get or refresh OAuth token"""
        if self.token and not self.token.needs_refresh:
            return self.token

        if self.token and self.token.refresh_token:
            # Refresh existing token
            self.token = await self._refresh_oauth_token(self.token.refresh_token)
        else:
            # Get new token
            self.token = await self._request_oauth_token()

        return self.token

    async def _request_oauth_token(self) -> OAuthToken:
        """Request new OAuth token"""
        if not self.config.oauth_config:
            raise ValueError(f"OAuth config missing for {self.config.name}")

        token_endpoint = self.config.oauth_config.get("tokenEndpoint")
        client_id = self.config.oauth_config.get("clientId")
        client_secret = self.config.oauth_config.get("clientSecret")
        scope = self.config.oauth_config.get("scope", "")

        if not all([token_endpoint, client_id, client_secret]):
            raise ValueError("Missing OAuth credentials")

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_endpoint, data=data) as response:
                if response.status != 200:
                    raise Exception(f"OAuth token request failed: {response.status}")

                token_data = await response.json()

                expires_in = token_data.get("expires_in", 3600)
                expires_at = datetime.now() + timedelta(seconds=expires_in)

                return OAuthToken(
                    access_token=token_data["access_token"],
                    token_type=token_data.get("token_type", "Bearer"),
                    expires_at=expires_at,
                    refresh_token=token_data.get("refresh_token"),
                    scope=token_data.get("scope"),
                )

    async def _refresh_oauth_token(self, refresh_token: str) -> OAuthToken:
        """Refresh OAuth token"""
        token_endpoint = self.config.oauth_config.get("tokenEndpoint")
        client_id = self.config.oauth_config.get("clientId")
        client_secret = self.config.oauth_config.get("clientSecret")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_endpoint, data=data) as response:
                if response.status != 200:
                    # Refresh failed, get new token
                    return await self._request_oauth_token()

                token_data = await response.json()

                expires_in = token_data.get("expires_in", 3600)
                expires_at = datetime.now() + timedelta(seconds=expires_in)

                return OAuthToken(
                    access_token=token_data["access_token"],
                    token_type=token_data.get("token_type", "Bearer"),
                    expires_at=expires_at,
                    refresh_token=token_data.get("refresh_token", refresh_token),
                    scope=token_data.get("scope"),
                )

    async def _connect_sse(self):
        """Connect to SSE endpoint"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        # SSE connection will be established when first message is sent
        logger.info(f"SSE endpoint configured: {self.config.url}")

    async def _test_connection(self):
        """Test HTTP connection"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        try:
            async with self.session.get(f"{self.config.url}/health") as response:
                if response.status not in [200, 404]:
                    raise Exception(f"Connection test failed: {response.status}")
        except aiohttp.ClientError as e:
            logger.warning(f"Health check failed for {self.config.name}: {e}")
            # Don't fail - server might not have health endpoint

    async def send_request(self, method: str, params: Optional[Dict] = None) -> Any:
        """Send request to remote MCP server"""
        if not self.session:
            raise RuntimeError("Not connected")

        # Refresh auth if needed
        if self.config.auth_type == AuthType.OAUTH2:
            headers = await self._get_auth_headers()
            self.session.headers.update(headers)

        request_id = secrets.token_hex(8)

        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}

        if self.config.transport == TransportType.SSE:
            return await self._send_sse_request(payload)
        else:
            return await self._send_http_request(payload)

    async def _send_http_request(self, payload: Dict) -> Any:
        """Send HTTP request"""
        for attempt in range(self.config.retry_attempts):
            try:
                async with self.session.post(self.config.url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result")
                    elif response.status >= 500 and attempt < self.config.retry_attempts - 1:
                        # Retry on server errors
                        await asyncio.sleep(2**attempt)
                        continue
                    else:
                        error_text = await response.text()
                        raise Exception(f"Request failed: {response.status} - {error_text}")
            except aiohttp.ClientError as e:
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                raise

    async def _send_sse_request(self, payload: Dict) -> Any:
        """Send SSE request and wait for response"""
        # For SSE, we need to send via POST and listen for response
        async with self.session.post(f"{self.config.url}/request", json=payload) as response:
            if response.status != 200:
                raise Exception(f"SSE request failed: {response.status}")

            # Read SSE response
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data.get("id") == payload["id"]:
                        return data.get("result")


class RemoteMCPManager:
    """Manager for multiple remote MCP servers"""

    def __init__(self, config_file: Optional[str] = None):
        self.servers: Dict[str, RemoteMCPClient] = {}
        self.config_file = config_file or "mcp-config/remote-servers.json"
        self.load_config()

    def load_config(self):
        """Load remote server configurations"""
        if not os.path.exists(self.config_file):
            logger.warning(f"Config file not found: {self.config_file}")
            return

        with open(self.config_file, 'r') as f:
            config = json.load(f)

        for name, server_config in config.get("remoteMcpServers", {}).items():
            self.add_server(name, server_config)

    def add_server(self, name: str, config: Dict[str, Any]):
        """Add a remote server"""
        transport = TransportType(config.get("transport", "http"))
        auth_type = self._determine_auth_type(config)

        server_config = RemoteServerConfig(
            name=name,
            transport=transport,
            url=self._expand_env_vars(config["url"]),
            auth_type=auth_type,
            headers=self._expand_headers(config.get("headers", {})),
            oauth_config=config.get("authentication", {}) if auth_type == AuthType.OAUTH2 else None,
            timeout=config.get("timeout", 30000),
            retry_attempts=config.get("retryPolicy", {}).get("maxRetries", 3),
            tls_verify=config.get("tlsVerify", True),
        )

        self.servers[name] = RemoteMCPClient(server_config)
        logger.info(f"Added remote server: {name}")

    def _determine_auth_type(self, config: Dict) -> AuthType:
        """Determine authentication type from config"""
        auth = config.get("authentication", {})

        if auth.get("type") == "oauth2":
            return AuthType.OAUTH2
        elif auth.get("type") == "bearer":
            return AuthType.BEARER
        elif auth.get("type") == "api_key":
            return AuthType.API_KEY
        elif "headers" in config:
            headers = config["headers"]
            if "Authorization" in headers:
                return AuthType.BEARER
            elif "X-API-Key" in headers:
                return AuthType.API_KEY

        return AuthType.NONE

    def _expand_env_vars(self, value: str) -> str:
        """Expand environment variables in string"""
        if "${" in value:
            import re

            pattern = r'\$\{([^}]+)\}'

            def replace(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0))

            return re.sub(pattern, replace, value)
        return value

    def _expand_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Expand environment variables in headers"""
        return {key: self._expand_env_vars(value) for key, value in headers.items()}

    async def connect_all(self):
        """Connect to all configured servers"""
        tasks = [server.connect() for server in self.servers.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def disconnect_all(self):
        """Disconnect from all servers"""
        tasks = [server.disconnect() for server in self.servers.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def test_connectivity(self) -> Dict[str, bool]:
        """Test connectivity to all servers"""
        results = {}

        for name, server in self.servers.items():
            try:
                await server.connect()
                results[name] = True
                await server.disconnect()
            except Exception as e:
                logger.error(f"Failed to connect to {name}: {e}")
                results[name] = False

        return results

    def get_server(self, name: str) -> Optional[RemoteMCPClient]:
        """Get a specific server client"""
        return self.servers.get(name)


# Example usage
async def main():
    """Example usage of remote MCP integration"""

    # Initialize manager
    manager = RemoteMCPManager()

    # Test connectivity
    print("Testing remote server connectivity...")
    results = await manager.test_connectivity()

    for server, connected in results.items():
        status = "✅ Connected" if connected else "❌ Failed"
        print(f"{server}: {status}")

    # Use a specific server
    linear = manager.get_server("linear")
    if linear:
        async with linear:
            # Send a request
            result = await linear.send_request("listIssues", {"project": "PROJ-1"})
            print(f"Linear issues: {result}")

    # Disconnect all
    await manager.disconnect_all()


if __name__ == "__main__":
    asyncio.run(main())
