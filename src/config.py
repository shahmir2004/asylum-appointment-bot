"""
Configuration management for asylum appointment booking bot.

Handles loading and validation of configuration from:
- Environment variables (.env file)
- Default values for MVP
- Runtime configuration updates
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration class for asylum bot"""
    
    # Site configuration
    site_url: str = "https://icp.administracionelectronica.gob.es"
    
    # Email configuration
    gmail_username: str = ""
    gmail_password: str = ""
    recipient_email: str = ""
    
    # Bot behavior
    monitoring_interval: int = 120  # 2 minutes in seconds
    dry_run_mode: bool = True  # MVP safety flag
    auto_booking_enabled: bool = False  # MVP safety flag
    headless_browser: bool = True
    
    # Database
    database_url: str = "sqlite:///asylum_bot.db"
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 5.0
    booking_timeout: int = 30
    
    # User defaults for MVP
    default_user_name: str = "Test User"
    default_user_email: str = ""
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/asylum_bot.log"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables
        
        Returns:
            Config instance with values from environment
        """
        config = cls()
        
        # Load site configuration
        config.site_url = os.getenv('SITE_URL', config.site_url)
        
        # Load email configuration
        config.gmail_username = os.getenv('GMAIL_USERNAME', '')
        config.gmail_password = os.getenv('GMAIL_PASSWORD', '')
        config.recipient_email = os.getenv('RECIPIENT_EMAIL', config.gmail_username)
        
        # Load bot behavior
        config.monitoring_interval = int(os.getenv('MONITORING_INTERVAL', config.monitoring_interval))
        config.dry_run_mode = os.getenv('TEST_MODE', 'true').lower() == 'true'
        config.auto_booking_enabled = os.getenv('AUTO_BOOKING_ENABLED', 'false').lower() == 'true'
        config.headless_browser = os.getenv('HEADLESS_BROWSER', 'true').lower() == 'true'
        
        # Load database configuration
        config.database_url = os.getenv('DATABASE_URL', config.database_url)
        
        # Load retry configuration
        config.max_retries = int(os.getenv('MAX_RETRIES', config.max_retries))
        config.retry_delay = float(os.getenv('RETRY_DELAY', config.retry_delay))
        config.booking_timeout = int(os.getenv('BOOKING_TIMEOUT', config.booking_timeout))
        
        # Load user defaults
        config.default_user_name = os.getenv('DEFAULT_USER_NAME', config.default_user_name)
        config.default_user_email = os.getenv('DEFAULT_USER_EMAIL', config.recipient_email)
        
        # Load logging configuration
        config.log_level = os.getenv('LOG_LEVEL', config.log_level)
        config.log_file = os.getenv('LOG_FILE', config.log_file)
        
        logger.info(f"Configuration loaded from environment (dry_run: {config.dry_run_mode})")
        return config
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration
        
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        required_fields = [
            ('gmail_username', self.gmail_username, 'Gmail username is required for notifications'),
            ('gmail_password', self.gmail_password, 'Gmail password is required for notifications'),
            ('site_url', self.site_url, 'Site URL is required'),
        ]
        
        for field_name, field_value, error_message in required_fields:
            if not field_value:
                validation_result['errors'].append(error_message)
                validation_result['valid'] = False
        
        # Check numeric values
        if self.monitoring_interval < 30:
            validation_result['warnings'].append('Monitoring interval less than 30 seconds may overload the site')
        
        if self.monitoring_interval > 3600:
            validation_result['warnings'].append('Monitoring interval greater than 1 hour may miss appointments')
        
        if self.max_retries < 1:
            validation_result['errors'].append('Max retries must be at least 1')
            validation_result['valid'] = False
        
        if self.retry_delay < 1.0:
            validation_result['warnings'].append('Retry delay less than 1 second may cause rate limiting')
        
        # Check email format (basic)
        if self.gmail_username and '@' not in self.gmail_username:
            validation_result['errors'].append('Gmail username must be a valid email address')
            validation_result['valid'] = False
        
        if self.recipient_email and '@' not in self.recipient_email:
            validation_result['errors'].append('Recipient email must be a valid email address')
            validation_result['valid'] = False
        
        # Check URL format (basic)
        if not self.site_url.startswith(('http://', 'https://')):
            validation_result['errors'].append('Site URL must start with http:// or https://')
            validation_result['valid'] = False
        
        # Safety warnings for MVP
        if not self.dry_run_mode:
            validation_result['warnings'].append('DRY RUN MODE is disabled - actual bookings will be attempted!')
        
        if self.auto_booking_enabled and not self.dry_run_mode:
            validation_result['warnings'].append('AUTO BOOKING is enabled with dry run disabled - this will make real bookings!')
        
        return validation_result
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Args:
            include_sensitive: Whether to include sensitive data like passwords
            
        Returns:
            Dictionary representation of configuration
        """
        config_dict = {
            'site_url': self.site_url,
            'gmail_username': self.gmail_username,
            'recipient_email': self.recipient_email,
            'monitoring_interval': self.monitoring_interval,
            'dry_run_mode': self.dry_run_mode,
            'auto_booking_enabled': self.auto_booking_enabled,
            'headless_browser': self.headless_browser,
            'database_url': self.database_url,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'booking_timeout': self.booking_timeout,
            'default_user_name': self.default_user_name,
            'default_user_email': self.default_user_email,
            'log_level': self.log_level,
            'log_file': self.log_file
        }
        
        if include_sensitive:
            config_dict['gmail_password'] = self.gmail_password
        else:
            config_dict['gmail_password'] = '***hidden***' if self.gmail_password else None
        
        return config_dict
    
    def update_from_dict(self, updates: Dict[str, Any]):
        """
        Update configuration from dictionary
        
        Args:
            updates: Dictionary with configuration updates
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"Updated config {key}: {value}")
            else:
                logger.warning(f"Unknown config key: {key}")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database-specific configuration"""
        return {
            'database_url': self.database_url,
            'echo': self.log_level == 'DEBUG'  # Enable SQL logging in debug mode
        }
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email-specific configuration"""
        return {
            'username': self.gmail_username,
            'password': self.gmail_password,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'recipient': self.recipient_email
        }
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Get scraping-specific configuration"""
        return {
            'base_url': self.site_url,
            'headless': self.headless_browser,
            'timeout': self.booking_timeout * 1000,  # Convert to milliseconds
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def get_booking_config(self) -> Dict[str, Any]:
        """Get booking-specific configuration"""
        return {
            'dry_run_mode': self.dry_run_mode,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'booking_timeout': self.booking_timeout,
            'auto_booking_enabled': self.auto_booking_enabled
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring-specific configuration"""
        return {
            'interval_seconds': self.monitoring_interval,
            'auto_booking': self.auto_booking_enabled,
            'dry_run': self.dry_run_mode
        }

class ConfigManager:
    """Manages configuration loading, validation, and updates"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize config manager
        
        Args:
            config: Configuration instance (defaults to Config.from_env())
        """
        self.config = config or Config.from_env()
        self.logger = logging.getLogger(__name__)
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from JSON file
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            import json
            
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            self.config.update_from_dict(config_data)
            self.logger.info(f"Configuration loaded from {file_path}")
            return True
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {file_path}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading configuration file: {e}")
            return False
    
    def save_to_file(self, file_path: str, include_sensitive: bool = False) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            file_path: Path to save configuration file
            include_sensitive: Whether to include sensitive data
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            import json
            
            config_data = self.config.to_dict(include_sensitive=include_sensitive)
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration file: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate current configuration
        
        Returns:
            Dictionary with validation results
        """
        return self.config.validate()
    
    def get_config_summary(self) -> str:
        """
        Get human-readable configuration summary
        
        Returns:
            String with configuration summary
        """
        config_dict = self.config.to_dict(include_sensitive=False)
        
        summary = "Asylum Bot Configuration Summary:\n"
        summary += "=" * 40 + "\n"
        
        sections = {
            'Site Configuration': ['site_url'],
            'Email Configuration': ['gmail_username', 'recipient_email'],
            'Bot Behavior': ['monitoring_interval', 'dry_run_mode', 'auto_booking_enabled', 'headless_browser'],
            'Database': ['database_url'],
            'Retry Settings': ['max_retries', 'retry_delay', 'booking_timeout'],
            'User Defaults': ['default_user_name', 'default_user_email'],
            'Logging': ['log_level', 'log_file']
        }
        
        for section_name, section_keys in sections.items():
            summary += f"\n{section_name}:\n"
            for key in section_keys:
                value = config_dict.get(key, 'Not set')
                summary += f"  {key}: {value}\n"
        
        return summary
    
    def check_environment_variables(self) -> Dict[str, Any]:
        """
        Check which environment variables are set
        
        Returns:
            Dictionary with environment variable status
        """
        env_vars = {
            'SITE_URL': os.getenv('SITE_URL'),
            'GMAIL_USERNAME': os.getenv('GMAIL_USERNAME'),
            'GMAIL_PASSWORD': '***set***' if os.getenv('GMAIL_PASSWORD') else None,
            'RECIPIENT_EMAIL': os.getenv('RECIPIENT_EMAIL'),
            'MONITORING_INTERVAL': os.getenv('MONITORING_INTERVAL'),
            'TEST_MODE': os.getenv('TEST_MODE'),
            'AUTO_BOOKING_ENABLED': os.getenv('AUTO_BOOKING_ENABLED'),
            'HEADLESS_BROWSER': os.getenv('HEADLESS_BROWSER'),
            'DATABASE_URL': os.getenv('DATABASE_URL'),
            'MAX_RETRIES': os.getenv('MAX_RETRIES'),
            'RETRY_DELAY': os.getenv('RETRY_DELAY'),
            'BOOKING_TIMEOUT': os.getenv('BOOKING_TIMEOUT'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL'),
            'LOG_FILE': os.getenv('LOG_FILE')
        }
        
        return {
            'set_variables': {k: v for k, v in env_vars.items() if v is not None},
            'missing_variables': [k for k, v in env_vars.items() if v is None],
            'total_checked': len(env_vars)
        }

# Create default config manager instance
config_manager = ConfigManager()

# Convenience function for getting current config
def get_config() -> Config:
    """Get current configuration"""
    return config_manager.config

# Convenience function for validating current config
def validate_config() -> Dict[str, Any]:
    """Validate current configuration"""
    return config_manager.validate_config()
