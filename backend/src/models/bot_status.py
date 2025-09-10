"""
Bot status model for real-time status tracking and monitoring.
Manages bot lifecycle, monitoring state, and operational metrics.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import validates

from ..database import Base


class BotState(str, Enum):
    """Bot operational states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class MonitoringMode(str, Enum):
    """Monitoring operational modes."""
    DISABLED = "disabled"
    OFFICE_CHECK = "office_check"
    SLOT_MONITORING = "slot_monitoring"
    BOOKING_READY = "booking_ready"
    AUTO_BOOKING = "auto_booking"


class BotHealth(str, Enum):
    """Bot health status indicators."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class BotStatus(Base):
    """
    Bot status model for comprehensive real-time monitoring.
    
    Tracks bot state, monitoring configuration, performance metrics,
    and provides real-time status updates for the web interface.
    """
    __tablename__ = "bot_status"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Bot identification
    bot_instance_id = Column(String(100), unique=True, nullable=False, index=True)  # Unique bot instance
    
    # Current state
    state = Column(String(20), default=BotState.STOPPED, nullable=False, index=True)
    monitoring_mode = Column(String(30), default=MonitoringMode.DISABLED, nullable=False)
    health_status = Column(String(20), default=BotHealth.UNKNOWN, nullable=False)
    
    # Configuration
    target_office_code = Column(String(20), nullable=True)  # Office being monitored
    monitoring_interval_seconds = Column(Integer, default=300, nullable=False)  # 5 minutes default
    auto_booking_enabled = Column(Boolean, default=False, nullable=False)
    
    # Operational metrics
    last_check_time = Column(DateTime, nullable=True)
    last_success_time = Column(DateTime, nullable=True)
    last_error_time = Column(DateTime, nullable=True)
    total_checks_performed = Column(Integer, default=0, nullable=False)
    total_slots_found = Column(Integer, default=0, nullable=False)
    total_booking_attempts = Column(Integer, default=0, nullable=False)
    successful_bookings = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    average_response_time_ms = Column(Float, nullable=True)
    success_rate_percentage = Column(Float, default=0.0, nullable=False)
    uptime_percentage = Column(Float, default=0.0, nullable=False)
    
    # Current status information
    current_message = Column(String(500), nullable=True)  # Brief status message
    current_details = Column(Text, nullable=True)  # Detailed status information
    last_error_message = Column(String(500), nullable=True)
    last_error_details = Column(Text, nullable=True)
    
    # System information
    process_id = Column(Integer, nullable=True)  # OS process ID
    memory_usage_mb = Column(Float, nullable=True)
    cpu_usage_percentage = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    
    # Configuration JSON for complex settings
    configuration = Column(Text, nullable=True)  # JSON configuration
    metrics_data = Column(Text, nullable=True)  # JSON performance metrics
    
    def __repr__(self) -> str:
        """String representation of the bot status."""
        return f"<BotStatus(id={self.id}, state={self.state}, office={self.target_office_code})>"
    
    @validates('state')
    def validate_state(self, key, state):
        """Validate bot state."""
        if state not in [e.value for e in BotState]:
            raise ValueError(f"Invalid bot state: {state}")
        return state
    
    @validates('monitoring_mode')
    def validate_monitoring_mode(self, key, mode):
        """Validate monitoring mode."""
        if mode not in [e.value for e in MonitoringMode]:
            raise ValueError(f"Invalid monitoring mode: {mode}")
        return mode
    
    @validates('health_status')
    def validate_health_status(self, key, status):
        """Validate health status."""
        if status not in [e.value for e in BotHealth]:
            raise ValueError(f"Invalid health status: {status}")
        return status
    
    @classmethod
    def create_initial_status(
        cls,
        bot_instance_id: str,
        target_office_code: Optional[str] = None,
        monitoring_interval_seconds: int = 300,
        auto_booking_enabled: bool = False
    ) -> "BotStatus":
        """
        Create initial bot status entry.
        
        Args:
            bot_instance_id: Unique identifier for bot instance
            target_office_code: Office code to monitor
            monitoring_interval_seconds: Monitoring interval
            auto_booking_enabled: Whether auto-booking is enabled
            
        Returns:
            BotStatus: New bot status instance
        """
        return cls(
            bot_instance_id=bot_instance_id,
            state=BotState.STOPPED.value,
            monitoring_mode=MonitoringMode.DISABLED.value,
            health_status=BotHealth.UNKNOWN.value,
            target_office_code=target_office_code,
            monitoring_interval_seconds=monitoring_interval_seconds,
            auto_booking_enabled=auto_booking_enabled,
            current_message="Bot initialized"
        )
    
    @property
    def state_enum(self) -> BotState:
        """Get state as enum."""
        try:
            return BotState(self.state)
        except ValueError:
            return BotState.ERROR
    
    @property
    def monitoring_mode_enum(self) -> MonitoringMode:
        """Get monitoring mode as enum."""
        try:
            return MonitoringMode(self.monitoring_mode)
        except ValueError:
            return MonitoringMode.DISABLED
    
    @property
    def health_status_enum(self) -> BotHealth:
        """Get health status as enum."""
        try:
            return BotHealth(self.health_status)
        except ValueError:
            return BotHealth.UNKNOWN
    
    @property
    def is_running(self) -> bool:
        """Check if bot is currently running."""
        return self.state_enum == BotState.RUNNING
    
    @property
    def is_stopped(self) -> bool:
        """Check if bot is stopped."""
        return self.state_enum == BotState.STOPPED
    
    @property
    def is_healthy(self) -> bool:
        """Check if bot is healthy."""
        return self.health_status_enum == BotHealth.HEALTHY
    
    @property
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is active."""
        return (
            self.is_running and 
            self.monitoring_mode_enum != MonitoringMode.DISABLED
        )
    
    @property
    def uptime_seconds(self) -> Optional[int]:
        """Get current uptime in seconds."""
        if not self.started_at:
            return None
        
        end_time = self.stopped_at if self.is_stopped else datetime.utcnow()
        return int((end_time - self.started_at).total_seconds())
    
    @property
    def time_since_last_check(self) -> Optional[timedelta]:
        """Get time since last check."""
        if not self.last_check_time:
            return None
        return datetime.utcnow() - self.last_check_time
    
    @property
    def is_overdue_for_check(self) -> bool:
        """Check if bot is overdue for a monitoring check."""
        if not self.is_monitoring_active or not self.last_check_time:
            return False
        
        time_since_check = self.time_since_last_check
        if not time_since_check:
            return False
        
        # Consider overdue if more than 2x the monitoring interval
        overdue_threshold = timedelta(seconds=self.monitoring_interval_seconds * 2)
        return time_since_check > overdue_threshold
    
    def start_bot(self, process_id: Optional[int] = None) -> None:
        """
        Mark bot as started.
        
        Args:
            process_id: Operating system process ID
        """
        self.state = BotState.STARTING.value
        self.started_at = datetime.utcnow()
        self.stopped_at = None
        self.process_id = process_id
        self.current_message = "Bot starting up..."
        self.health_status = BotHealth.UNKNOWN.value
        self.updated_at = datetime.utcnow()
    
    def mark_running(self, monitoring_mode: MonitoringMode = MonitoringMode.OFFICE_CHECK) -> None:
        """
        Mark bot as running.
        
        Args:
            monitoring_mode: Active monitoring mode
        """
        self.state = BotState.RUNNING.value
        self.monitoring_mode = monitoring_mode.value
        self.health_status = BotHealth.HEALTHY.value
        self.current_message = f"Bot running in {monitoring_mode.value} mode"
        self.updated_at = datetime.utcnow()
    
    def stop_bot(self, reason: str = "Manual stop") -> None:
        """
        Mark bot as stopped.
        
        Args:
            reason: Reason for stopping
        """
        self.state = BotState.STOPPED.value
        self.monitoring_mode = MonitoringMode.DISABLED.value
        self.stopped_at = datetime.utcnow()
        self.process_id = None
        self.current_message = f"Bot stopped: {reason}"
        self.health_status = BotHealth.UNKNOWN.value
        self.updated_at = datetime.utcnow()
    
    def mark_error(self, error_message: str, error_details: Optional[str] = None) -> None:
        """
        Mark bot as in error state.
        
        Args:
            error_message: Brief error description
            error_details: Detailed error information
        """
        self.state = BotState.ERROR.value
        self.health_status = BotHealth.CRITICAL.value
        self.last_error_time = datetime.utcnow()
        self.last_error_message = error_message
        self.last_error_details = error_details
        self.current_message = f"Error: {error_message}"
        self.updated_at = datetime.utcnow()
    
    def update_check_metrics(
        self, 
        success: bool, 
        response_time_ms: Optional[float] = None,
        slots_found: int = 0
    ) -> None:
        """
        Update metrics after a monitoring check.
        
        Args:
            success: Whether the check was successful
            response_time_ms: Response time in milliseconds
            slots_found: Number of slots found
        """
        self.last_check_time = datetime.utcnow()
        self.total_checks_performed += 1
        
        if success:
            self.last_success_time = datetime.utcnow()
            self.total_slots_found += slots_found
            
            # Update health status based on recent success
            self.health_status = BotHealth.HEALTHY.value
        else:
            # Update health status for failed checks
            if self.health_status_enum == BotHealth.HEALTHY:
                self.health_status = BotHealth.WARNING.value
        
        # Update average response time
        if response_time_ms is not None:
            if self.average_response_time_ms is None:
                self.average_response_time_ms = response_time_ms
            else:
                # Simple moving average
                self.average_response_time_ms = (
                    (self.average_response_time_ms * 0.8) + (response_time_ms * 0.2)
                )
        
        # Calculate success rate
        if self.total_checks_performed > 0:
            success_count = self.total_checks_performed
            if not success and self.last_success_time:
                # Estimate successful checks based on time since last success
                time_since_success = datetime.utcnow() - self.last_success_time
                estimated_failed_checks = max(1, int(time_since_success.total_seconds() / self.monitoring_interval_seconds))
                success_count = max(0, self.total_checks_performed - estimated_failed_checks)
            
            self.success_rate_percentage = (success_count / self.total_checks_performed) * 100
        
        self.updated_at = datetime.utcnow()
    
    def update_booking_metrics(self, attempt: bool, success: bool) -> None:
        """
        Update booking attempt metrics.
        
        Args:
            attempt: Whether a booking attempt was made
            success: Whether the booking was successful
        """
        if attempt:
            self.total_booking_attempts += 1
            
            if success:
                self.successful_bookings += 1
                self.current_message = "Booking successful!"
            else:
                self.current_message = "Booking attempt failed"
        
        self.updated_at = datetime.utcnow()
    
    def update_system_metrics(self, memory_mb: float, cpu_percentage: float) -> None:
        """
        Update system resource metrics.
        
        Args:
            memory_mb: Memory usage in MB
            cpu_percentage: CPU usage percentage
        """
        self.memory_usage_mb = memory_mb
        self.cpu_usage_percentage = cpu_percentage
        self.updated_at = datetime.utcnow()
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            dict: Configuration dictionary
        """
        if not self.configuration:
            return {}
        
        try:
            import json
            return json.loads(self.configuration)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_configuration(self, config: Dict[str, Any]) -> None:
        """
        Set configuration from dictionary.
        
        Args:
            config: Configuration dictionary
        """
        import json
        
        try:
            self.configuration = json.dumps(config, default=str)
        except (TypeError, ValueError):
            self.configuration = json.dumps({})
        
        self.updated_at = datetime.utcnow()
    
    def get_metrics_data(self) -> Dict[str, Any]:
        """
        Get metrics data as dictionary.
        
        Returns:
            dict: Metrics data dictionary
        """
        if not self.metrics_data:
            return {}
        
        try:
            import json
            return json.loads(self.metrics_data)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def add_metric(self, metric_name: str, metric_value: Any, timestamp: Optional[datetime] = None) -> None:
        """
        Add a metric data point.
        
        Args:
            metric_name: Name of the metric
            metric_value: Value of the metric
            timestamp: Timestamp for the metric
        """
        import json
        
        metrics = self.get_metrics_data()
        
        if metric_name not in metrics:
            metrics[metric_name] = []
        
        metric_entry = {
            "value": metric_value,
            "timestamp": (timestamp or datetime.utcnow()).isoformat()
        }
        
        # Keep only last 100 entries per metric
        metrics[metric_name].append(metric_entry)
        if len(metrics[metric_name]) > 100:
            metrics[metric_name] = metrics[metric_name][-100:]
        
        try:
            self.metrics_data = json.dumps(metrics, default=str)
        except (TypeError, ValueError):
            pass  # Ignore serialization errors
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert bot status to dictionary for API responses.
        
        Args:
            include_sensitive: Whether to include sensitive fields
            
        Returns:
            dict: Bot status data dictionary
        """
        data = {
            "id": self.id,
            "bot_instance_id": self.bot_instance_id,
            "state": self.state,
            "monitoring_mode": self.monitoring_mode,
            "health_status": self.health_status,
            "target_office_code": self.target_office_code,
            "monitoring_interval_seconds": self.monitoring_interval_seconds,
            "auto_booking_enabled": self.auto_booking_enabled,
            "is_running": self.is_running,
            "is_monitoring_active": self.is_monitoring_active,
            "current_message": self.current_message,
            "uptime_seconds": self.uptime_seconds,
            "total_checks_performed": self.total_checks_performed,
            "total_slots_found": self.total_slots_found,
            "success_rate_percentage": self.success_rate_percentage,
            "average_response_time_ms": self.average_response_time_ms,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data.update({
                "process_id": self.process_id,
                "memory_usage_mb": self.memory_usage_mb,
                "cpu_usage_percentage": self.cpu_usage_percentage,
                "current_details": self.current_details,
                "last_error_message": self.last_error_message,
                "last_error_details": self.last_error_details,
                "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
                "total_booking_attempts": self.total_booking_attempts,
                "successful_bookings": self.successful_bookings,
                "configuration": self.get_configuration(),
                "metrics_data": self.get_metrics_data()
            })
        
        return data
