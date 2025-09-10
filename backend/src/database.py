"""
Database configuration and initialization for the web API.
Handles SQLAlchemy setup and database lifecycle management.
"""
import asyncio
from typing import AsyncGenerator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
import structlog

from .config import get_settings


# Create SQLAlchemy base class
Base = declarative_base()

# Metadata for table creation
metadata = MetaData()

# Database engines (will be initialized in init_database)
sync_engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None

logger = structlog.get_logger()


def init_sync_database():
    """Initialize synchronous database connection."""
    global sync_engine, SessionLocal
    
    settings = get_settings()
    
    # Create synchronous engine
    sync_engine = create_engine(
        settings.database_url_sync,
        echo=settings.database_echo,
        pool_pre_ping=True,  # Verify connections before use
    )
    
    # Create session factory
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine
    )
    
    logger.info("Synchronous database initialized", url=settings.database_url_sync)
    return sync_engine


def init_async_database():
    """Initialize asynchronous database connection."""
    global async_engine, AsyncSessionLocal
    
    settings = get_settings()
    
    # Create asynchronous engine
    async_engine = create_async_engine(
        settings.database_url_async,
        echo=settings.database_echo,
        pool_pre_ping=True,
    )
    
    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logger.info("Asynchronous database initialized", url=settings.database_url_async)
    return async_engine


async def init_database():
    """
    Initialize database connections and create tables.
    Called during application startup.
    """
    try:
        # Initialize both sync and async connections
        init_sync_database()
        init_async_database()
        
        # Create all tables
        # Note: In production, use Alembic migrations instead
        async with async_engine.begin() as conn:
            # Import all models to ensure they're registered
            from .models import web_user, web_session, activity_log, bot_status
            
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables created successfully")
        
        # Create default users if they don't exist
        await create_default_users()
        
    except Exception as e:
        logger.error("Failed to initialize database", exc_info=e)
        raise


async def create_default_users():
    """Create default developer and user accounts if they don't exist."""
    try:
        from .models.web_user import WebUser
        from .auth.password_service import hash_password
        
        settings = get_settings()
        
        async with get_async_db() as db:
            # Check if users already exist
            developer_exists = await db.query(WebUser).filter(
                WebUser.email == settings.default_developer_email
            ).first()
            
            user_exists = await db.query(WebUser).filter(
                WebUser.email == settings.default_user_email
            ).first()
            
            # Create developer account
            if not developer_exists:
                developer = WebUser(
                    email=settings.default_developer_email,
                    password_hash=hash_password(settings.default_developer_password),
                    role="developer",
                    is_active=True
                )
                db.add(developer)
                logger.info("Created default developer account", email=settings.default_developer_email)
            
            # Create user account
            if not user_exists:
                user = WebUser(
                    email=settings.default_user_email,
                    password_hash=hash_password(settings.default_user_password),
                    role="user",
                    is_active=True
                )
                db.add(user)
                logger.info("Created default user account", email=settings.default_user_email)
            
            await db.commit()
            
    except Exception as e:
        logger.warning("Failed to create default users", exc_info=e)
        # Don't fail startup if user creation fails


def get_sync_db():
    """
    Get synchronous database session.
    
    Yields:
        Session: SQLAlchemy session
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get asynchronous database session.
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dependency for FastAPI route injection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session injection.
    
    Yields:
        AsyncSession: Database session for request handling
    """
    async for session in get_async_db():
        yield session


async def close_database():
    """
    Close database connections.
    Called during application shutdown.
    """
    global sync_engine, async_engine
    
    try:
        if async_engine:
            await async_engine.dispose()
            logger.info("Async database connection closed")
        
        if sync_engine:
            sync_engine.dispose()
            logger.info("Sync database connection closed")
            
    except Exception as e:
        logger.error("Error closing database connections", exc_info=e)
