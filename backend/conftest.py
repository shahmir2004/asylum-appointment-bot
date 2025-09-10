"""
Pytest configuration for backend tests.
"""
import pytest
import sys
import os

# Add the backend src directory to Python path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, "src")
sys.path.insert(0, src_dir)


@pytest.fixture(scope="session")
def test_app():
    """Create test FastAPI application instance."""
    from src.main import create_app
    return create_app()


@pytest.fixture
def test_settings():
    """Provide test-specific settings."""
    from src.config import Settings
    
    return Settings(
        environment="testing",
        database_url="sqlite:///./test_asylum_bot.db",
        secret_key="test_secret_key_for_testing_only",
        debug=True
    )
