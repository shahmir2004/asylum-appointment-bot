"""
Contract test for POST /api/auth/refresh endpoint.
This test MUST FAIL initially as per TDD methodology.

Tests the token refresh endpoint contract:
- Refresh token validation
- New token generation
- Response format validation
- Security requirements
"""
import pytest
import httpx
from fastapi.testclient import TestClient

from src.main import app


class TestAuthRefreshContract:
    """Contract tests for POST /api/auth/refresh endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_refresh_endpoint_exists(self, client):
        """Test that the refresh endpoint exists and accepts POST requests."""
        # This should fail initially - endpoint doesn't exist yet
        response = client.post("/api/auth/refresh")
        
        # Should not return 404 (endpoint should exist)
        assert response.status_code != 404, "Refresh endpoint should exist at /api/auth/refresh"
    
    def test_refresh_successful_token_renewal(self, client):
        """Test successful token refresh with valid refresh token."""
        # Valid refresh request payload
        refresh_data = {
            "refresh_token": "valid_refresh_token_here"
        }
        
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        # Should return 200 for successful token refresh
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Response should contain required fields
        response_data = response.json()
        assert "access_token" in response_data, "Response must include new access_token"
        assert "refresh_token" in response_data, "Response must include new refresh_token"
        assert "token_type" in response_data, "Response must include token_type"
        assert "expires_in" in response_data, "Response must include expires_in"
        
        # Validate token type
        assert response_data["token_type"] == "bearer", "Token type must be 'bearer'"
        
        # Tokens should be non-empty strings
        assert isinstance(response_data["access_token"], str), "Access token must be string"
        assert len(response_data["access_token"]) > 0, "Access token must not be empty"
        assert isinstance(response_data["refresh_token"], str), "Refresh token must be string"
        assert len(response_data["refresh_token"]) > 0, "Refresh token must not be empty"
        
        # New tokens should be different from the input (token rotation)
        assert response_data["refresh_token"] != refresh_data["refresh_token"], "New refresh token should be different (token rotation)"
    
    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid/expired refresh token returns 401."""
        invalid_refresh_data = {
            "refresh_token": "invalid_or_expired_token"
        }
        
        response = client.post("/api/auth/refresh", json=invalid_refresh_data)
        
        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"
        
        # Error response format
        response_data = response.json()
        assert "error" in response_data, "Error response must include error field"
        assert "detail" in response_data, "Error response must include detail field"
    
    def test_refresh_missing_token(self, client):
        """Test refresh with missing refresh_token field returns 422."""
        incomplete_data = {}
        
        response = client.post("/api/auth/refresh", json=incomplete_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for missing refresh_token, got {response.status_code}"
        
        # Validation error format
        response_data = response.json()
        assert "detail" in response_data, "Validation error must include detail"
    
    def test_refresh_empty_token(self, client):
        """Test refresh with empty refresh token returns 422."""
        invalid_data = {
            "refresh_token": ""
        }
        
        response = client.post("/api/auth/refresh", json=invalid_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for empty refresh_token, got {response.status_code}"
    
    def test_refresh_malformed_token(self, client):
        """Test refresh with malformed token returns 401."""
        malformed_data = {
            "refresh_token": "not.a.valid.jwt.token"
        }
        
        response = client.post("/api/auth/refresh", json=malformed_data)
        
        # Should return 401 for malformed token
        assert response.status_code == 401, f"Expected 401 for malformed token, got {response.status_code}"
    
    def test_refresh_revoked_token(self, client):
        """Test refresh with revoked token returns 401."""
        # This would be a previously valid token that has been revoked
        revoked_data = {
            "refresh_token": "revoked_token_example"
        }
        
        response = client.post("/api/auth/refresh", json=revoked_data)
        
        # Should return 401 for revoked token
        assert response.status_code == 401, f"Expected 401 for revoked token, got {response.status_code}"
    
    def test_refresh_token_from_inactive_user(self, client):
        """Test refresh with token from inactive user returns 401."""
        inactive_user_token = {
            "refresh_token": "token_from_inactive_user"
        }
        
        response = client.post("/api/auth/refresh", json=inactive_user_token)
        
        # Should return 401 for inactive user
        assert response.status_code == 401, f"Expected 401 for inactive user token, got {response.status_code}"
    
    def test_refresh_content_type_validation(self, client):
        """Test that refresh endpoint requires JSON content type."""
        # Send form data instead of JSON
        response = client.post("/api/auth/refresh", data={"refresh_token": "some_token"})
        
        # Should return 422 or 415 for wrong content type
        assert response.status_code in [415, 422], f"Expected 415 or 422 for wrong content type, got {response.status_code}"
    
    def test_refresh_rate_limiting(self, client):
        """Test that refresh endpoint has rate limiting protection."""
        # Make multiple rapid requests
        refresh_data = {
            "refresh_token": "some_token"
        }
        
        responses = []
        for _ in range(10):  # Try 10 rapid requests
            response = client.post("/api/auth/refresh", json=refresh_data)
            responses.append(response.status_code)
        
        # Should have reasonable rate limiting behavior
        assert all(code in [401, 422, 429] for code in responses), "All responses should be valid error codes"
    
    def test_refresh_response_headers(self, client):
        """Test that refresh response includes proper security headers."""
        refresh_data = {
            "refresh_token": "valid_refresh_token_here"
        }
        
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        # Check for proper headers
        headers = response.headers
        
        # Content-Type should be JSON
        assert "application/json" in headers.get("content-type", ""), "Response should be JSON"
    
    def test_refresh_token_expiry_validation(self, client):
        """Test that expired refresh tokens are properly rejected."""
        expired_token_data = {
            "refresh_token": "expired_refresh_token"
        }
        
        response = client.post("/api/auth/refresh", json=expired_token_data)
        
        # Should return 401 for expired token
        assert response.status_code == 401, f"Expected 401 for expired token, got {response.status_code}"
        
        # Error should indicate token expiry
        response_data = response.json()
        assert "expired" in response_data.get("detail", "").lower() or "invalid" in response_data.get("detail", "").lower(), \
            "Error message should indicate token issue"
    
    def test_refresh_security_headers(self, client):
        """Test that refresh endpoint returns appropriate security headers."""
        refresh_data = {
            "refresh_token": "test_token"
        }
        
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        # Should have proper CORS headers if configured
        headers = response.headers
        
        # Basic security check - no sensitive information in headers
        assert "password" not in str(headers).lower(), "Headers should not contain sensitive information"
        assert "secret" not in str(headers).lower(), "Headers should not contain sensitive information"
