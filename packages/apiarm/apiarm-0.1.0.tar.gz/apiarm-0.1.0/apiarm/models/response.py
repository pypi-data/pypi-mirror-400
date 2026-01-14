"""
Response Model - Represents an API response.
"""

from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class APIResponse:
    """
    Represents an API response.
    
    Attributes:
        success: Whether the request was successful (2xx or 3xx status)
        status_code: HTTP status code
        headers: Response headers
        data: Parsed JSON data (if response was JSON)
        text: Raw text response (if not JSON)
        error: Error message if request failed
        request_time: Time taken for the request
        timestamp: When the response was received
    """
    success: bool
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    data: Optional[dict[str, Any]] = None
    text: Optional[str] = None
    error: Optional[str] = None
    request_time: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_json(self) -> bool:
        """Check if the response contains JSON data."""
        return self.data is not None
    
    @property
    def content(self) -> Any:
        """Get the response content (data or text)."""
        return self.data if self.data is not None else self.text
    
    @property
    def is_client_error(self) -> bool:
        """Check if this is a client error (4xx)."""
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        """Check if this is a server error (5xx)."""
        return 500 <= self.status_code < 600
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the response data."""
        if self.data and isinstance(self.data, dict):
            return self.data.get(key, default)
        return default
    
    def __getitem__(self, key: str) -> Any:
        """Access response data by key."""
        if self.data and isinstance(self.data, dict):
            return self.data[key]
        raise KeyError(f"Response has no data or key '{key}' not found")
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in response data."""
        if self.data and isinstance(self.data, dict):
            return key in self.data
        return False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "success": self.success,
            "status_code": self.status_code,
            "headers": self.headers,
            "data": self.data,
            "text": self.text,
            "error": self.error,
            "request_time": self.request_time,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def raise_for_status(self) -> None:
        """Raise an exception if the request failed."""
        if not self.success:
            error_msg = self.error or f"Request failed with status {self.status_code}"
            raise APIResponseError(error_msg, self)
    
    def __repr__(self) -> str:
        status = "success" if self.success else "failed"
        return f"APIResponse(status={self.status_code}, {status})"


class APIResponseError(Exception):
    """Exception raised when an API request fails."""
    
    def __init__(self, message: str, response: APIResponse):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code
