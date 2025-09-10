"""
Unit tests for configuration management

Tests the configuration loading, validation, and environment variable handling.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, mock_open
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestConfig:
    """Test configuration management"""
    
    def test_config_from_env_with_all_variables(self):
        """Test Config.from_env() with all environment variables set"""
        env_vars = {
            'DATABASE_URL': 'sqlite:///test.db',
            'SMTP_SERVER': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'testpass',
            'NOTIFICATION_FROM_EMAIL': 'bot@test.com',
            'NOTIFICATION_FROM_NAME': 'Test Bot',
            'USER_NAME': 'Test User',
            'USER_EMAIL': 'user@test.com',
            'USER_PHONE': '+34612345678',
            'USER_NATIONALITY': 'US',
            'USER_PASSPORT_NUMBER': '123456789',
            'MONITORING_INTERVAL': '120',
            'DRY_RUN_MODE': 'true',
            'AUTO_BOOKING_ENABLED': 'false',
            'MAX_BOOKING_ATTEMPTS': '3',
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': 'test.log'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            assert config.database_url == 'sqlite:///test.db'
            assert config.smtp_server == 'smtp.test.com'
            assert config.smtp_port == 587
            assert config.smtp_username == 'test@test.com'
            assert config.smtp_password == 'testpass'
            assert config.notification_from_email == 'bot@test.com'
            assert config.notification_from_name == 'Test Bot'
            assert config.user_name == 'Test User'
            assert config.user_email == 'user@test.com'
            assert config.user_phone == '+34612345678'
            assert config.user_nationality == 'US'
            assert config.user_passport_number == '123456789'
            assert config.monitoring_interval == 120
            assert config.dry_run_mode is True
            assert config.auto_booking_enabled is False
            assert config.max_booking_attempts == 3
            assert config.log_level == 'INFO'
            assert config.log_file == 'test.log'
    
    def test_config_from_env_with_missing_variables(self):
        """Test Config.from_env() with missing environment variables (should use defaults)"""
        minimal_env_vars = {
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'testpass',
            'USER_NAME': 'Test User',
            'USER_EMAIL': 'user@test.com',
            'USER_PHONE': '+34612345678',
            'USER_NATIONALITY': 'US',
            'USER_PASSPORT_NUMBER': '123456789'
        }
        
        with patch.dict(os.environ, minimal_env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            # Check defaults are applied
            assert config.database_url == 'sqlite:///asylum_bot.db'
            assert config.smtp_server == 'smtp.gmail.com'
            assert config.smtp_port == 587
            assert config.monitoring_interval == 120
            assert config.dry_run_mode is True
            assert config.auto_booking_enabled is False
            assert config.max_booking_attempts == 5
            assert config.log_level == 'INFO'
            assert config.log_file == 'logs/asylum_bot.log'
    
    def test_config_validation_success(self):
        """Test config validation with valid configuration"""
        env_vars = {
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'testpass',
            'USER_NAME': 'Test User',
            'USER_EMAIL': 'user@test.com',
            'USER_PHONE': '+34612345678',
            'USER_NATIONALITY': 'US',
            'USER_PASSPORT_NUMBER': '123456789'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            validation = config.validate()
            assert validation['valid'] is True
            assert len(validation['missing_fields']) == 0
            assert len(validation['warnings']) == 0
    
    def test_config_validation_missing_required_fields(self):
        """Test config validation with missing required fields"""
        incomplete_env_vars = {
            'SMTP_USERNAME': 'test@test.com',
            # Missing SMTP_PASSWORD
            'USER_NAME': 'Test User',
            # Missing USER_EMAIL, USER_PHONE, etc.
        }
        
        with patch.dict(os.environ, incomplete_env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            validation = config.validate()
            assert validation['valid'] is False
            assert 'smtp_password' in validation['missing_fields']
            assert 'user_email' in validation['missing_fields']
            assert 'user_phone' in validation['missing_fields']
    
    def test_config_validation_warnings(self):
        """Test config validation warnings for potentially problematic settings"""
        env_vars = {
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'testpass',
            'USER_NAME': 'Test User',
            'USER_EMAIL': 'user@test.com',
            'USER_PHONE': '+34612345678',
            'USER_NATIONALITY': 'US',
            'USER_PASSPORT_NUMBER': '123456789',
            'MONITORING_INTERVAL': '10',  # Very short interval
            'DRY_RUN_MODE': 'false',      # Live mode
            'MAX_BOOKING_ATTEMPTS': '50'   # Too many attempts
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            validation = config.validate()
            assert validation['valid'] is True  # Valid but with warnings
            
            warnings = validation['warnings']
            assert any('monitoring interval' in w.lower() for w in warnings)
            assert any('dry run mode is disabled' in w.lower() for w in warnings)
            assert any('booking attempts' in w.lower() for w in warnings)
    
    def test_config_boolean_parsing(self):
        """Test boolean value parsing from environment variables"""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('yes', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('no', False),
            ('', False),
            ('invalid', False)
        ]
        
        for env_value, expected in test_cases:
            env_vars = {
                'DRY_RUN_MODE': env_value,
                'AUTO_BOOKING_ENABLED': env_value,
                'SMTP_USERNAME': 'test@test.com',
                'SMTP_PASSWORD': 'testpass',
                'USER_NAME': 'Test User',
                'USER_EMAIL': 'user@test.com',
                'USER_PHONE': '+34612345678',
                'USER_NATIONALITY': 'US',
                'USER_PASSPORT_NUMBER': '123456789'
            }
            
            with patch.dict(os.environ, env_vars, clear=True):
                from config import Config
                config = Config.from_env()
                
                assert config.dry_run_mode == expected, f"Failed for '{env_value}'"
                assert config.auto_booking_enabled == expected, f"Failed for '{env_value}'"
    
    def test_config_integer_parsing(self):
        """Test integer value parsing from environment variables"""
        env_vars = {
            'SMTP_PORT': '465',
            'MONITORING_INTERVAL': '300',
            'MAX_BOOKING_ATTEMPTS': '10',
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'testpass',
            'USER_NAME': 'Test User',
            'USER_EMAIL': 'user@test.com',
            'USER_PHONE': '+34612345678',
            'USER_NATIONALITY': 'US',
            'USER_PASSPORT_NUMBER': '123456789'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            assert config.smtp_port == 465
            assert config.monitoring_interval == 300
            assert config.max_booking_attempts == 10
    
    def test_config_integer_parsing_invalid(self):
        """Test integer parsing with invalid values (should use defaults)"""
        env_vars = {
            'SMTP_PORT': 'invalid',
            'MONITORING_INTERVAL': 'not_a_number',
            'MAX_BOOKING_ATTEMPTS': '',
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'testpass',
            'USER_NAME': 'Test User',
            'USER_EMAIL': 'user@test.com',
            'USER_PHONE': '+34612345678',
            'USER_NATIONALITY': 'US',
            'USER_PASSPORT_NUMBER': '123456789'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            # Should use defaults for invalid integer values
            assert config.smtp_port == 587      # default
            assert config.monitoring_interval == 120  # default
            assert config.max_booking_attempts == 5   # default
    
    def test_config_email_validation(self):
        """Test email validation in config"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'test+label@gmail.com'
        ]
        
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user name@domain.com'
        ]
        
        from config import Config
        
        # Test valid emails
        for email in valid_emails:
            assert Config._is_valid_email(email), f"'{email}' should be valid"
        
        # Test invalid emails
        for email in invalid_emails:
            assert not Config._is_valid_email(email), f"'{email}' should be invalid"
    
    def test_config_phone_validation(self):
        """Test phone number validation in config"""
        valid_phones = [
            '+34612345678',
            '+1234567890',
            '+44123456789'
        ]
        
        invalid_phones = [
            '612345678',      # Missing country code
            '+34 612 345 678', # Spaces
            'phone',          # Not a number
            ''                # Empty
        ]
        
        from config import Config
        
        # Test valid phone numbers
        for phone in valid_phones:
            assert Config._is_valid_phone(phone), f"'{phone}' should be valid"
        
        # Test invalid phone numbers
        for phone in invalid_phones:
            assert not Config._is_valid_phone(phone), f"'{phone}' should be invalid"
    
    def test_config_to_dict(self):
        """Test config serialization to dictionary"""
        env_vars = {
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'testpass',
            'USER_NAME': 'Test User',
            'USER_EMAIL': 'user@test.com',
            'USER_PHONE': '+34612345678',
            'USER_NATIONALITY': 'US',
            'USER_PASSPORT_NUMBER': '123456789'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            config_dict = config.to_dict()
            
            assert isinstance(config_dict, dict)
            assert config_dict['smtp_username'] == 'test@test.com'
            assert config_dict['user_name'] == 'Test User'
            assert config_dict['dry_run_mode'] is True
            
            # Sensitive fields should be masked
            assert config_dict['smtp_password'] == '***'
            assert config_dict['user_passport_number'] == '***'
    
    def test_config_from_file(self):
        """Test loading config from .env file"""
        env_content = """
DATABASE_URL=sqlite:///file_test.db
SMTP_SERVER=smtp.file.com
SMTP_PORT=465
SMTP_USERNAME=file@test.com
SMTP_PASSWORD=filepass
USER_NAME=File User
USER_EMAIL=fileuser@test.com
USER_PHONE=+34612345679
USER_NATIONALITY=ES
USER_PASSPORT_NUMBER=987654321
MONITORING_INTERVAL=180
DRY_RUN_MODE=false
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file_path = f.name
        
        try:
            from config import Config
            config = Config.from_file(env_file_path)
            
            assert config.database_url == 'sqlite:///file_test.db'
            assert config.smtp_server == 'smtp.file.com'
            assert config.smtp_port == 465
            assert config.smtp_username == 'file@test.com'
            assert config.smtp_password == 'filepass'
            assert config.user_name == 'File User'
            assert config.user_email == 'fileuser@test.com'
            assert config.monitoring_interval == 180
            assert config.dry_run_mode is False
            
        finally:
            os.unlink(env_file_path)
    
    def test_config_repr_and_str(self):
        """Test config string representations"""
        env_vars = {
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'testpass',
            'USER_NAME': 'Test User',
            'USER_EMAIL': 'user@test.com',
            'USER_PHONE': '+34612345678',
            'USER_NATIONALITY': 'US',
            'USER_PASSPORT_NUMBER': '123456789'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from config import Config
            config = Config.from_env()
            
            config_str = str(config)
            config_repr = repr(config)
            
            # Should contain key information but mask sensitive data
            assert 'test@test.com' in config_str
            assert 'Test User' in config_str
            assert 'testpass' not in config_str  # Password should be masked
            assert '123456789' not in config_str  # Passport should be masked
            
            assert 'Config(' in config_repr
