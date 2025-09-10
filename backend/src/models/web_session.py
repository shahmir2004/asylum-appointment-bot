"""
Web session model for authentication tracking.
Manages JWT tokens, refresh tokens, and session lifecycle.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from ..database import Base


class WebSession(Base):
    """
    Web session model for tracking user authentication sessions.
    
    Manages JWT tokens, refresh tokens, and provides session security features
    including token rotation, expiration tracking, and device information.
    """
    __tablename__ = "web_sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("web_users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token information
    access_token_jti = Column(String(255), unique=True, nullable=False, index=True)  # JWT ID for access token
    refresh_token_jti = Column(String(255), unique=True, nullable=False, index=True)  # JWT ID for refresh token
    
    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Device and location information
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Supports both IPv4 and IPv6
    device_fingerprint = Column(String(255), nullable=True)
    
    # Security information
    login_method = Column(String(50), default="password", nullable=False)  # password, refresh_token
    security_flags = Column(String(255), nullable=True)  # JSON string for additional security data
    
    # Relationship
    user = relationship("WebUser", back_populates="sessions")
    
    def __repr__(self) -> str:
        """String representation of the session."""
        return f"<WebSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"
    
    @classmethod
    def create_session(
        cls,
        user_id: int,
        access_token_jti: str,
        refresh_token_jti: str,
        expires_in_seconds: int = 1800,  # 30 minutes default
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        login_method: str = "password"
    ) -> "WebSession":
        """
        Create a new web session.
        
        Args:
            user_id: ID of the user
            access_token_jti: JWT ID for access token
            refresh_token_jti: JWT ID for refresh token
            expires_in_seconds: Session expiration time in seconds
            user_agent: Browser user agent string
            ip_address: Client IP address
            device_fingerprint: Device fingerprint for security
            login_method: Method used for login
            
        Returns:
            WebSession: New session instance
        """
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        
        return cls(
            user_id=user_id,
            access_token_jti=access_token_jti,
            refresh_token_jti=refresh_token_jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
            login_method=login_method
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is valid (active, not revoked, not expired)."""
        return self.is_active and not self.is_revoked and not self.is_expired
    
    @property
    def time_until_expiry(self) -> Optional[timedelta]:
        """Get time remaining until session expires."""
        if self.is_expired:
            return None
        return self.expires_at - datetime.utcnow()
    
    @property
    def session_duration(self) -> timedelta:
        """Get total session duration."""
        return self.last_used_at - self.created_at
    
    def update_last_used(self) -> None:
        """Update last used timestamp."""
        self.last_used_at = datetime.utcnow()
    
    def extend_session(self, additional_seconds: int = 1800) -> None:
        """
        Extend session expiration time.
        
        Args:
            additional_seconds: Additional time to add to session
        """
        self.expires_at = datetime.utcnow() + timedelta(seconds=additional_seconds)
        self.update_last_used()
    
    def revoke_session(self, reason: str = "manual_revocation") -> None:
        """
        Revoke the session.
        
        Args:
            reason: Reason for revocation
        """
        self.is_active = False
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()
        
        # Store revocation reason in security flags
        import json
        try:
            flags = json.loads(self.security_flags or '{}')
        except (json.JSONDecodeError, TypeError):
            flags = {}
        
        flags['revocation_reason'] = reason
        flags['revoked_at'] = datetime.utcnow().isoformat()
        self.security_flags = json.dumps(flags)
    
    def rotate_tokens(self, new_access_jti: str, new_refresh_jti: str) -> None:
        """
        Rotate session tokens for security.
        
        Args:
            new_access_jti: New access token JTI
            new_refresh_jti: New refresh token JTI
        """
        self.access_token_jti = new_access_jti
        self.refresh_token_jti = new_refresh_jti
        self.update_last_used()
    
    def is_suspicious_activity(self, current_ip: str, current_user_agent: str) -> bool:
        """
        Check for suspicious activity based on IP and user agent changes.
        
        Args:
            current_ip: Current request IP address
            current_user_agent: Current request user agent
            
        Returns:
            bool: True if activity seems suspicious
        """
        # Check for IP address change
        ip_changed = self.ip_address and self.ip_address != current_ip
        
        # Check for significant user agent change
        user_agent_changed = self.user_agent and self.user_agent != current_user_agent
        
        # Simple heuristic: both IP and user agent changed
        return ip_changed and user_agent_changed
    
    def add_security_flag(self, flag_name: str, flag_value: any) -> None:
        """
        Add a security flag to the session.
        
        Args:
            flag_name: Name of the security flag
            flag_value: Value of the security flag
        """
        import json
        
        try:
            flags = json.loads(self.security_flags or '{}')
        except (json.JSONDecodeError, TypeError):
            flags = {}
        
        flags[flag_name] = flag_value
        self.security_flags = json.dumps(flags)
    
    def get_security_flag(self, flag_name: str, default=None) -> any:
        """
        Get a security flag value.
        
        Args:
            flag_name: Name of the security flag
            default: Default value if flag doesn't exist
            
        Returns:
            Security flag value or default
        """
        import json
        
        try:
            flags = json.loads(self.security_flags or '{}')
            return flags.get(flag_name, default)
        except (json.JSONDecodeError, TypeError):
            return default
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert session to dictionary for API responses.
        
        Args:
            include_sensitive: Whether to include sensitive fields
            
        Returns:
            dict: Session data dictionary
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "login_method": self.login_method,
            "ip_address": self.ip_address,
            "is_expired": self.is_expired,
            "is_valid": self.is_valid,
            "session_duration_seconds": int(self.session_duration.total_seconds()) if self.session_duration else 0
        }
        
        if include_sensitive:
            data.update({
                "access_token_jti": self.access_token_jti,
                "refresh_token_jti": self.refresh_token_jti,
                "is_revoked": self.is_revoked,
                "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
                "user_agent": self.user_agent,
                "device_fingerprint": self.device_fingerprint,
                "security_flags": self.security_flags
            })
        
        return data
