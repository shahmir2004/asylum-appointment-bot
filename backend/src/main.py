"""
FastAPI application factory and configuration.
Main entry point for the Asylum Appointment Bot web API.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from .config import get_settings
from .database import init_database
from .auth.middleware import AuthenticationMiddleware


# Configure structured logging
def configure_logging():
    """Configure structured logging for the application."""
    settings = get_settings()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper()),
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    settings = get_settings()
    logger = structlog.get_logger()
    
    # Startup
    logger.info("Starting Asylum Appointment Bot API", version=app.version)
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Create log directories
        os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
        os.makedirs(settings.upload_path, exist_ok=True)
        
        logger.info("Application startup complete")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down Asylum Appointment Bot API")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    # Configure logging first
    configure_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="REST API for Asylum Appointment Bot with web interface control",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
    )
    
    # Add security middleware
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure properly for production
        )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )
    
    # Add custom authentication middleware (will be implemented later)
    # app.add_middleware(AuthenticationMiddleware)
    
    # Add request/response logging middleware
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Log all HTTP requests and responses."""
        logger = structlog.get_logger()
        
        # Log request
        logger.info(
            "HTTP request",
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            client=request.client.host if request.client else None
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            "HTTP response",
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
        return response
    
    # Add health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint for monitoring and load balancers.
        
        Returns:
            dict: Health status information
        """
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment
        }
    
    # Add root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """
        Root endpoint with API information.
        
        Returns:
            dict: API information
        """
        return {
            "message": "Asylum Appointment Bot API",
            "version": settings.app_version,
            "docs": "/docs" if settings.is_development else "API documentation disabled in production",
            "health": "/health"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Global exception handler for unhandled exceptions.
        
        Args:
            request: The HTTP request
            exc: The unhandled exception
            
        Returns:
            JSONResponse: Error response
        """
        logger = structlog.get_logger()
        logger.error(
            "Unhandled exception",
            exc_info=exc,
            request_url=str(request.url),
            request_method=request.method
        )
        
        if settings.is_development:
            # Show detailed errors in development
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": str(exc),
                    "type": type(exc).__name__
                }
            )
        else:
            # Hide error details in production
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred"
                }
            )
    
    # TODO: Add API routers
    # from .api import auth, bot, users
    # app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    # app.include_router(bot.router, prefix="/api/bot", tags=["Bot Control"])
    # app.include_router(users.router, prefix="/api/users", tags=["User Management"])
    
    # TODO: Add WebSocket endpoints
    # from .websocket import endpoints
    # app.include_router(endpoints.router)
    
    return app


# Create app instance
app = create_app()


def run_dev_server():
    """Run development server with auto-reload."""
    settings = get_settings()
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload and settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    run_dev_server()
