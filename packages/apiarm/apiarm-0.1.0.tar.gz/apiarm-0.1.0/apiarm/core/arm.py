"""
API-ARM Main Class - The unified interface for API analysis and requests.

This is the main entry point that combines the analyzer, requester,
and security handler into a cohesive API manipulation tool.
"""

from pathlib import Path
from typing import Any, Optional
import httpx

from .analyzer import APIAnalyzer, AnalysisResult, AnalysisDepth
from .requester import APIRequester, RequestConfig
from .security import SecurityHandler, Credentials
from .logger import RequestLogger, LogLevel
from .cache import ResponseCache
from ..models.endpoint import AuthMethod, HTTPMethod
from ..models.response import APIResponse


class APIArm:
    """
    API-ARM: Application Programming Interface with Automated Request Manipulator.
    
    The main class that provides a unified interface for:
    - Analyzing APIs to understand their structure
    - Making secure, properly formatted requests
    - Handling authentication automatically
    - Managing the request/response lifecycle
    
    Usage:
        async with APIArm("https://api.example.com") as arm:
            # Analyze the API
            analysis = await arm.analyze()
            
            # Make requests
            response = await arm.get("/users")
            print(response.data)
    """
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize API-ARM.
        
        Args:
            base_url: The base URL of the target API
            headers: Optional default headers for all requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = headers or {}
        self.timeout = timeout
        
        # Components
        self.security = SecurityHandler()
        self.logger = RequestLogger(console_output=False)
        self.cache = ResponseCache(enabled=False)
        self._analyzer: Optional[APIAnalyzer] = None
        self._requester: Optional[APIRequester] = None
        self._analysis: Optional[AnalysisResult] = None
        self._client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.default_headers,
            timeout=self.timeout,
        )
        self._requester = APIRequester(
            base_url=self.base_url,
            security=self.security,
            default_headers=self.default_headers,
        )
        await self._requester.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._requester:
            await self._requester.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.aclose()
            
    # ==================== Configuration ====================
    
    def configure_auth(
        self,
        method: AuthMethod,
        **kwargs: Any,
    ) -> "APIArm":
        """
        Configure authentication for requests.
        
        Args:
            method: The authentication method to use
            **kwargs: Method-specific arguments:
                - API_KEY: api_key, header_name (optional)
                - BEARER: token
                - BASIC: username, password
                - OAUTH2: client_id, client_secret, token (optional)
                
        Returns:
            Self for method chaining
        """
        if method == AuthMethod.API_KEY:
            self.security.set_api_key(kwargs.get("api_key", ""))
            if "header_name" in kwargs:
                self.security.api_key_header = kwargs["header_name"]
        elif method == AuthMethod.BEARER:
            self.security.set_bearer_token(kwargs.get("token", ""))
        elif method == AuthMethod.BASIC:
            self.security.set_basic_auth(
                kwargs.get("username", ""),
                kwargs.get("password", ""),
            )
        elif method == AuthMethod.OAUTH2:
            self.security.set_oauth(
                client_id=kwargs.get("client_id", ""),
                client_secret=kwargs.get("client_secret", ""),
                token=kwargs.get("token"),
            )
        return self
    
    def set_api_key(self, api_key: str, header_name: str = "X-API-Key") -> "APIArm":
        """Convenience method to set API key auth."""
        self.security.set_api_key(api_key)
        self.security.api_key_header = header_name
        return self
    
    def set_bearer_token(self, token: str) -> "APIArm":
        """Convenience method to set bearer token auth."""
        self.security.set_bearer_token(token)
        return self
    
    # ==================== Logging & Caching ====================
    
    def enable_logging(
        self,
        console: bool = True,
        file_path: Optional[Path] = None,
    ) -> "APIArm":
        """
        Enable request/response logging.
        
        Args:
            console: Whether to print to console
            file_path: Optional path to log file
            
        Returns:
            Self for method chaining
        """
        self.logger = RequestLogger(
            console_output=console,
            file_output=file_path,
        )
        return self
    
    def enable_caching(
        self,
        max_size: int = 100,
        default_ttl: float = 300.0,
    ) -> "APIArm":
        """
        Enable response caching.
        
        Args:
            max_size: Maximum cache entries
            default_ttl: Default time-to-live in seconds
            
        Returns:
            Self for method chaining
        """
        self.cache = ResponseCache(
            max_size=max_size,
            default_ttl=default_ttl,
            enabled=True,
        )
        return self
    
    def disable_logging(self) -> "APIArm":
        """Disable request logging."""
        self.logger.console_output = False
        self.logger.file_output = None
        return self
    
    def disable_caching(self) -> "APIArm":
        """Disable response caching."""
        self.cache.enabled = False
        return self
        
    # ==================== Analysis ====================
    
    async def analyze(
        self,
        depth: AnalysisDepth = AnalysisDepth.STANDARD,
        force: bool = False,
    ) -> AnalysisResult:
        """
        Analyze the API to understand its structure.
        
        Args:
            depth: How deep to analyze
            force: Force re-analysis even if already done
            
        Returns:
            AnalysisResult with discovered information
        """
        if self._analysis and not force:
            return self._analysis
            
        async with APIAnalyzer(
            base_url=self.base_url,
            headers=self.default_headers,
            timeout=self.timeout,
        ) as analyzer:
            self._analysis = await analyzer.analyze(depth)
            
        return self._analysis
    
    @property
    def analysis(self) -> Optional[AnalysisResult]:
        """Get the last analysis result."""
        return self._analysis
    
    @property
    def is_analyzed(self) -> bool:
        """Check if the API has been analyzed."""
        return self._analysis is not None
        
    # ==================== Requests ====================
    
    async def request(
        self,
        path: str,
        method: HTTPMethod = HTTPMethod.GET,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> APIResponse:
        """
        Make a request to the API.
        
        Args:
            path: Endpoint path
            method: HTTP method
            use_cache: Whether to use cache for this request
            **kwargs: Additional request options (params, json_body, headers, etc.)
            
        Returns:
            APIResponse with the result
        """
        if not self._requester:
            raise RuntimeError(
                "APIArm must be used as an async context manager. "
                "Use 'async with APIArm(...) as arm:'"
            )
        
        # Check cache for GET requests
        cache_key = None
        if use_cache and self.cache.enabled and method == HTTPMethod.GET:
            cache_key = ResponseCache.generate_key(
                method.value,
                path,
                kwargs.get("params"),
            )
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # Start logging
        log_context = self.logger.start_request(
            method=method.value,
            url=f"{self.base_url}{path}",
            path=path,
            headers=self.default_headers,
            body=kwargs.get("json_body"),
        )
        
        # Make the request
        config = RequestConfig(method=method, **kwargs)
        response = await self._requester.request(path, config)
        
        # End logging
        self.logger.end_request(log_context, response)
        
        # Cache successful GET responses
        if cache_key and response.success:
            self.cache.set(cache_key, response)
            
        return response
    
    async def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a GET request."""
        return await self.request(path, HTTPMethod.GET, params=params, **kwargs)
    
    async def post(
        self,
        path: str,
        json_body: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a POST request."""
        return await self.request(path, HTTPMethod.POST, json_body=json_body, **kwargs)
    
    async def put(
        self,
        path: str,
        json_body: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a PUT request."""
        return await self.request(path, HTTPMethod.PUT, json_body=json_body, **kwargs)
    
    async def patch(
        self,
        path: str,
        json_body: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make a PATCH request."""
        return await self.request(path, HTTPMethod.PATCH, json_body=json_body, **kwargs)
    
    async def delete(self, path: str, **kwargs: Any) -> APIResponse:
        """Make a DELETE request."""
        return await self.request(path, HTTPMethod.DELETE, **kwargs)
        
    # ==================== Smart Request Building ====================
    
    async def smart_request(
        self,
        endpoint_path: str,
        method: Optional[HTTPMethod] = None,
        **kwargs: Any,
    ) -> APIResponse:
        """
        Make a smart request using analysis data.
        
        If the API has been analyzed, this method uses that information
        to build optimal requests with proper parameters and headers.
        
        Args:
            endpoint_path: The endpoint path
            method: HTTP method (auto-detected if None and analysis exists)
            **kwargs: Request parameters
            
        Returns:
            APIResponse with the result
        """
        # If no analysis, fall back to regular request
        if not self._analysis:
            return await self.request(
                endpoint_path,
                method or HTTPMethod.GET,
                **kwargs,
            )
            
        # Find matching endpoint from analysis
        matching_endpoint = None
        for ep in self._analysis.endpoints:
            if ep.path == endpoint_path or ep.matches_path(endpoint_path):
                matching_endpoint = ep
                break
                
        if matching_endpoint and method is None:
            # Use the first available method for this endpoint
            method = matching_endpoint.methods[0] if matching_endpoint.methods else HTTPMethod.GET
            
        return await self.request(
            endpoint_path,
            method or HTTPMethod.GET,
            **kwargs,
        )
    
    def __repr__(self) -> str:
        status = "analyzed" if self._analysis else "not analyzed"
        cache_status = f", cache={self.cache.size}" if self.cache.enabled else ""
        return f"APIArm(base_url='{self.base_url}', status='{status}'{cache_status})"
    
    def print_stats(self) -> None:
        """Print logging and caching statistics."""
        self.logger.print_summary()
        if self.cache.enabled:
            stats = self.cache.get_stats()
            print(f"\nCache: {stats['size']}/{stats['max_size']} entries, "
                  f"{stats['hit_rate']}% hit rate")
