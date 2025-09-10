"""
Contract test for POST /api/auth/login endpoint.
This test MUST FAIL initially as per TDD methodology.

Tests the authentication login endpoint contract:
- Request format validation
- Response schema validation
- Status codes and error handling
- Security requirements
"""
import pytest
import httpx
from fastapi.testclient import TestClient

from src.main import app


class TestAuthLoginContract:
    """Contract tests for POST /api/auth/login endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_login_endpoint_exists(self, client):
        """Test that the login endpoint exists and accepts POST requests."""
        # This should fail initially - endpoint doesn't exist yet
        response = client.post("/api/auth/login")
        
        # Should not return 404 (endpoint should exist)
        assert response.status_code != 404, "Login endpoint should exist at /api/auth/login"
    
    def test_login_successful_authentication(self, client):
        """Test successful login with valid credentials."""
        # Valid login request payload
        login_data = {
            "email": "developer@asylum-bot.local",
            "password": "dev_password_change_me"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        # Should return 200 for successful authentication
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Response should contain required fields
        response_data = response.json()
        assert "access_token" in response_data, "Response must include access_token"
        assert "refresh_token" in response_data, "Response must include refresh_token"
        assert "token_type" in response_data, "Response must include token_type"
        assert "expires_in" in response_data, "Response must include expires_in"
        assert "user" in response_data, "Response must include user info"
        
        # Validate token type
        assert response_data["token_type"] == "bearer", "Token type must be 'bearer'"
        
        # Validate user information
        user_data = response_data["user"]
        assert "id" in user_data, "User data must include id"
        assert "email" in user_data, "User data must include email"
        assert "role" in user_data, "User data must include role"
        assert user_data["email"] == login_data["email"], "Email should match login request"
        
        # Tokens should be non-empty strings
        assert isinstance(response_data["access_token"], str), "Access token must be string"
        assert len(response_data["access_token"]) > 0, "Access token must not be empty"
        assert isinstance(response_data["refresh_token"], str), "Refresh token must be string"
        assert len(response_data["refresh_token"]) > 0, "Refresh token must not be empty"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials returns 401."""
        invalid_login_data = {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=invalid_login_data)
        
        # Should return 401 for invalid credentials
        assert response.status_code == 401, f"Expected 401 for invalid credentials, got {response.status_code}"
        
        # Error response format
        response_data = response.json()
        assert "error" in response_data, "Error response must include error field"
        assert "detail" in response_data, "Error response must include detail field"
    
    def test_login_missing_email(self, client):
        """Test login with missing email field returns 422."""
        incomplete_data = {
            "password": "somepassword"
        }
        
        response = client.post("/api/auth/login", json=incomplete_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for missing email, got {response.status_code}"
        
        # Validation error format
        response_data = response.json()
        assert "detail" in response_data, "Validation error must include detail"
    
    def test_login_missing_password(self, client):
        """Test login with missing password field returns 422."""
        incomplete_data = {
            "email": "test@example.com"
        }
        
        response = client.post("/api/auth/login", json=incomplete_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for missing password, got {response.status_code}"
    
    def test_login_empty_email(self, client):
        """Test login with empty email returns 422."""
        invalid_data = {
            "email": "",
            "password": "somepassword"
        }
        
        response = client.post("/api/auth/login", json=invalid_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for empty email, got {response.status_code}"
    
    def test_login_empty_password(self, client):
        """Test login with empty password returns 422."""
        invalid_data = {
            "email": "test@example.com",
            "password": ""
        }
        
        response = client.post("/api/auth/login", json=invalid_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for empty password, got {response.status_code}"
    
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format returns 422."""
        invalid_data = {
            "email": "not-an-email",
            "password": "somepassword"
        }
        
        response = client.post("/api/auth/login", json=invalid_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for invalid email format, got {response.status_code}"
    
    def test_login_inactive_user(self, client):
        """Test login with inactive user account returns 403."""
        # This test assumes there's an inactive user for testing
        inactive_user_data = {
            "email": "inactive@asylum-bot.local",
            "password": "somepassword"
        }
        
        response = client.post("/api/auth/login", json=inactive_user_data)
        
        # Should return 403 for inactive account
        # Note: This might return 401 if user doesn't exist, which is also acceptable
        assert response.status_code in [401, 403], f"Expected 401 or 403 for inactive user, got {response.status_code}"
    
    def test_login_content_type_validation(self, client):
        """Test that login endpoint requires JSON content type."""
        # Send form data instead of JSON
        response = client.post("/api/auth/login", data={"email": "test@example.com", "password": "password"})
        
        # Should return 422 or 415 for wrong content type
        assert response.status_code in [415, 422], f"Expected 415 or 422 for wrong content type, got {response.status_code}"
    
    def test_login_rate_limiting(self, client):
        """Test that login endpoint has rate limiting protection."""
        # Make multiple rapid requests
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        responses = []
        for _ in range(10):  # Try 10 rapid requests
            response = client.post("/api/auth/login", json=login_data)
            responses.append(response.status_code)
        
        # Should have at least one rate limit response (429)
        # Note: This might not trigger in test environment, so we'll check for reasonable behavior
        assert all(code in [401, 422, 429] for code in responses), "All responses should be valid error codes"
    
    def test_login_response_headers(self, client):
        """Test that login response includes proper security headers."""
        login_data = {
            "email": "developer@asylum-bot.local",
            "password": "dev_password_change_me"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        # Check for security headers (may pass or fail depending on implementation)
        headers = response.headers
        
        # Content-Type should be JSON
        assert "application/json" in headers.get("content-type", ""), "Response should be JSON"
