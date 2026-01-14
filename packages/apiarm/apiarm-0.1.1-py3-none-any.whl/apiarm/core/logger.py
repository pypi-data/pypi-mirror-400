"""
Request Logger - Logs all API requests and responses for debugging and analysis.

Features:
- Console logging with Rich formatting
- File logging in JSON format
- Request/response timing
- Sensitive data masking
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..models.response import APIResponse


class LogLevel(Enum):
    """Log levels for request logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class RequestLog:
    """Represents a logged request/response pair."""
    timestamp: str
    method: str
    url: str
    path: str
    request_headers: dict[str, str] = field(default_factory=dict)
    request_body: Optional[dict[str, Any]] = None
    response_status: int = 0
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body: Optional[Any] = None
    duration_ms: float = 0.0
    success: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class RequestLogger:
    """
    Logs API requests and responses.
    
    Supports both console output (with Rich formatting) and
    file output (JSON format for later analysis).
    """
    
    # Headers that should be masked in logs
    SENSITIVE_HEADERS = [
        "authorization",
        "x-api-key",
        "api-key",
        "token",
        "cookie",
        "set-cookie",
    ]
    
    def __init__(
        self,
        console_output: bool = True,
        file_output: Optional[Path] = None,
        log_level: LogLevel = LogLevel.INFO,
        mask_sensitive: bool = True,
    ):
        """
        Initialize the request logger.
        
        Args:
            console_output: Whether to print to console
            file_output: Path to log file (JSON lines format)
            log_level: Minimum log level to record
            mask_sensitive: Whether to mask sensitive headers
        """
        self.console_output = console_output
        self.file_output = file_output
        self.log_level = log_level
        self.mask_sensitive = mask_sensitive
        self.console = Console()
        self._logs: list[RequestLog] = []
        
    def start_request(
        self,
        method: str,
        url: str,
        path: str,
        headers: dict[str, str],
        body: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Begin logging a request. Returns context for end_request.
        
        Args:
            method: HTTP method
            url: Full URL
            path: Endpoint path
            headers: Request headers
            body: Request body
            
        Returns:
            Context dictionary to pass to end_request
        """
        return {
            "start_time": time.time(),
            "method": method,
            "url": url,
            "path": path,
            "headers": self._mask_headers(headers) if self.mask_sensitive else headers,
            "body": body,
        }
        
    def end_request(
        self,
        context: dict[str, Any],
        response: APIResponse,
    ) -> RequestLog:
        """
        Complete logging a request with its response.
        
        Args:
            context: Context from start_request
            response: The API response
            
        Returns:
            The completed RequestLog
        """
        duration_ms = (time.time() - context["start_time"]) * 1000
        
        log = RequestLog(
            timestamp=datetime.now().isoformat(),
            method=context["method"],
            url=context["url"],
            path=context["path"],
            request_headers=context["headers"],
            request_body=context["body"],
            response_status=response.status_code,
            response_headers=self._mask_headers(response.headers) if self.mask_sensitive else response.headers,
            response_body=response.data or response.text,
            duration_ms=round(duration_ms, 2),
            success=response.success,
            error=response.error,
        )
        
        self._logs.append(log)
        
        # Output
        if self.console_output:
            self._print_log(log)
        if self.file_output:
            self._write_log(log)
            
        return log
    
    def _mask_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Mask sensitive header values."""
        masked = {}
        for key, value in headers.items():
            if key.lower() in self.SENSITIVE_HEADERS:
                masked[key] = self._mask_value(value)
            else:
                masked[key] = value
        return masked
    
    def _mask_value(self, value: str, visible: int = 4) -> str:
        """Mask a sensitive value."""
        if len(value) <= visible:
            return "*" * len(value)
        return value[:visible] + "*" * min(len(value) - visible, 20)
    
    def _print_log(self, log: RequestLog) -> None:
        """Print log to console with Rich formatting."""
        status_color = "green" if log.success else "red"
        status_icon = "✓" if log.success else "✗"
        
        self.console.print(
            f"[bold blue]{log.method}[/bold blue] "
            f"[dim]{log.path}[/dim] "
            f"[{status_color}]{status_icon} {log.response_status}[/{status_color}] "
            f"[dim]({log.duration_ms}ms)[/dim]"
        )
        
    def _write_log(self, log: RequestLog) -> None:
        """Write log to file in JSON lines format."""
        if self.file_output:
            with open(self.file_output, "a") as f:
                f.write(json.dumps(log.to_dict()) + "\n")
                
    def get_logs(self) -> list[RequestLog]:
        """Get all logged requests."""
        return self._logs.copy()
    
    def get_stats(self) -> dict[str, Any]:
        """Get statistics about logged requests."""
        if not self._logs:
            return {"total": 0}
            
        successful = sum(1 for log in self._logs if log.success)
        durations = [log.duration_ms for log in self._logs]
        
        return {
            "total": len(self._logs),
            "successful": successful,
            "failed": len(self._logs) - successful,
            "success_rate": round(successful / len(self._logs) * 100, 1),
            "avg_duration_ms": round(sum(durations) / len(durations), 2),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
        }
    
    def print_summary(self) -> None:
        """Print a summary of all logged requests."""
        stats = self.get_stats()
        
        if stats["total"] == 0:
            self.console.print("[yellow]No requests logged[/yellow]")
            return
            
        table = Table(title="Request Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Requests", str(stats["total"]))
        table.add_row("Successful", str(stats["successful"]))
        table.add_row("Failed", str(stats["failed"]))
        table.add_row("Success Rate", f"{stats['success_rate']}%")
        table.add_row("Avg Duration", f"{stats['avg_duration_ms']}ms")
        table.add_row("Min Duration", f"{stats['min_duration_ms']}ms")
        table.add_row("Max Duration", f"{stats['max_duration_ms']}ms")
        
        self.console.print(table)
        
    def clear(self) -> None:
        """Clear all logged requests."""
        self._logs.clear()
