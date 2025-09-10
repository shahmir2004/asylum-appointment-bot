"""
Database models for the icpBot web interface.

This module contains all SQLAlchemy models for the web application,
including user management, session tracking, activity logging, and
bot status monitoring.
"""

from .web_user import WebUser, UserRole
from .web_session import WebSession
from .activity_log import ActivityLog, ActivityType, ActivitySeverity
from .bot_status import BotStatus, BotState, MonitoringMode, BotHealth

# Export all models and enums
__all__ = [
    # Models
    "WebUser",
    "WebSession", 
    "ActivityLog",
    "BotStatus",
    
    # Enums
    "UserRole",
    "ActivityType",
    "ActivitySeverity", 
    "BotState",
    "MonitoringMode",
    "BotHealth"
]
