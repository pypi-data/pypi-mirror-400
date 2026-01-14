"""
API Requester - Handles making secure requests to APIs.

This module is responsible for:
- Building properly formatted requests
- Handling authentication
- Managing request/response lifecycle
- Retry logic and error handling
"""

import asyncio
from typing import Any, Optional, Union
from dataclasses import dataclass
import httpx

from ..models.endpoint import AuthMethod, HTTPMethod
from ..models.response import APIResponse
from .security import SecurityHandler


@dataclass
class RequestConfig:
    """Configuration for a request."""
    method: HTTPMethod = HTTPMethod.GET
    headers: Optional[dict[str, str]] = None
    params: Optional[dict[str, Any]] = None
    json_body: Optional[dict[str, Any]] = None
    data: Optional[dict[str, Any]] = None
    timeout: float = 30.0
    retries: int = 3
    retry_delay: float = 1.0


class APIRequester:
    """
    Makes secure API requests with proper authentication and error handling.
    
    This is the arm of API-ARM - it executes requests based on
    what the analyzer has learned about the API.
    """
    
    def __init__(
        self,
        base_url: str,
        security: Optional[SecurityHandler] = None,
        default_headers: Optional[dict[str, str]] = None,
    ):
        """
        Initialize the API requester.
        
        Args:
            base_url: The base URL of the API
            security: Security handler for authentication
            default_headers: Headers to include in all requests
        """
        self.base_url = base_url.rstrip("/")
        self.security = security or SecurityHandler()
        self.default_headers = default_headers or {}
        self._client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.default_headers,
            follow_redirects=True,
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            
    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, ensuring it's initialized."""
        if not self._client:
            raise RuntimeError(
                "APIRequester must be used as an async context manager. "
                "Use 'async with APIRequester(...) as requester:'"
            )
        return self._client
    
    async def request(
        self,
        path: str,
        config: Optional[RequestConfig] = None,
    ) -> APIResponse:
        """
        Make a request to the API.
        
        Args:
            path: The endpoint path
            config: Request configuration
            
        Returns:
            APIResponse containing the result
        """
        config = config or RequestConfig()
        
        # Build headers
        headers = {**self.default_headers}
        if config.headers:
            headers.update(config.headers)
            
        # Apply authentication
        headers = await self.security.apply_auth(headers)
        
        # Attempt request with retries
        last_error: Optional[Exception] = None
        
        for attempt in range(config.retries):
            try:
                response = await self._make_request(path, config, headers)
                return self._build_response(response)
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < config.retries - 1:
                    await asyncio.sleep(config.retry_delay * (attempt + 1))
            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    return self._build_response(e.response)
                last_error = e
                if attempt < config.retries - 1:
                    await asyncio.sleep(config.retry_delay * (attempt + 1))
            except Exception as e:
                last_error = e
                break
                
        # All retries failed
        return APIResponse(
            success=False,
            status_code=0,
            error=str(last_error),
        )
    
    async def _make_request(
        self,
        path: str,
        config: RequestConfig,
        headers: dict[str, str],
    ) -> httpx.Response:
        """Execute the actual HTTP request."""
        method = config.method.value.upper()
        
        request_kwargs: dict[str, Any] = {
            "url": path,
            "headers": headers,
            "timeout": config.timeout,
        }
        
        if config.params:
            request_kwargs["params"] = config.params
        if config.json_body:
            request_kwargs["json"] = config.json_body
        elif config.data:
            request_kwargs["data"] = config.data
            
        response = await self.client.request(method, **request_kwargs)
        return response
    
    def _build_response(self, response: httpx.Response) -> APIResponse:
        """Build an APIResponse from an httpx response."""
        # Try to parse JSON
        data: Optional[dict[str, Any]] = None
        try:
            data = response.json()
        except Exception:
            pass
            
        return APIResponse(
            success=200 <= response.status_code < 400,
            status_code=response.status_code,
            headers=dict(response.headers),
            data=data,
            text=response.text if not data else None,
        )
    
    # Convenience methods for common HTTP methods
    
    async def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a GET request."""
        config = RequestConfig(
            method=HTTPMethod.GET,
            params=params,
            **kwargs,
        )
        return await self.request(path, config)
    
    async def post(
        self,
        path: str,
        json_body: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a POST request."""
        config = RequestConfig(
            method=HTTPMethod.POST,
            json_body=json_body,
            data=data,
            **kwargs,
        )
        return await self.request(path, config)
    
    async def put(
        self,
        path: str,
        json_body: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a PUT request."""
        config = RequestConfig(
            method=HTTPMethod.PUT,
            json_body=json_body,
            **kwargs,
        )
        return await self.request(path, config)
    
    async def patch(
        self,
        path: str,
        json_body: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a PATCH request."""
        config = RequestConfig(
            method=HTTPMethod.PATCH,
            json_body=json_body,
            **kwargs,
        )
        return await self.request(path, config)
    
    async def delete(
        self,
        path: str,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a DELETE request."""
        config = RequestConfig(
            method=HTTPMethod.DELETE,
            **kwargs,
        )
        return await self.request(path, config)
