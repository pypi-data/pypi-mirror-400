"""
MCP Client for Agentic Fabric SDK.

Provides a high-level client for interacting with the Agentic Fabric MCP server
using JSON-RPC 2.0 over SSE (Server-Sent Events).

Usage:
    # Using CLI stored credentials (user ran 'afctl auth login')
    async with MCPClient(method="cli", app_id="myapp", app_secret="sk_xxx") as client:
        tools = await client.list_tools()
        result = await client.call_tool("google_gmail_list_messages", {"max_results": 5})

    # Using Keycloak token directly (from agent's auth flow)
    async with MCPClient(
        method="keycloak",
        app_id="myapp",
        app_secret="sk_xxx",
        keycloak_token="eyJhbGc..."
    ) as client:
        result = await client.call_tool("google_gmail_list_messages", {"max_results": 5})

    # Using external IdP token (e.g., Okta SSO)
    async with MCPClient(
        method="idp",
        app_id="myapp",
        app_secret="sk_xxx",
        external_token="eyJhbGc..."
    ) as client:
        result = await client.call_tool("google_gmail_list_messages", {"max_results": 5})
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Literal, Optional, Union

import httpx

from .exceptions import (
    AuthenticationError,
    MCPConnectionError,
    MCPError,
)
from .auth.credentials import (
    load_stored_credentials,
    exchange_keycloak_for_af_token,
    AFTokenResponse,
)
from .auth.applications import exchange_okta_for_af_token

logger = logging.getLogger(__name__)

# Type alias for authentication method
AuthMethod = Literal["keycloak", "cli", "individual", "idp"]


class MCPClient:
    """
    Async/sync client for Agentic Fabric MCP server.
    
    Handles authentication and JSON-RPC 2.0 communication with the MCP endpoint.
    
    Authentication Methods:
        - "cli": Uses stored credentials from 'afctl auth login' (no token needed)
        - "keycloak": Pass a Keycloak token directly via keycloak_token parameter
        - "idp": Pass an external IdP token (e.g., Okta) via external_token parameter
    
    Args:
        method: Authentication method - "cli" (stored credentials), 
                "keycloak" (pass keycloak token), or "idp" (external IdP token)
        app_id: Application ID from afctl activation
        app_secret: Application secret from afctl activation
        keycloak_token: Keycloak JWT token (required when method="keycloak")
        external_token: External IdP token like Okta (required when method="idp")
        mcp_url: MCP server URL (default: staging)
        gateway_url: Gateway URL for token exchange (default: staging)
        timeout: Request timeout in seconds (default: 60)
    
    Example:
        >>> # Using CLI stored credentials (user already ran 'afctl auth login')
        >>> async with MCPClient(
        ...     method="cli",
        ...     app_id="org-xxx_myapp",
        ...     app_secret="sk_xxx..."
        ... ) as client:
        ...     tools = await client.list_tools()
        ...     print(f"Available tools: {client.tool_names}")
        
        >>> # Using Keycloak token from agent's auth flow
        >>> async with MCPClient(
        ...     method="keycloak",
        ...     app_id="org-xxx_myapp",
        ...     app_secret="sk_xxx...",
        ...     keycloak_token="eyJhbGc..."  # Token from Keycloak login
        ... ) as client:
        ...     result = await client.call_tool("google_gmail_list_messages", {})
        
        >>> # Using external IdP token (e.g., Okta SSO)
        >>> async with MCPClient(
        ...     method="idp",
        ...     app_id="org-xxx_myapp",
        ...     app_secret="sk_xxx...",
        ...     external_token="eyJhbGc..."  # Token from Okta
        ... ) as client:
        ...     result = await client.call_tool("google_gmail_list_messages", {})
    """
    
    # Default URLs
    DEFAULT_MCP_URL = "https://staging.agenticfabriq.com/mcp"
    DEFAULT_GATEWAY_URL = "https://staging.agenticfabriq.com"
    
    def __init__(
        self,
        *,
        method: AuthMethod,
        app_id: str,
        app_secret: str,
        keycloak_token: Optional[str] = None,
        external_token: Optional[str] = None,
        mcp_url: Optional[str] = None,
        gateway_url: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        # Validate method
        if method not in ("keycloak", "cli", "individual", "idp"):
            raise ValueError(
                f"Invalid method '{method}'. Must be 'cli', 'keycloak', or 'idp'"
            )
        
        # Validate token requirements based on method
        if method == "keycloak" and not keycloak_token:
            raise ValueError("keycloak_token is required when method='keycloak'")
        if method == "idp" and not external_token:
            raise ValueError("external_token is required when method='idp'")
        
        self._method = method
        self._app_id = app_id
        self._app_secret = app_secret
        self._keycloak_token = keycloak_token
        self._external_token = external_token
        self._mcp_url = (mcp_url or self.DEFAULT_MCP_URL).rstrip("/")
        self._gateway_url = (gateway_url or self.DEFAULT_GATEWAY_URL).rstrip("/")
        self._timeout = timeout
        
        # Internal state
        self._http_client: Optional[httpx.AsyncClient] = None
        self._af_token: Optional[str] = None
        self._af_token_response: Optional[AFTokenResponse] = None
        self._tools: List[Dict[str, Any]] = []
        self._request_id: int = 0
        
        # Event loop management for sync wrappers
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    
    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self._http_client is not None
    
    @property
    def tool_names(self) -> List[str]:
        """Get list of available tool names."""
        return [t.get("name", "") for t in self._tools]
    
    @property
    def token_info(self) -> Optional[AFTokenResponse]:
        """Get the AF token response with metadata."""
        return self._af_token_response
    
    # -------------------------------------------------------------------------
    # Context Managers
    # -------------------------------------------------------------------------
    
    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
    
    def __enter__(self) -> "MCPClient":
        """Sync context manager entry."""
        self.connect_sync()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Sync context manager exit."""
        self.disconnect_sync()
    
    # -------------------------------------------------------------------------
    # Connection Management
    # -------------------------------------------------------------------------
    
    async def connect(self) -> None:
        """
        Connect to the MCP server.
        
        Authenticates based on the configured method and verifies the connection
        by fetching the available tools.
        
        Raises:
            AuthenticationError: If authentication fails
            MCPConnectionError: If connection to MCP server fails
        """
        # Get AF token via authentication
        self._af_token = await self._authenticate()
        
        # Debug: log token (first 20 chars only for security)
        if self._af_token:
            logger.debug(f"AF token obtained: {self._af_token[:20]}...")
        else:
            logger.error("AF token is empty or None!")
            raise AuthenticationError("Token exchange returned empty token")
        
        # Create HTTP client without base_url - we'll pass full URL each time
        # This avoids potential issues with httpx stream() and base_url
        self._http_client = httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
        )
        
        # Verify connection by listing tools
        try:
            self._tools = await self.list_tools()
            logger.info(
                f"Connected to MCP server. {len(self._tools)} tools available."
            )
        except Exception as e:
            # Clean up on failure
            await self.disconnect()
            raise MCPConnectionError(f"Failed to connect to MCP server: {e}") from e
    
    async def disconnect(self) -> None:
        """
        Disconnect from the MCP server.
        
        Closes the HTTP client and clears internal state.
        """
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
        
        self._af_token = None
        logger.info("Disconnected from MCP server.")
    
    # -------------------------------------------------------------------------
    # Sync Wrappers
    # -------------------------------------------------------------------------
    
    def _get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """Get existing event loop or create a new one."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Loop closed")
            return loop
        except RuntimeError:
            # No running loop or loop is closed
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            return loop
    
    def connect_sync(self) -> None:
        """Synchronous version of connect()."""
        loop = self._get_or_create_loop()
        loop.run_until_complete(self.connect())
    
    def disconnect_sync(self) -> None:
        """Synchronous version of disconnect()."""
        loop = self._get_or_create_loop()
        loop.run_until_complete(self.disconnect())
    
    def list_tools_sync(self) -> List[Dict[str, Any]]:
        """Synchronous version of list_tools()."""
        loop = self._get_or_create_loop()
        return loop.run_until_complete(self.list_tools())
    
    def call_tool_sync(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Synchronous version of call_tool()."""
        loop = self._get_or_create_loop()
        return loop.run_until_complete(self.call_tool(name, arguments))
    
    # -------------------------------------------------------------------------
    # MCP Methods
    # -------------------------------------------------------------------------
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available MCP tools.
        
        Returns:
            List of tool definitions with name, description, and inputSchema
            
        Raises:
            MCPError: If the MCP server returns an error
            MCPConnectionError: If not connected
        """
        result = await self._jsonrpc_request("tools/list")
        
        # Extract tools array from result
        tools = result.get("tools", []) if isinstance(result, dict) else result
        
        # Cache tools
        self._tools = [
            {
                "name": t.get("name"),
                "description": t.get("description"),
                "inputSchema": t.get("inputSchema"),
            }
            for t in tools
        ]
        
        return self._tools
    
    async def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Call an MCP tool.
        
        Args:
            name: Tool name (e.g., "google_gmail_list_messages")
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool result (content from the response)
            
        Raises:
            MCPError: If the MCP server returns an error
            MCPConnectionError: If not connected
        """
        result = await self._jsonrpc_request(
            "tools/call",
            params={
                "name": name,
                "arguments": arguments or {},
            },
        )
        
        # Handle result format - may have "content" key or return directly
        if isinstance(result, dict) and "content" in result:
            return result["content"]
        return result
    
    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get cached tools list without making a network call.
        
        Returns:
            List of cached tool definitions
        """
        return self._tools
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific tool by name from the cache.
        
        Args:
            name: Tool name to find
            
        Returns:
            Tool definition or None if not found
        """
        for tool in self._tools:
            if tool.get("name") == name:
                return tool
        return None
    
    def has_tool(self, name: str) -> bool:
        """
        Check if a tool exists in the cache.
        
        Args:
            name: Tool name to check
            
        Returns:
            True if tool exists, False otherwise
        """
        return self.get_tool(name) is not None
    
    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------
    
    async def _authenticate(self) -> str:
        """
        Authenticate and get AF token based on configured method.
        
        Authentication methods:
            - "cli": Load stored credentials from 'afctl auth login'
            - "keycloak": Use the provided keycloak_token directly
            - "idp": Use the provided external_token (e.g., Okta) directly
        
        Returns:
            AF access token string
            
        Raises:
            AuthenticationError: If authentication fails
        """
        token_for_exchange: Optional[str] = None
        
        if self._method in ("cli", "individual"):
            # Load stored credentials from CLI login
            creds = load_stored_credentials()
            if creds is None:
                raise AuthenticationError(
                    "Not logged in. Please run 'afctl auth login' first."
                )
            if creds.is_expired:
                raise AuthenticationError(
                    "Token expired. Please run 'afctl auth login' again."
                )
            token_for_exchange = creds.access_token
            logger.info("Using stored CLI credentials")
            
        elif self._method == "keycloak":
            # Use the provided Keycloak token directly
            token_for_exchange = self._keycloak_token
            logger.info("Using provided Keycloak token")
                
        elif self._method == "idp":
            # Use external IdP token (e.g., Okta)
            token_for_exchange = self._external_token
            logger.info("Using provided external IdP token")
        
        if not token_for_exchange:
            raise AuthenticationError("Failed to obtain authentication token")
        
        # Exchange for AF token - use different endpoint based on method
        if self._method == "idp":
            # IdP method (Okta SSO) uses okta exchange endpoint
            af_token = await exchange_okta_for_af_token(
                okta_token=token_for_exchange,
                app_id=self._app_id,
                app_secret=self._app_secret,
                gateway_url=self._gateway_url,
            )
            # exchange_okta_for_af_token returns just the token string
            self._af_token_response = AFTokenResponse(
                access_token=af_token,
                expires_in=3600,  # Default 1 hour
                token_type="Bearer",
            )
            logger.info(f"Authenticated via IdP (Okta) for app_id={self._app_id}")
        else:
            # Keycloak and CLI methods use keycloak exchange endpoint
            self._af_token_response = await exchange_keycloak_for_af_token(
                keycloak_token=token_for_exchange,
                app_id=self._app_id,
                secret_key=self._app_secret,
                gateway_url=self._gateway_url,
            )
            logger.info(
                f"Authenticated as user_id={self._af_token_response.user_id}, "
                f"app_id={self._af_token_response.app_id}"
            )
        
        return self._af_token_response.access_token
    
    async def _jsonrpc_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a JSON-RPC 2.0 request to the MCP server.
        
        Args:
            method: JSON-RPC method name (e.g., "tools/list")
            params: Optional parameters
            
        Returns:
            Result from the JSON-RPC response
            
        Raises:
            MCPError: If the server returns a JSON-RPC error
            MCPConnectionError: If not connected or network error
        """
        if self._http_client is None:
            raise MCPConnectionError(
                "Not connected. Call connect() first or use context manager."
            )
        
        # Build request payload
        self._request_id += 1
        payload: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._request_id,
        }
        if params:
            payload["params"] = params
        
        logger.debug(f"MCP request: {method} (id={self._request_id})")
        
        try:
            # Build headers explicitly
            request_headers = {
                "Authorization": f"Bearer {self._af_token}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream, application/json",
            }
            
            logger.debug(f"MCP request to {self._mcp_url}")
            logger.debug(f"Authorization header present: {'Authorization' in request_headers}")
            
            # Send as streaming POST request with full URL
            async with self._http_client.stream(
                "POST",
                self._mcp_url,  # Full URL instead of empty path
                json=payload,
                headers=request_headers,
            ) as response:
                # Check HTTP status
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise MCPConnectionError(
                        f"MCP server returned HTTP {response.status_code}: {error_text.decode()}"
                    )
                
                # Parse response - handle both SSE and plain JSON
                return await self._parse_sse_response(response)
                
        except httpx.RequestError as e:
            raise MCPConnectionError(f"Network error: {e}") from e
    
    async def _parse_sse_response(
        self,
        response: httpx.Response,
    ) -> Any:
        """
        Parse SSE or JSON response from MCP server.
        
        Handles both:
        - SSE format with "data:" prefixed lines
        - Plain JSON responses
        
        Returns:
            Result from JSON-RPC response
            
        Raises:
            MCPError: If the response contains a JSON-RPC error
        """
        accumulated_data = ""
        
        async for line in response.aiter_lines():
            line = line.strip()
            
            if not line:
                continue
            
            # Handle SSE format
            if line.startswith("data:"):
                data = line[5:].strip()
                if data:
                    accumulated_data += data
            else:
                # Plain JSON or continuation
                accumulated_data += line
            
            # Try to parse accumulated data as JSON
            try:
                parsed = json.loads(accumulated_data)
                
                # Check for JSON-RPC error
                if "error" in parsed:
                    error = parsed["error"]
                    raise MCPError(
                        message=error.get("message", "Unknown MCP error"),
                        code=error.get("code"),
                        data=error.get("data"),
                    )
                
                # Return result on success
                if "result" in parsed:
                    return parsed["result"]
                
                # Some responses may not have result wrapper
                return parsed
                
            except json.JSONDecodeError:
                # Keep accumulating
                continue
        
        # If we get here without valid JSON, try one more parse
        if accumulated_data:
            try:
                parsed = json.loads(accumulated_data)
                if "error" in parsed:
                    error = parsed["error"]
                    raise MCPError(
                        message=error.get("message", "Unknown MCP error"),
                        code=error.get("code"),
                        data=error.get("data"),
                    )
                if "result" in parsed:
                    return parsed["result"]
                return parsed
            except json.JSONDecodeError:
                raise MCPError(f"Invalid JSON response from MCP server: {accumulated_data[:200]}")
        
        raise MCPError("Empty response from MCP server")
    
    def __repr__(self) -> str:
        status = "connected" if self.is_connected else "disconnected"
        return (
            f"MCPClient(method={self._method!r}, app_id={self._app_id!r}, "
            f"mcp_url={self._mcp_url!r}, status={status})"
        )

