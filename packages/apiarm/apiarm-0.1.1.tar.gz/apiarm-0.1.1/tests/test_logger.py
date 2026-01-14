"""
Tests for the Request Logger module.
"""

import pytest
from apiarm.core.logger import RequestLogger, RequestLog, LogLevel
from apiarm.models.response import APIResponse


class TestRequestLog:
    """Tests for RequestLog dataclass."""
    
    def test_create_log(self):
        log = RequestLog(
            timestamp="2024-01-01T00:00:00",
            method="GET",
            url="https://api.example.com/users",
            path="/users",
            response_status=200,
            success=True,
        )
        assert log.method == "GET"
        assert log.success is True
        
    def test_to_dict(self):
        log = RequestLog(
            timestamp="2024-01-01T00:00:00",
            method="POST",
            url="https://api.example.com/users",
            path="/users",
            response_status=201,
            duration_ms=150.5,
            success=True,
        )
        data = log.to_dict()
        assert data["method"] == "POST"
        assert data["duration_ms"] == 150.5


class TestRequestLogger:
    """Tests for RequestLogger class."""
    
    def test_init(self):
        logger = RequestLogger()
        assert logger.console_output is True
        assert logger.mask_sensitive is True
        
    def test_mask_headers(self):
        logger = RequestLogger()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer secret-token-12345",
            "X-API-Key": "my-secret-key",
        }
        masked = logger._mask_headers(headers)
        assert masked["Content-Type"] == "application/json"
        assert "secret" not in masked["Authorization"]
        assert masked["Authorization"].startswith("Bear")
        
    def test_get_logs_empty(self):
        logger = RequestLogger(console_output=False)
        assert logger.get_logs() == []
        
    def test_get_stats_empty(self):
        logger = RequestLogger(console_output=False)
        stats = logger.get_stats()
        assert stats["total"] == 0
        
    def test_logging_flow(self):
        logger = RequestLogger(console_output=False)
        
        # Start a request
        context = logger.start_request(
            method="GET",
            url="https://api.example.com/users",
            path="/users",
            headers={"Authorization": "Bearer token"},
        )
        
        # Create a mock response
        response = APIResponse(
            success=True,
            status_code=200,
            data={"users": []},
        )
        
        # End the request
        log = logger.end_request(context, response)
        
        assert log.method == "GET"
        assert log.success is True
        assert log.response_status == 200
        assert len(logger.get_logs()) == 1
        
    def test_clear(self):
        logger = RequestLogger(console_output=False)
        context = logger.start_request("GET", "url", "/path", {})
        response = APIResponse(success=True, status_code=200)
        logger.end_request(context, response)
        
        assert len(logger.get_logs()) == 1
        logger.clear()
        assert len(logger.get_logs()) == 0
