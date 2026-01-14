"""
API Analyzer - Analyzes API endpoints to determine their usage patterns.

This module is responsible for:
- Detecting API structure and endpoints
- Identifying authentication methods
- Understanding request/response formats
- Building a map of available operations
"""

import re
import os
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import httpx

from ..models.endpoint import Endpoint, AuthMethod, HTTPMethod


try:
    from .ai import AIAnalyzer, AIModel
    HAS_AI = True
except ImportError:
    HAS_AI = False


class AnalysisDepth(Enum):
    """Depth of API analysis."""
    SHALLOW = "shallow"  # Basic endpoint detection
    STANDARD = "standard"  # Endpoint + auth detection
    DEEP = "deep"  # Full analysis with response patterns
    SMART = "smart"  # AI-powered analysis


@dataclass
class AnalysisResult:
    """Results from API analysis."""
    base_url: str
    endpoints: list[Endpoint] = field(default_factory=list)
    auth_methods: list[AuthMethod] = field(default_factory=list)
    rate_limits: Optional[dict[str, Any]] = None
    response_formats: list[str] = field(default_factory=list)
    api_version: Optional[str] = None
    documentation_url: Optional[str] = None
    
    @property
    def endpoint_count(self) -> int:
        return len(self.endpoints)
    
    def get_endpoints_by_method(self, method: HTTPMethod) -> list[Endpoint]:
        """Get all endpoints that support a specific HTTP method."""
        return [ep for ep in self.endpoints if method in ep.methods]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert analysis result to dictionary."""
        return {
            "base_url": self.base_url,
            "endpoints": [ep.to_dict() for ep in self.endpoints],
            "auth_methods": [am.value for am in self.auth_methods],
            "rate_limits": self.rate_limits,
            "response_formats": self.response_formats,
            "api_version": self.api_version,
            "documentation_url": self.documentation_url,
        }


class APIAnalyzer:
    """
    Analyzes APIs to understand their structure and usage patterns.
    
    This is the brain of API-ARM - it figures out how an API works
    so we can make proper requests to it.
    """
    
    # Common API documentation paths to check
    COMMON_DOC_PATHS = [
        "/docs",
        "/api/docs",
        "/swagger",
        "/swagger.json",
        "/openapi.json",
        "/api-docs",
        "/v1/docs",
        "/v2/docs",
    ]
    
    # Common API version patterns
    VERSION_PATTERNS = [
        r"/v(\d+)/",
        r"/api/v(\d+)/",
        r"version[=:]?\s*[\"']?(\d+\.?\d*)[\"']?",
    ]
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the API analyzer.
        
        Args:
            base_url: The base URL of the API to analyze
            headers: Optional headers to include in requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
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
                "APIAnalyzer must be used as an async context manager. "
                "Use 'async with APIAnalyzer(...) as analyzer:'"
            )
        return self._client
    
    async def analyze(
        self,
        depth: AnalysisDepth = AnalysisDepth.STANDARD,
    ) -> AnalysisResult:
        """
        Perform API analysis.
        
        Args:
            depth: How deep to analyze the API
            
        Returns:
            AnalysisResult containing discovered information
        """
        result = AnalysisResult(base_url=self.base_url)
        
        # Try to find API documentation
        doc_info = await self._find_documentation()
        if doc_info:
            result.documentation_url = doc_info.get("url")
            if "endpoints" in doc_info:
                result.endpoints = doc_info["endpoints"]
                
        # Detect API version
        result.api_version = await self._detect_version()
        
        # Detect authentication methods
        result.auth_methods = await self._detect_auth_methods()
        
        # Detect response formats
        result.response_formats = await self._detect_response_formats()
        
        # Rate limits (Deep analysis)
        if depth in [AnalysisDepth.DEEP, AnalysisDepth.SMART]:
            result.rate_limits = await self._detect_rate_limits()

        # AI Analysis (Smart mode or fallback if no endpoints found)
        should_use_ai = depth == AnalysisDepth.SMART or (not result.endpoints and depth != AnalysisDepth.SHALLOW)
        
        if should_use_ai and HAS_AI:
            # Check for GITHUB_TOKEN inside AIAnalyzer init, but checking here avoids noise
            if "GITHUB_TOKEN" in os.environ:
                 # Fetch root content for AI context
                 try:
                    root_response = await self.client.get("/")
                    content_snippet = root_response.text[:2000]
                    
                    try:
                        ai = AIAnalyzer()
                        ai_endpoints = ai.discover_endpoints(self.base_url, content_snippet)
                        if ai_endpoints:
                            # Merge inferred endpoints
                            existing_paths = {e.path for e in result.endpoints}
                            for ep in ai_endpoints:
                                if ep.path not in existing_paths:
                                    result.endpoints.append(ep)
                    except ValueError:
                         # Token missing handled by AIAnalyzer but we double check
                         pass
                    except Exception:
                        pass # AI fail shouldn't crash main tool
                 except Exception:
                     pass
            
        return result
    
    async def _find_documentation(self) -> Optional[dict[str, Any]]:
        """Try to find API documentation (OpenAPI/Swagger)."""
        for path in self.COMMON_DOC_PATHS:
            try:
                response = await self.client.get(path)
                if response.status_code == 200:
                    # Check if it's JSON (OpenAPI spec)
                    if "application/json" in response.headers.get("content-type", ""):
                        spec = response.json()
                        return await self._parse_openapi_spec(spec, path)
                    # Could be HTML documentation
                    return {"url": f"{self.base_url}{path}"}
            except Exception:
                continue
        return None
    
    async def _parse_openapi_spec(
        self,
        spec: dict[str, Any],
        path: str,
    ) -> dict[str, Any]:
        """Parse an OpenAPI specification to extract endpoints."""
        result: dict[str, Any] = {
            "url": f"{self.base_url}{path}",
            "endpoints": [],
        }
        
        paths = spec.get("paths", {})
        for endpoint_path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint = Endpoint(
                        path=endpoint_path,
                        methods=[HTTPMethod(method.upper())],
                        description=details.get("summary", ""),
                        parameters=self._extract_parameters(details),
                        requires_auth="security" in details or "security" in spec,
                    )
                    result["endpoints"].append(endpoint)
                    
        return result
    
    def _extract_parameters(self, details: dict[str, Any]) -> dict[str, Any]:
        """Extract parameters from OpenAPI endpoint details."""
        params: dict[str, Any] = {
            "query": [],
            "path": [],
            "body": None,
        }
        
        for param in details.get("parameters", []):
            param_info = {
                "name": param.get("name"),
                "required": param.get("required", False),
                "type": param.get("schema", {}).get("type", "string"),
            }
            if param.get("in") == "query":
                params["query"].append(param_info)
            elif param.get("in") == "path":
                params["path"].append(param_info)
                
        # Handle request body
        if "requestBody" in details:
            params["body"] = details["requestBody"]
            
        return params
    
    async def _detect_version(self) -> Optional[str]:
        """Detect the API version from URL or responses."""
        # Check URL for version pattern
        for pattern in self.VERSION_PATTERNS:
            match = re.search(pattern, self.base_url)
            if match:
                return match.group(1)
                
        # Try to get version from root endpoint
        try:
            response = await self.client.get("/")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "version" in data:
                        return str(data["version"])
                except Exception:
                    pass
        except Exception:
            pass
            
        return None
    
    async def _detect_auth_methods(self) -> list[AuthMethod]:
        """Detect what authentication methods the API supports."""
        methods: list[AuthMethod] = []
        
        try:
            # Make a request without auth and check the response
            response = await self.client.get("/")
            
            # Check WWW-Authenticate header
            www_auth = response.headers.get("www-authenticate", "").lower()
            if "bearer" in www_auth:
                methods.append(AuthMethod.BEARER)
            if "basic" in www_auth:
                methods.append(AuthMethod.BASIC)
            if "oauth" in www_auth:
                methods.append(AuthMethod.OAUTH2)
                
            # Check for API key patterns in documentation
            if response.status_code == 401:
                body = response.text.lower()
                if "api key" in body or "apikey" in body or "x-api-key" in body:
                    methods.append(AuthMethod.API_KEY)
                    
        except Exception:
            pass
            
        return methods if methods else [AuthMethod.NONE]
    
    async def _detect_response_formats(self) -> list[str]:
        """Detect what response formats the API supports."""
        formats: list[str] = []
        
        try:
            response = await self.client.get("/")
            content_type = response.headers.get("content-type", "")
            
            if "json" in content_type:
                formats.append("application/json")
            if "xml" in content_type:
                formats.append("application/xml")
            if "html" in content_type:
                formats.append("text/html")
                
        except Exception:
            pass
            
        return formats if formats else ["application/json"]
    
    async def _detect_rate_limits(self) -> Optional[dict[str, Any]]:
        """Detect rate limiting information from API responses."""
        try:
            response = await self.client.get("/")
            
            rate_limit_info: dict[str, Any] = {}
            
            # Common rate limit headers
            headers_to_check = [
                ("x-ratelimit-limit", "limit"),
                ("x-ratelimit-remaining", "remaining"),
                ("x-ratelimit-reset", "reset"),
                ("retry-after", "retry_after"),
            ]
            
            for header, key in headers_to_check:
                if header in response.headers:
                    rate_limit_info[key] = response.headers[header]
                    
            return rate_limit_info if rate_limit_info else None
            
        except Exception:
            return None
