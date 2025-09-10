"""
Activity log model for tracking user actions and system events.
Provides comprehensive audit trail and monitoring capabilities.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from ..database import Base


class ActivityType(str, Enum):
    """Activity types for categorizing logged actions."""
    
    # Authentication activities
    LOGIN = "login"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    LOGIN_FAILED = "login_failed"
    SESSION_EXPIRED = "session_expired"
    PASSWORD_CHANGE = "password_change"
    
    # Bot control activities
    BOT_START = "bot_start"
    BOT_STOP = "bot_stop"
    BOT_STATUS_CHECK = "bot_status_check"
    BOT_CONFIG_UPDATE = "bot_config_update"
    BOT_FORCE_STOP = "bot_force_stop"
    
    # Monitoring activities
    OFFICE_CHECK = "office_check"
    SLOT_FOUND = "slot_found"
    BOOKING_ATTEMPT = "booking_attempt"
    BOOKING_SUCCESS = "booking_success"
    BOOKING_FAILED = "booking_failed"
    
    # System activities
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_ERROR = "system_error"
    SYSTEM_MAINTENANCE = "system_maintenance"
    
    # User management (developer only)
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ROLE_CHANGED = "user_role_changed"
    
    # Data activities
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    LOGS_VIEWED = "logs_viewed"
    LOGS_CLEARED = "logs_cleared"
    
    # Configuration activities
    CONFIG_UPDATED = "config_updated"
    PROXY_UPDATED = "proxy_updated"
    NOTIFICATION_SENT = "notification_sent"
    
    # Security activities
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    PERMISSION_DENIED = "permission_denied"


class ActivitySeverity(str, Enum):
    """Severity levels for activities."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ActivityLog(Base):
    """
    Activity log model for comprehensive audit trail and monitoring.
    
    Tracks all user actions, system events, and bot activities with
    detailed context and metadata for analysis and debugging.
    """
    __tablename__ = "activity_logs"
    
    # Create composite index for efficient querying
    __table_args__ = (
        Index('idx_activity_user_type_timestamp', 'user_id', 'activity_type', 'timestamp'),
        Index('idx_activity_type_timestamp', 'activity_type', 'timestamp'),
        Index('idx_activity_severity_timestamp', 'severity', 'timestamp'),
        Index('idx_activity_session_timestamp', 'session_id', 'timestamp'),
    )
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("web_users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(Integer, ForeignKey("web_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Activity information
    activity_type = Column(String(50), nullable=False, index=True)  # ActivityType enum value
    severity = Column(String(20), default=ActivitySeverity.INFO, nullable=False, index=True)
    
    # Description and details
    description = Column(String(500), nullable=False)  # Brief description
    details = Column(Text, nullable=True)  # Detailed information (JSON or text)
    
    # Context information
    ip_address = Column(String(45), nullable=True)  # Client IP address
    user_agent = Column(Text, nullable=True)  # Browser/client information
    endpoint = Column(String(255), nullable=True)  # API endpoint accessed
    method = Column(String(10), nullable=True)  # HTTP method
    
    # Request/Response information
    request_id = Column(String(100), nullable=True, index=True)  # Correlation ID
    response_status = Column(Integer, nullable=True)  # HTTP status code
    response_time_ms = Column(Integer, nullable=True)  # Response time in milliseconds
    
    # Metadata
    metadata = Column(Text, nullable=True)  # Additional JSON metadata
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Status flags
    is_sensitive = Column(Boolean, default=False, nullable=False)  # Contains sensitive data
    is_system_generated = Column(Boolean, default=False, nullable=False)  # System vs user action
    
    # Relationships
    user = relationship("WebUser", back_populates="activity_logs")
    session = relationship("WebSession")
    
    def __repr__(self) -> str:
        """String representation of the activity log."""
        return f"<ActivityLog(id={self.id}, type={self.activity_type}, user_id={self.user_id})>"
    
    @classmethod
    def log_activity(
        cls,
        activity_type: ActivityType,
        description: str,
        user_id: Optional[int] = None,
        session_id: Optional[int] = None,
        severity: ActivitySeverity = ActivitySeverity.INFO,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
        response_status: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_sensitive: bool = False,
        is_system_generated: bool = False
    ) -> "ActivityLog":
        """
        Create a new activity log entry.
        
        Args:
            activity_type: Type of activity
            description: Brief description of the activity
            user_id: ID of the user performing the action
            session_id: ID of the session
            severity: Severity level of the activity
            details: Detailed information about the activity
            ip_address: Client IP address
            user_agent: Client user agent
            endpoint: API endpoint accessed
            method: HTTP method used
            request_id: Request correlation ID
            response_status: HTTP response status
            response_time_ms: Response time in milliseconds
            metadata: Additional metadata dictionary
            is_sensitive: Whether the log contains sensitive data
            is_system_generated: Whether this is a system-generated log
            
        Returns:
            ActivityLog: New activity log instance
        """
        import json
        
        # Convert metadata to JSON string if provided
        metadata_json = None
        if metadata:
            try:
                metadata_json = json.dumps(metadata, default=str)
            except (TypeError, ValueError):
                metadata_json = str(metadata)
        
        return cls(
            activity_type=activity_type.value,
            description=description,
            user_id=user_id,
            session_id=session_id,
            severity=severity.value,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            request_id=request_id,
            response_status=response_status,
            response_time_ms=response_time_ms,
            metadata=metadata_json,
            is_sensitive=is_sensitive,
            is_system_generated=is_system_generated
        )
    
    @classmethod
    def log_authentication(
        cls,
        activity_type: ActivityType,
        user_id: Optional[int],
        session_id: Optional[int],
        ip_address: str,
        user_agent: str,
        success: bool,
        details: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> "ActivityLog":
        """
        Log authentication-related activities.
        
        Args:
            activity_type: Authentication activity type
            user_id: ID of the user
            session_id: ID of the session
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether the authentication was successful
            details: Additional details
            request_id: Request correlation ID
            
        Returns:
            ActivityLog: New activity log entry
        """
        severity = ActivitySeverity.INFO if success else ActivitySeverity.WARNING
        
        return cls.log_activity(
            activity_type=activity_type,
            description=f"Authentication {activity_type.value}: {'success' if success else 'failed'}",
            user_id=user_id,
            session_id=session_id,
            severity=severity,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            is_sensitive=True
        )
    
    @classmethod
    def log_bot_activity(
        cls,
        activity_type: ActivityType,
        description: str,
        user_id: Optional[int] = None,
        session_id: Optional[int] = None,
        success: bool = True,
        details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> "ActivityLog":
        """
        Log bot-related activities.
        
        Args:
            activity_type: Bot activity type
            description: Description of the activity
            user_id: ID of the user who triggered the action
            session_id: ID of the session
            success: Whether the activity was successful
            details: Additional details
            metadata: Additional metadata
            request_id: Request correlation ID
            
        Returns:
            ActivityLog: New activity log entry
        """
        severity = ActivitySeverity.INFO if success else ActivitySeverity.ERROR
        
        return cls.log_activity(
            activity_type=activity_type,
            description=description,
            user_id=user_id,
            session_id=session_id,
            severity=severity,
            details=details,
            metadata=metadata,
            request_id=request_id,
            is_system_generated=user_id is None
        )
    
    @classmethod
    def log_system_event(
        cls,
        activity_type: ActivityType,
        description: str,
        severity: ActivitySeverity = ActivitySeverity.INFO,
        details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ActivityLog":
        """
        Log system events.
        
        Args:
            activity_type: System activity type
            description: Description of the event
            severity: Severity level
            details: Additional details
            metadata: Additional metadata
            
        Returns:
            ActivityLog: New activity log entry
        """
        return cls.log_activity(
            activity_type=activity_type,
            description=description,
            severity=severity,
            details=details,
            metadata=metadata,
            is_system_generated=True
        )
    
    @classmethod
    def log_security_event(
        cls,
        activity_type: ActivityType,
        description: str,
        user_id: Optional[int] = None,
        session_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None,
        severity: ActivitySeverity = ActivitySeverity.WARNING,
        request_id: Optional[str] = None
    ) -> "ActivityLog":
        """
        Log security-related events.
        
        Args:
            activity_type: Security activity type
            description: Description of the event
            user_id: ID of the user involved
            session_id: ID of the session
            ip_address: Client IP address
            user_agent: Client user agent
            details: Additional details
            severity: Severity level
            request_id: Request correlation ID
            
        Returns:
            ActivityLog: New activity log entry
        """
        return cls.log_activity(
            activity_type=activity_type,
            description=description,
            user_id=user_id,
            session_id=session_id,
            severity=severity,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            is_sensitive=True
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata as dictionary.
        
        Returns:
            dict: Metadata dictionary
        """
        if not self.metadata:
            return {}
        
        try:
            import json
            return json.loads(self.metadata)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the log entry.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        import json
        
        metadata = self.get_metadata()
        metadata[key] = value
        
        try:
            self.metadata = json.dumps(metadata, default=str)
        except (TypeError, ValueError):
            self.metadata = json.dumps({key: str(value)})
    
    @property
    def activity_type_enum(self) -> ActivityType:
        """Get activity type as enum."""
        try:
            return ActivityType(self.activity_type)
        except ValueError:
            return ActivityType.SYSTEM_ERROR  # Default for unknown types
    
    @property
    def severity_enum(self) -> ActivitySeverity:
        """Get severity as enum."""
        try:
            return ActivitySeverity(self.severity)
        except ValueError:
            return ActivitySeverity.INFO  # Default for unknown severities
    
    @property
    def is_authentication_activity(self) -> bool:
        """Check if this is an authentication-related activity."""
        auth_types = {
            ActivityType.LOGIN,
            ActivityType.LOGOUT,
            ActivityType.TOKEN_REFRESH,
            ActivityType.LOGIN_FAILED,
            ActivityType.SESSION_EXPIRED,
            ActivityType.PASSWORD_CHANGE
        }
        return self.activity_type_enum in auth_types
    
    @property
    def is_bot_activity(self) -> bool:
        """Check if this is a bot-related activity."""
        bot_types = {
            ActivityType.BOT_START,
            ActivityType.BOT_STOP,
            ActivityType.BOT_STATUS_CHECK,
            ActivityType.BOT_CONFIG_UPDATE,
            ActivityType.BOT_FORCE_STOP,
            ActivityType.OFFICE_CHECK,
            ActivityType.SLOT_FOUND,
            ActivityType.BOOKING_ATTEMPT,
            ActivityType.BOOKING_SUCCESS,
            ActivityType.BOOKING_FAILED
        }
        return self.activity_type_enum in bot_types
    
    @property
    def is_security_activity(self) -> bool:
        """Check if this is a security-related activity."""
        security_types = {
            ActivityType.SUSPICIOUS_ACTIVITY,
            ActivityType.ACCOUNT_LOCKED,
            ActivityType.ACCOUNT_UNLOCKED,
            ActivityType.PERMISSION_DENIED,
            ActivityType.LOGIN_FAILED
        }
        return self.activity_type_enum in security_types
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert activity log to dictionary for API responses.
        
        Args:
            include_sensitive: Whether to include sensitive fields
            
        Returns:
            dict: Activity log data dictionary
        """
        data = {
            "id": self.id,
            "activity_type": self.activity_type,
            "severity": self.severity,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_system_generated": self.is_system_generated,
            "user_id": self.user_id,
            "response_status": self.response_status,
            "response_time_ms": self.response_time_ms,
            "metadata": self.get_metadata()
        }
        
        if include_sensitive:
            data.update({
                "session_id": self.session_id,
                "details": self.details,
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "endpoint": self.endpoint,
                "method": self.method,
                "request_id": self.request_id,
                "is_sensitive": self.is_sensitive
            })
        
        return data
