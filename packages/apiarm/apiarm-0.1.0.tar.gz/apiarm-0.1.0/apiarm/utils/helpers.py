"""
Helper utilities for API-ARM.
"""

import json
from typing import Any, Optional
from urllib.parse import urlparse, urlunparse, urljoin, urlencode


def parse_url(url: str) -> dict[str, Any]:
    """
    Parse a URL into its components.
    
    Args:
        url: The URL to parse
        
    Returns:
        Dictionary with URL components
    """
    parsed = urlparse(url)
    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "path": parsed.path,
        "params": parsed.params,
        "query": parsed.query,
        "fragment": parsed.fragment,
        "hostname": parsed.hostname,
        "port": parsed.port,
    }


def build_url(
    base: str,
    path: str = "",
    params: Optional[dict[str, Any]] = None,
) -> str:
    """
    Build a complete URL from components.
    
    Args:
        base: Base URL
        path: Path to append
        params: Query parameters
        
    Returns:
        Complete URL string
    """
    url = urljoin(base, path)
    
    if params:
        # Filter out None values
        filtered_params = {k: v for k, v in params.items() if v is not None}
        if filtered_params:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{urlencode(filtered_params)}"
            
    return url


def merge_headers(
    *header_dicts: Optional[dict[str, str]],
) -> dict[str, str]:
    """
    Merge multiple header dictionaries.
    
    Later dictionaries override earlier ones for duplicate keys.
    
    Args:
        *header_dicts: Header dictionaries to merge
        
    Returns:
        Merged headers dictionary
    """
    result: dict[str, str] = {}
    for headers in header_dicts:
        if headers:
            result.update(headers)
    return result


def safe_json_loads(text: str) -> Optional[dict[str, Any]]:
    """
    Safely parse JSON, returning None on failure.
    
    Args:
        text: JSON string to parse
        
    Returns:
        Parsed JSON or None
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_json_from_response(text: str) -> Optional[dict[str, Any]]:
    """
    Try to extract JSON from a response that might have additional content.
    
    Some APIs return JSON wrapped in other content or with extra text.
    This function tries to find and extract valid JSON.
    
    Args:
        text: Response text
        
    Returns:
        Extracted JSON or None
    """
    # First try direct parse
    result = safe_json_loads(text)
    if result is not None:
        return result
        
    # Try to find JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        result = safe_json_loads(text[start:end])
        if result is not None:
            return result
            
    # Try to find JSON array
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        result = safe_json_loads(text[start:end])
        if result is not None:
            return result
            
    return None


def truncate_string(s: str, max_length: int = 100) -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        s: String to truncate
        max_length: Maximum length
        
    Returns:
        Truncated string with ellipsis if needed
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - 3] + "..."


def format_headers_for_log(headers: dict[str, str]) -> str:
    """
    Format headers for logging, masking sensitive values.
    
    Args:
        headers: Headers dictionary
        
    Returns:
        Formatted string for logging
    """
    sensitive_keys = ["authorization", "x-api-key", "api-key", "token"]
    
    formatted = []
    for key, value in headers.items():
        if key.lower() in sensitive_keys:
            value = mask_value(value)
        formatted.append(f"{key}: {value}")
        
    return "\n".join(formatted)


def mask_value(value: str, visible: int = 4) -> str:
    """Mask a sensitive value, showing only first few characters."""
    if len(value) <= visible:
        return "*" * len(value)
    return value[:visible] + "*" * (len(value) - visible)
