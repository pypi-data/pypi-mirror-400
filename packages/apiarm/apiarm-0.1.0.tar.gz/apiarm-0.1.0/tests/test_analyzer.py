"""
Tests for the API Analyzer module.
"""

import pytest
from apiarm.core.analyzer import APIAnalyzer, AnalysisResult, AnalysisDepth
from apiarm.models.endpoint import AuthMethod


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""
    
    def test_create_result(self):
        result = AnalysisResult(base_url="https://api.example.com")
        assert result.base_url == "https://api.example.com"
        assert result.endpoints == []
        assert result.endpoint_count == 0
        
    def test_to_dict(self):
        result = AnalysisResult(
            base_url="https://api.example.com",
            api_version="1.0",
            auth_methods=[AuthMethod.BEARER],
        )
        data = result.to_dict()
        assert data["base_url"] == "https://api.example.com"
        assert data["api_version"] == "1.0"
        assert "bearer" in data["auth_methods"]


class TestAPIAnalyzer:
    """Tests for APIAnalyzer class."""
    
    def test_init(self):
        analyzer = APIAnalyzer("https://api.example.com")
        assert analyzer.base_url == "https://api.example.com"
        assert analyzer.timeout == 30.0
        
    def test_init_strips_trailing_slash(self):
        analyzer = APIAnalyzer("https://api.example.com/")
        assert analyzer.base_url == "https://api.example.com"
        
    def test_common_doc_paths(self):
        assert "/docs" in APIAnalyzer.COMMON_DOC_PATHS
        assert "/swagger.json" in APIAnalyzer.COMMON_DOC_PATHS
        assert "/openapi.json" in APIAnalyzer.COMMON_DOC_PATHS
