"""
Tests for the Endpoint model.
"""

import pytest
from apiarm.models.endpoint import Endpoint, HTTPMethod, AuthMethod


class TestHTTPMethod:
    """Tests for HTTPMethod enum."""
    
    def test_methods_exist(self):
        assert HTTPMethod.GET.value == "GET"
        assert HTTPMethod.POST.value == "POST"
        assert HTTPMethod.PUT.value == "PUT"
        assert HTTPMethod.PATCH.value == "PATCH"
        assert HTTPMethod.DELETE.value == "DELETE"


class TestAuthMethod:
    """Tests for AuthMethod enum."""
    
    def test_methods_exist(self):
        assert AuthMethod.NONE.value == "none"
        assert AuthMethod.API_KEY.value == "api_key"
        assert AuthMethod.BEARER.value == "bearer"
        assert AuthMethod.BASIC.value == "basic"
        assert AuthMethod.OAUTH2.value == "oauth2"


class TestEndpoint:
    """Tests for Endpoint model."""
    
    def test_create_endpoint(self):
        endpoint = Endpoint(path="/users")
        assert endpoint.path == "/users"
        assert HTTPMethod.GET in endpoint.methods
        
    def test_path_parameters(self):
        endpoint = Endpoint(path="/users/{id}/posts/{post_id}")
        params = endpoint.path_parameters
        assert "id" in params
        assert "post_id" in params
        assert endpoint.has_path_parameters
        
    def test_no_path_parameters(self):
        endpoint = Endpoint(path="/users")
        assert endpoint.path_parameters == []
        assert not endpoint.has_path_parameters
        
    def test_matches_path(self):
        endpoint = Endpoint(path="/users/{id}")
        assert endpoint.matches_path("/users/123")
        assert endpoint.matches_path("/users/abc")
        assert not endpoint.matches_path("/posts/123")
        
    def test_build_path(self):
        endpoint = Endpoint(path="/users/{id}/posts/{post_id}")
        path = endpoint.build_path(id="123", post_id="456")
        assert path == "/users/123/posts/456"
        
    def test_to_dict(self):
        endpoint = Endpoint(
            path="/users",
            methods=[HTTPMethod.GET, HTTPMethod.POST],
            description="User management",
            requires_auth=True,
        )
        data = endpoint.to_dict()
        assert data["path"] == "/users"
        assert "GET" in data["methods"]
        assert "POST" in data["methods"]
        assert data["requires_auth"] is True
        
    def test_from_dict(self):
        data = {
            "path": "/users",
            "methods": ["GET", "POST"],
            "description": "User management",
        }
        endpoint = Endpoint.from_dict(data)
        assert endpoint.path == "/users"
        assert HTTPMethod.GET in endpoint.methods
        assert HTTPMethod.POST in endpoint.methods
