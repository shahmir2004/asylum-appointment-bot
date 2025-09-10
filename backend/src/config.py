"""
Backend configuration settings using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # ================================
    # Application Configuration
    # ================================
    app_name: str = "Asylum Appointment Bot API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # ================================
    # Server Configuration
    # ================================
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    reload: bool = True
    
    # ================================
    # Database Configuration
    # ================================
    database_url: str = "sqlite:///./asylum_bot_web.db"
    database_echo: bool = False
    
    # ================================
    # Security Configuration
    # ================================
    secret_key: str = "change_me_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # ================================
    # CORS Configuration
    # ================================
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: List[str] = ["*"]
    
    # ================================
    # Default Users
    # ================================
    default_developer_email: str = "developer@asylum-bot.local"
    default_developer_password: str = "dev_password_change_me"
    default_user_email: str = "user@asylum-bot.local"
    default_user_password: str = "user_password_change_me"
    
    # ================================
    # Bot Integration
    # ================================
    bot_project_path: str = "../src"
    bot_log_path: str = "../logs"
    bot_database_path: str = "../asylum_bot.db"
    
    # ================================
    # WebSocket Configuration
    # ================================
    ws_heartbeat_interval: int = 30
    ws_max_connections: int = 100
    
    # ================================
    # Logging Configuration
    # ================================
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "backend/logs/web_api.log"
    
    # ================================
    # Rate Limiting
    # ================================
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # ================================
    # File Upload
    # ================================
    max_upload_size_mb: int = 10
    upload_path: str = "backend/uploads"
    
    # ================================
    # External Services
    # ================================
    sentry_dsn: Optional[str] = None
    prometheus_metrics_port: Optional[int] = None
    
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins from environment variable."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_methods", pre=True)
    def parse_allowed_methods(cls, v):
        """Parse comma-separated methods from environment variable."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Ensure secret key is set in production."""
        if v == "change_me_in_production":
            import warnings
            warnings.warn(
                "Using default secret key! Generate a secure key for production.",
                UserWarning
            )
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for SQLAlchemy."""
        return self.database_url
    
    @property
    def database_url_async(self) -> str:
        """Get asynchronous database URL for async SQLAlchemy."""
        if self.database_url.startswith("sqlite"):
            return self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
        return self.database_url
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings (dependency injection for FastAPI)."""
    return settings
