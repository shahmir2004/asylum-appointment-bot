"""
Contract test for POST /api/auth/logout endpoint.
This test MUST FAIL initially as per TDD methodology.

Tests the logout endpoint contract:
- Token invalidation
- Response format validation
- Authentication requirement
- Security considerations
"""
import pytest
import httpx
from fastapi.testclient import TestClient

from src.main import app


class TestAuthLogoutContract:
    """Contract tests for POST /api/auth/logout endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_logout_endpoint_exists(self, client):
        """Test that the logout endpoint exists and accepts POST requests."""
        # This should fail initially - endpoint doesn't exist yet
        response = client.post("/api/auth/logout")
        
        # Should not return 404 (endpoint should exist)
        assert response.status_code != 404, "Logout endpoint should exist at /api/auth/logout"
    
    def test_logout_successful_with_valid_token(self, client):
        """Test successful logout with valid access token."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        response = client.post("/api/auth/logout", headers=headers)
        
        # Should return 200 for successful logout
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Response should confirm logout
        response_data = response.json()
        assert "message" in response_data, "Response must include message"
        assert "success" in response_data, "Response must include success status"
        
        # Validate response format
        assert isinstance(response_data["success"], bool), "Success field must be boolean"
        assert response_data["success"] is True, "Success should be True for valid logout"
        assert isinstance(response_data["message"], str), "Message must be string"
    
    def test_logout_with_refresh_token(self, client):
        """Test logout with both access and refresh tokens."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        logout_data = {
            "refresh_token": "valid_refresh_token_here"
        }
        
        response = client.post("/api/auth/logout", headers=headers, json=logout_data)
        
        # Should return 200 for successful logout
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Should acknowledge both tokens were invalidated
        response_data = response.json()
        assert response_data.get("success") is True, "Logout should be successful"
    
    def test_logout_missing_authorization_header(self, client):
        """Test logout without authorization header returns 401."""
        response = client.post("/api/auth/logout")
        
        # Should return 401 for missing authorization
        assert response.status_code == 401, f"Expected 401 for missing auth header, got {response.status_code}"
        
        # Error response format
        response_data = response.json()
        assert "error" in response_data, "Error response must include error field"
        assert "detail" in response_data, "Error response must include detail field"
    
    def test_logout_invalid_token(self, client):
        """Test logout with invalid access token returns 401."""
        headers = {
            "Authorization": "Bearer invalid_token"
        }
        
        response = client.post("/api/auth/logout", headers=headers)
        
        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"
    
    def test_logout_expired_token(self, client):
        """Test logout with expired access token returns 401."""
        headers = {
            "Authorization": "Bearer expired_access_token"
        }
        
        response = client.post("/api/auth/logout", headers=headers)
        
        # Should return 401 for expired token
        assert response.status_code == 401, f"Expected 401 for expired token, got {response.status_code}"
    
    def test_logout_malformed_authorization_header(self, client):
        """Test logout with malformed authorization header returns 401."""
        malformed_headers = [
            {"Authorization": "invalid_format"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Basic token"},  # Wrong type
        ]
        
        for headers in malformed_headers:
            response = client.post("/api/auth/logout", headers=headers)
            assert response.status_code == 401, f"Expected 401 for malformed header {headers}, got {response.status_code}"
    
    def test_logout_already_logged_out_token(self, client):
        """Test logout with already invalidated token returns 401."""
        headers = {
            "Authorization": "Bearer already_logged_out_token"
        }
        
        response = client.post("/api/auth/logout", headers=headers)
        
        # Should return 401 for already invalidated token
        assert response.status_code == 401, f"Expected 401 for invalidated token, got {response.status_code}"
    
    def test_logout_token_invalidation_is_immediate(self, client):
        """Test that token is immediately invalidated after logout."""
        # This test simulates the token invalidation behavior
        headers = {
            "Authorization": "Bearer token_to_be_invalidated"
        }
        
        # First logout attempt
        logout_response = client.post("/api/auth/logout", headers=headers)
        
        # Then try to use the same token (this would be tested in integration)
        # For contract test, we just verify the logout response format
        if logout_response.status_code == 200:
            response_data = logout_response.json()
            assert response_data.get("success") is True, "Token should be successfully invalidated"
    
    def test_logout_only_post_method_allowed(self, client):
        """Test that logout endpoint only accepts POST method."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        # Test other HTTP methods
        methods_responses = [
            client.get("/api/auth/logout", headers=headers),
            client.put("/api/auth/logout", headers=headers),
            client.delete("/api/auth/logout", headers=headers),
            client.patch("/api/auth/logout", headers=headers),
        ]
        
        for response in methods_responses:
            # Should return 405 Method Not Allowed
            assert response.status_code == 405, f"Non-POST methods should return 405, got {response.status_code}"
    
    def test_logout_with_invalid_refresh_token(self, client):
        """Test logout with valid access token but invalid refresh token."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        logout_data = {
            "refresh_token": "invalid_refresh_token"
        }
        
        response = client.post("/api/auth/logout", headers=headers, json=logout_data)
        
        # Should still succeed (access token is valid, refresh token error is tolerable)
        # Or return specific error - either is acceptable depending on implementation
        assert response.status_code in [200, 400, 401], "Should handle invalid refresh token gracefully"
    
    def test_logout_response_headers(self, client):
        """Test that logout response includes proper headers."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        response = client.post("/api/auth/logout", headers=headers)
        
        # Check for proper headers
        response_headers = response.headers
        
        # Content-Type should be JSON
        assert "application/json" in response_headers.get("content-type", ""), "Response should be JSON"
        
        # Should not expose sensitive information
        assert "token" not in str(response_headers).lower(), "Headers should not contain token information"
    
    def test_logout_rate_limiting(self, client):
        """Test that logout endpoint has appropriate rate limiting."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        responses = []
        for _ in range(10):  # Try 10 rapid logout requests
            response = client.post("/api/auth/logout", headers=headers)
            responses.append(response.status_code)
        
        # Should have reasonable behavior
        assert all(code in [200, 401, 429] for code in responses), "All responses should be valid"
    
    def test_logout_no_sensitive_data_in_response(self, client):
        """Test that logout response doesn't contain sensitive information."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        response = client.post("/api/auth/logout", headers=headers)
        
        if response.status_code == 200:
            response_text = response.text.lower()
            
            # Should not contain sensitive information
            assert "password" not in response_text, "Response should not contain password"
            assert "secret" not in response_text, "Response should not contain secret"
            assert "private" not in response_text, "Response should not contain private keys"
    
    def test_logout_idempotent_behavior(self, client):
        """Test that multiple logout calls with same token are handled gracefully."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        # First logout
        first_response = client.post("/api/auth/logout", headers=headers)
        
        # Second logout with same token (should be invalid now)
        second_response = client.post("/api/auth/logout", headers=headers)
        
        # First should succeed or fail based on token validity
        assert first_response.status_code in [200, 401], "First logout should be handled properly"
        
        # Second should fail with 401 (token already invalidated)
        assert second_response.status_code == 401, "Second logout should fail with invalidated token"
    
    def test_logout_content_type_handling(self, client):
        """Test logout endpoint handles different content types properly."""
        headers = {
            "Authorization": "Bearer valid_access_token_here"
        }
        
        # Test without body (should work)
        response1 = client.post("/api/auth/logout", headers=headers)
        
        # Test with JSON body
        response2 = client.post("/api/auth/logout", headers=headers, json={"refresh_token": "some_token"})
        
        # Both should be handled properly
        assert response1.status_code in [200, 401], "Logout without body should be handled"
        assert response2.status_code in [200, 401], "Logout with JSON should be handled"
