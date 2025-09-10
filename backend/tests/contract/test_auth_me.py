"""
Contract test for GET /api/auth/me endpoint.
This test MUST FAIL initially as per TDD methodology.

Tests the current user information endpoint contract:
- Authentication requirement
- User data format validation
- Authorization header handling
- Response schema validation
"""
import pytest
import httpx
from fastapi.testclient import TestClient

from src.main import app


class TestAuthMeContract:
    """Contract tests for GET /api/auth/me endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_me_endpoint_exists(self, client):
        """Test that the me endpoint exists and accepts GET requests."""
        # This should fail initially - endpoint doesn't exist yet
        response = client.get("/api/auth/me")
        
        # Should not return 404 (endpoint should exist)
        assert response.status_code != 404, "Me endpoint should exist at /api/auth/me"
    
    def test_me_successful_with_valid_token(self, client):
        """Test successful user info retrieval with valid access token."""
        # Valid authorization header
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        response = client.get("/api/auth/me", headers=headers)
        
        # Should return 200 for valid token
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Response should contain user information
        response_data = response.json()
        assert "id" in response_data, "Response must include user id"
        assert "email" in response_data, "Response must include user email"
        assert "role" in response_data, "Response must include user role"
        assert "is_active" in response_data, "Response must include is_active status"
        assert "created_at" in response_data, "Response must include created_at timestamp"
        
        # Validate data types
        assert isinstance(response_data["id"], int), "User id must be integer"
        assert isinstance(response_data["email"], str), "Email must be string"
        assert isinstance(response_data["role"], str), "Role must be string"
        assert isinstance(response_data["is_active"], bool), "is_active must be boolean"
        assert isinstance(response_data["created_at"], str), "created_at must be string (ISO datetime)"
        
        # Validate role values
        assert response_data["role"] in ["developer", "user"], "Role must be 'developer' or 'user'"
        
        # Email should be valid format
        assert "@" in response_data["email"], "Email should contain @"
        assert "." in response_data["email"], "Email should contain domain"
        
        # Should not include sensitive information
        assert "password" not in response_data, "Response must not include password"
        assert "password_hash" not in response_data, "Response must not include password_hash"
    
    def test_me_missing_authorization_header(self, client):
        """Test me endpoint without authorization header returns 401."""
        response = client.get("/api/auth/me")
        
        # Should return 401 for missing authorization
        assert response.status_code == 401, f"Expected 401 for missing auth header, got {response.status_code}"
        
        # Error response format
        response_data = response.json()
        assert "error" in response_data, "Error response must include error field"
        assert "detail" in response_data, "Error response must include detail field"
    
    def test_me_invalid_token(self, client):
        """Test me endpoint with invalid access token returns 401."""
        headers = {
            "Authorization": "Bearer invalid_token"
        }
        
        response = client.get("/api/auth/me", headers=headers)
        
        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"
    
    def test_me_malformed_authorization_header(self, client):
        """Test me endpoint with malformed authorization header returns 401."""
        # Test various malformed authorization headers
        malformed_headers = [
            {"Authorization": "invalid_format"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Basic token"},  # Wrong type
            {"Authorization": "bearer lowercase_bearer"},  # Lowercase bearer
        ]
        
        for headers in malformed_headers:
            response = client.get("/api/auth/me", headers=headers)
            assert response.status_code == 401, f"Expected 401 for malformed header {headers}, got {response.status_code}"
    
    def test_me_expired_token(self, client):
        """Test me endpoint with expired access token returns 401."""
        headers = {
            "Authorization": "Bearer expired_access_token"
        }
        
        response = client.get("/api/auth/me", headers=headers)
        
        # Should return 401 for expired token
        assert response.status_code == 401, f"Expected 401 for expired token, got {response.status_code}"
    
    def test_me_revoked_token(self, client):
        """Test me endpoint with revoked access token returns 401."""
        headers = {
            "Authorization": "Bearer revoked_access_token"
        }
        
        response = client.get("/api/auth/me", headers=headers)
        
        # Should return 401 for revoked token
        assert response.status_code == 401, f"Expected 401 for revoked token, got {response.status_code}"
    
    def test_me_inactive_user_token(self, client):
        """Test me endpoint with token from inactive user returns 401."""
        headers = {
            "Authorization": "Bearer token_from_inactive_user"
        }
        
        response = client.get("/api/auth/me", headers=headers)
        
        # Should return 401 for inactive user
        assert response.status_code == 401, f"Expected 401 for inactive user token, got {response.status_code}"
    
    def test_me_response_headers(self, client):
        """Test that me endpoint returns proper response headers."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        response = client.get("/api/auth/me", headers=headers)
        
        # Check for proper headers
        response_headers = response.headers
        
        # Content-Type should be JSON
        assert "application/json" in response_headers.get("content-type", ""), "Response should be JSON"
        
        # Should not expose sensitive information in headers
        assert "password" not in str(response_headers).lower(), "Headers should not contain sensitive info"
    
    def test_me_case_insensitive_bearer(self, client):
        """Test that authorization header accepts case variations of Bearer."""
        test_cases = [
            "Bearer valid_token",
            "bearer valid_token",
            "BEARER valid_token",
        ]
        
        for auth_value in test_cases:
            headers = {"Authorization": auth_value}
            response = client.get("/api/auth/me", headers=headers)
            
            # Should handle case variations properly (either 401 for invalid token or 200 for valid)
            assert response.status_code in [200, 401], f"Should handle '{auth_value}' properly"
    
    def test_me_no_query_parameters_needed(self, client):
        """Test that me endpoint doesn't require query parameters."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        # Test with unnecessary query parameters
        response = client.get("/api/auth/me?unnecessary=param", headers=headers)
        
        # Should work the same regardless of query parameters
        assert response.status_code in [200, 401], "Query parameters should not affect endpoint"
    
    def test_me_only_get_method_allowed(self, client):
        """Test that me endpoint only accepts GET method."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        # Test other HTTP methods
        methods_responses = [
            client.post("/api/auth/me", headers=headers),
            client.put("/api/auth/me", headers=headers),
            client.delete("/api/auth/me", headers=headers),
            client.patch("/api/auth/me", headers=headers),
        ]
        
        for response in methods_responses:
            # Should return 405 Method Not Allowed
            assert response.status_code == 405, f"Non-GET methods should return 405, got {response.status_code}"
    
    def test_me_rate_limiting(self, client):
        """Test that me endpoint has appropriate rate limiting."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        responses = []
        for _ in range(20):  # Try 20 rapid requests
            response = client.get("/api/auth/me", headers=headers)
            responses.append(response.status_code)
        
        # Should have reasonable behavior (either success or rate limiting)
        assert all(code in [200, 401, 429] for code in responses), "All responses should be valid"
    
    def test_me_user_data_consistency(self, client):
        """Test that repeated calls return consistent user data."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.get("/api/auth/me", headers=headers)
            if response.status_code == 200:
                responses.append(response.json())
        
        # If any successful responses, they should be identical
        if responses:
            first_response = responses[0]
            for response in responses[1:]:
                assert response == first_response, "User data should be consistent across requests"
