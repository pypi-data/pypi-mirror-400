"""
Security Handler - Manages authentication and security for API requests.

This module is responsible for:
- Storing and applying credentials securely
- Supporting multiple authentication methods
- Token refresh and management
- Secure credential storage
"""

import base64
import os
from typing import Any, Callable, Optional, Awaitable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from ..models.endpoint import AuthMethod


@dataclass
class Credentials:
    """Stores authentication credentials."""
    auth_method: AuthMethod
    api_key: Optional[str] = None
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_token: Optional[str] = None
    oauth_refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    
    @classmethod
    def from_env(cls, auth_method: AuthMethod) -> "Credentials":
        """Create credentials from environment variables."""
        return cls(
            auth_method=auth_method,
            api_key=os.getenv("API_ARM_API_KEY"),
            bearer_token=os.getenv("API_ARM_BEARER_TOKEN"),
            username=os.getenv("API_ARM_USERNAME"),
            password=os.getenv("API_ARM_PASSWORD"),
            oauth_client_id=os.getenv("API_ARM_OAUTH_CLIENT_ID"),
            oauth_client_secret=os.getenv("API_ARM_OAUTH_CLIENT_SECRET"),
        )
    
    @property
    def is_token_expired(self) -> bool:
        """Check if the OAuth token is expired."""
        if not self.token_expiry:
            return False
        return datetime.now() >= self.token_expiry


class SecurityHandler:
    """
    Handles all security aspects of API requests.
    
    Supports:
    - API Key authentication (header or query param)
    - Bearer token authentication
    - Basic authentication
    - OAuth 2.0 with token refresh
    """
    
    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        api_key_header: str = "X-API-Key",
        api_key_param: Optional[str] = None,
    ):
        """
        Initialize the security handler.
        
        Args:
            credentials: Authentication credentials
            api_key_header: Header name for API key auth
            api_key_param: Query param name for API key (if using query param auth)
        """
        self.credentials = credentials
        self.api_key_header = api_key_header
        self.api_key_param = api_key_param
        self._token_refresh_callback: Optional[
            Callable[[], Awaitable[str]]
        ] = None
        
    def set_credentials(self, credentials: Credentials) -> None:
        """Set or update credentials."""
        self.credentials = credentials
        
    def set_api_key(self, api_key: str) -> None:
        """Convenience method to set API key authentication."""
        self.credentials = Credentials(
            auth_method=AuthMethod.API_KEY,
            api_key=api_key,
        )
        
    def set_bearer_token(self, token: str) -> None:
        """Convenience method to set bearer token authentication."""
        self.credentials = Credentials(
            auth_method=AuthMethod.BEARER,
            bearer_token=token,
        )
        
    def set_basic_auth(self, username: str, password: str) -> None:
        """Convenience method to set basic authentication."""
        self.credentials = Credentials(
            auth_method=AuthMethod.BASIC,
            username=username,
            password=password,
        )
        
    def set_oauth(
        self,
        client_id: str,
        client_secret: str,
        token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[datetime] = None,
    ) -> None:
        """Set OAuth 2.0 credentials."""
        self.credentials = Credentials(
            auth_method=AuthMethod.OAUTH2,
            oauth_client_id=client_id,
            oauth_client_secret=client_secret,
            oauth_token=token,
            oauth_refresh_token=refresh_token,
            token_expiry=token_expiry,
        )
        
    def set_token_refresh_callback(
        self,
        callback: Callable[[], Awaitable[str]],
    ) -> None:
        """Set a callback function for refreshing OAuth tokens."""
        self._token_refresh_callback = callback
        
    async def apply_auth(
        self,
        headers: dict[str, str],
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, str]:
        """
        Apply authentication to request headers.
        
        Args:
            headers: Existing headers dict
            params: Query parameters (for API key in query param)
            
        Returns:
            Updated headers dict
        """
        if not self.credentials:
            return headers
            
        auth_method = self.credentials.auth_method
        
        if auth_method == AuthMethod.API_KEY:
            headers = self._apply_api_key(headers)
        elif auth_method == AuthMethod.BEARER:
            headers = await self._apply_bearer(headers)
        elif auth_method == AuthMethod.BASIC:
            headers = self._apply_basic(headers)
        elif auth_method == AuthMethod.OAUTH2:
            headers = await self._apply_oauth(headers)
            
        return headers
    
    def _apply_api_key(self, headers: dict[str, str]) -> dict[str, str]:
        """Apply API key authentication."""
        if self.credentials and self.credentials.api_key:
            headers[self.api_key_header] = self.credentials.api_key
        return headers
    
    async def _apply_bearer(self, headers: dict[str, str]) -> dict[str, str]:
        """Apply bearer token authentication."""
        if self.credentials and self.credentials.bearer_token:
            headers["Authorization"] = f"Bearer {self.credentials.bearer_token}"
        return headers
    
    def _apply_basic(self, headers: dict[str, str]) -> dict[str, str]:
        """Apply basic authentication."""
        if self.credentials and self.credentials.username and self.credentials.password:
            credentials = f"{self.credentials.username}:{self.credentials.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        return headers
    
    async def _apply_oauth(self, headers: dict[str, str]) -> dict[str, str]:
        """Apply OAuth 2.0 authentication, refreshing token if needed."""
        if not self.credentials:
            return headers
            
        # Check if token needs refresh
        if self.credentials.is_token_expired and self._token_refresh_callback:
            new_token = await self._token_refresh_callback()
            self.credentials.oauth_token = new_token
            
        if self.credentials.oauth_token:
            headers["Authorization"] = f"Bearer {self.credentials.oauth_token}"
            
        return headers
    
    def get_api_key_param(self) -> Optional[tuple[str, str]]:
        """Get API key as query parameter if configured that way."""
        if (
            self.api_key_param
            and self.credentials
            and self.credentials.api_key
        ):
            return (self.api_key_param, self.credentials.api_key)
        return None
    
    @staticmethod
    def mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
        """Mask a sensitive value for logging purposes."""
        if len(value) <= visible_chars:
            return "*" * len(value)
        return value[:visible_chars] + "*" * (len(value) - visible_chars)
