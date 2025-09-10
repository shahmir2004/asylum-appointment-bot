"""
Web user model for authentication and authorization.
Supports role-based access control with developer and user roles.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""
    DEVELOPER = "developer"
    USER = "user"


class WebUser(Base):
    """
    Web user model for authentication and authorization.
    
    Supports two roles:
    - Developer: Full access to bot control, user management, and system configuration
    - User: Limited access to monitoring and basic bot status
    """
    __tablename__ = "web_users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Role-based access control
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Security fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sessions = relationship("WebSession", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<WebUser(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name or email if name not provided."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.email.split('@')[0]  # Use email username as fallback
    
    @property
    def is_developer(self) -> bool:
        """Check if user has developer role."""
        return self.role == UserRole.DEVELOPER
    
    @property
    def is_user(self) -> bool:
        """Check if user has user role."""
        return self.role == UserRole.USER
    
    @property
    def is_account_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.account_locked_until is None:
            return False
        return datetime.utcnow() < self.account_locked_until
    
    def can_access_bot_control(self) -> bool:
        """Check if user can control bot (start/stop)."""
        return self.is_developer and self.is_active and not self.is_account_locked
    
    def can_access_user_management(self) -> bool:
        """Check if user can manage other users."""
        return self.is_developer and self.is_active and not self.is_account_locked
    
    def can_access_system_config(self) -> bool:
        """Check if user can modify system configuration."""
        return self.is_developer and self.is_active and not self.is_account_locked
    
    def can_view_logs(self) -> bool:
        """Check if user can view bot logs."""
        return self.is_active and not self.is_account_locked
    
    def can_view_statistics(self) -> bool:
        """Check if user can view bot statistics."""
        return self.is_active and not self.is_account_locked
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
        self.failed_login_attempts = 0  # Reset failed attempts on successful login
    
    def increment_failed_login(self) -> None:
        """Increment failed login attempts and lock account if necessary."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def unlock_account(self) -> None:
        """Unlock the user account."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert user to dictionary for API responses.
        
        Args:
            include_sensitive: Whether to include sensitive fields (for admin use)
            
        Returns:
            dict: User data dictionary
        """
        data = {
            "id": self.id,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "permissions": {
                "can_access_bot_control": self.can_access_bot_control(),
                "can_access_user_management": self.can_access_user_management(),
                "can_access_system_config": self.can_access_system_config(),
                "can_view_logs": self.can_view_logs(),
                "can_view_statistics": self.can_view_statistics()
            }
        }
        
        if include_sensitive:
            data.update({
                "failed_login_attempts": self.failed_login_attempts,
                "account_locked_until": self.account_locked_until.isoformat() if self.account_locked_until else None,
                "password_changed_at": self.password_changed_at.isoformat() if self.password_changed_at else None,
                "is_account_locked": self.is_account_locked
            })
        
        return data
