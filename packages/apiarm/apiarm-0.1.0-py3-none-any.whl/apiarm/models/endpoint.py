"""
Endpoint Model - Represents an API endpoint.
"""

import re
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthMethod(Enum):
    """Authentication methods."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


@dataclass
class Endpoint:
    """
    Represents an API endpoint.
    
    Attributes:
        path: The URL path (may contain path parameters like /users/{id})
        methods: HTTP methods this endpoint supports
        description: Human-readable description
        parameters: Parameter definitions (query, path, body)
        requires_auth: Whether authentication is required
        rate_limit: Rate limit info if known
        response_schema: Expected response structure
    """
    path: str
    methods: list[HTTPMethod] = field(default_factory=lambda: [HTTPMethod.GET])
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_auth: bool = False
    rate_limit: Optional[dict[str, Any]] = None
    response_schema: Optional[dict[str, Any]] = None
    
    # Regex pattern for matching path parameters
    _PATH_PARAM_PATTERN = re.compile(r"\{([^}]+)\}")
    
    @property
    def path_parameters(self) -> list[str]:
        """Extract path parameter names from the path."""
        return self._PATH_PARAM_PATTERN.findall(self.path)
    
    @property
    def has_path_parameters(self) -> bool:
        """Check if this endpoint has path parameters."""
        return bool(self.path_parameters)
    
    def matches_path(self, actual_path: str) -> bool:
        """
        Check if an actual path matches this endpoint's pattern.
        
        For example, /users/123 matches /users/{id}
        """
        # Convert path template to regex
        pattern = self._PATH_PARAM_PATTERN.sub(r"([^/]+)", self.path)
        pattern = f"^{pattern}$"
        return bool(re.match(pattern, actual_path))
    
    def build_path(self, **path_params: str) -> str:
        """
        Build the actual path by substituting path parameters.
        
        Args:
            **path_params: Path parameter values
            
        Returns:
            The complete path with substituted values
        """
        result = self.path
        for param_name, param_value in path_params.items():
            result = result.replace(f"{{{param_name}}}", str(param_value))
        return result
    
    def to_dict(self) -> dict[str, Any]:
        """Convert endpoint to dictionary."""
        return {
            "path": self.path,
            "methods": [m.value for m in self.methods],
            "description": self.description,
            "parameters": self.parameters,
            "requires_auth": self.requires_auth,
            "rate_limit": self.rate_limit,
            "response_schema": self.response_schema,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Endpoint":
        """Create endpoint from dictionary."""
        methods = [HTTPMethod(m) for m in data.get("methods", ["GET"])]
        return cls(
            path=data["path"],
            methods=methods,
            description=data.get("description", ""),
            parameters=data.get("parameters", {}),
            requires_auth=data.get("requires_auth", False),
            rate_limit=data.get("rate_limit"),
            response_schema=data.get("response_schema"),
        )
    
    def __repr__(self) -> str:
        methods_str = ", ".join(m.value for m in self.methods)
        return f"Endpoint(path='{self.path}', methods=[{methods_str}])"
