"""
Unit tests for notification service

Tests the email notification functionality including template rendering,
SMTP configuration, and various notification types.

Updated for T022 - comprehensive unit testing of individual components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestNotificationService:
    """Test email notification service"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing"""
        config = Mock()
        config.smtp_server = "smtp.gmail.com"
        config.smtp_port = 587
        config.smtp_username = "test@gmail.com"
        config.smtp_password = "test_password"
        config.notification_from_email = "test@gmail.com"
        config.notification_from_name = "Test Bot"
        return config
    
    @pytest.fixture
    def notification_service(self, mock_config):
        """Create notification service with mocked config"""
        from notifications import NotificationService
        return NotificationService(mock_config)
    
    @pytest.fixture
    def sample_booking_data(self):
        """Sample booking data for testing"""
        return {
            'success': True,
            'confirmation_code': 'TEST123456',
            'appointment_date': '2025-12-15',
            'appointment_time': '10:30',
            'office_info': {
                'name': 'Madrid Centro',
                'address': 'Calle Test 123'
            },
            'dry_run': True,
            'timestamp': datetime.now().isoformat()
        }
    
    @pytest.fixture
    def sample_error_data(self):
        """Sample error data for testing"""
        return {
            'error_type': 'connection_error',
            'error_message': 'Failed to connect to government website',
            'timestamp': datetime.now().isoformat(),
            'operation': 'appointment_scraping',
            'context': {'url': 'https://example.com', 'timeout': 30}
        }
    
    def test_notification_service_initialization(self, mock_config):
        """Test NotificationService initialization"""
        from notifications import NotificationService
        service = NotificationService(mock_config)
        
        assert service.config == mock_config
        assert service.smtp_server == "smtp.gmail.com"
        assert service.smtp_port == 587
        assert service.username == "test@gmail.com"
        assert service.password == "test_password"
        assert service.from_email == "test@gmail.com"
        assert service.from_name == "Test Bot"
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, notification_service):
        """Test successful email sending"""
        # Setup mock SMTP
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        # Test email sending
        result = notification_service._send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test message body",
            is_html=False
        )
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@gmail.com", "test_password")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
        
        assert result is True
    
    @patch('smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp, notification_service):
        """Test email sending with SMTP error"""
        # Setup mock to raise exception
        mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
        
        # Test email sending
        result = notification_service._send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test message body",
            is_html=False
        )
        
        assert result is False
    
    @patch('smtplib.SMTP')
    def test_notify_appointment_found(self, mock_smtp, notification_service):
        """Test appointment found notification"""
        # Setup mock SMTP
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        appointment_data = {
            'date': '2025-12-20',
            'time': '14:30',
            'office_info': {
                'name': 'Madrid Norte',
                'address': 'Avenida Test 456'
            }
        }
        
        result = notification_service.notify_appointment_found(
            appointment_data=appointment_data,
            recipient="user@example.com"
        )
        
        # Verify email was sent
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Get the sent message
        sent_call = mock_server.send_message.call_args[0][0]
        subject = sent_call['Subject']
        
        assert "Appointment Available" in subject
        assert "2025-12-20" in subject or "14:30" in subject
    
    @patch('smtplib.SMTP')
    def test_notify_booking_confirmed(self, mock_smtp, notification_service, sample_booking_data):
        """Test booking confirmation notification"""
        # Setup mock SMTP
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        result = notification_service.notify_booking_confirmed(
            booking_data=sample_booking_data,
            recipient="user@example.com"
        )
        
        # Verify email was sent
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Get the sent message
        sent_call = mock_server.send_message.call_args[0][0]
        subject = sent_call['Subject']
        body = sent_call.get_payload()
        
        assert "Booking Confirmed" in subject
        assert "TEST123456" in str(body)  # Confirmation code should be in body
    
    @patch('smtplib.SMTP')
    def test_notify_error(self, mock_smtp, notification_service, sample_error_data):
        """Test error notification"""
        # Setup mock SMTP
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        result = notification_service.notify_error(
            error_data=sample_error_data,
            recipient="admin@example.com"
        )
        
        # Verify email was sent
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Get the sent message
        sent_call = mock_server.send_message.call_args[0][0]
        subject = sent_call['Subject']
        body = str(sent_call.get_payload())
        
        assert "Error Alert" in subject
        assert "connection_error" in body
        assert "Failed to connect to government website" in body
    
    @patch('smtplib.SMTP')
    def test_notify_status(self, mock_smtp, notification_service):
        """Test status notification"""
        # Setup mock SMTP
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        status_data = {
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'monitoring_interval': 120,
            'dry_run_mode': True
        }
        
        result = notification_service.notify_status(
            status_data=status_data,
            recipient="user@example.com"
        )
        
        # Verify email was sent
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Get the sent message
        sent_call = mock_server.send_message.call_args[0][0]
        subject = sent_call['Subject']
        body = str(sent_call.get_payload())
        
        assert "Status Update" in subject
        assert "started" in body
        assert "120" in body  # monitoring interval
    
    def test_format_appointment_template(self, notification_service):
        """Test appointment notification template formatting"""
        appointment_data = {
            'date': '2025-12-25',
            'time': '09:00',
            'office_info': {
                'name': 'Madrid Centro',
                'address': 'Plaza España 1'
            }
        }
        
        subject, body = notification_service._format_appointment_template(appointment_data)
        
        assert "2025-12-25" in subject
        assert "09:00" in subject
        assert "Madrid Centro" in body
        assert "Plaza España 1" in body
        assert "appointment" in body.lower()
    
    def test_format_booking_template(self, notification_service, sample_booking_data):
        """Test booking confirmation template formatting"""
        subject, body = notification_service._format_booking_template(sample_booking_data)
        
        assert "TEST123456" in subject or "TEST123456" in body
        assert "2025-12-15" in body
        assert "10:30" in body
        assert "Madrid Centro" in body
        assert sample_booking_data['confirmation_code'] in body
    
    def test_format_error_template(self, notification_service, sample_error_data):
        """Test error notification template formatting"""
        subject, body = notification_service._format_error_template(sample_error_data)
        
        assert "connection_error" in subject or "connection_error" in body
        assert "Failed to connect to government website" in body
        assert "appointment_scraping" in body
        assert "https://example.com" in body
    
    def test_format_status_template(self, notification_service):
        """Test status notification template formatting"""
        status_data = {
            'status': 'stopped',
            'timestamp': datetime.now().isoformat(),
            'runtime_duration_seconds': 3600,
            'total_cycles': 30,
            'total_appointments_found': 5,
            'successful_bookings': 2
        }
        
        subject, body = notification_service._format_status_template(status_data)
        
        assert "stopped" in subject
        assert "30" in body  # total cycles
        assert "5" in body   # appointments found
        assert "2" in body   # successful bookings
        assert "3600" in body or "1 hour" in body  # runtime
    
    def test_create_html_message(self, notification_service):
        """Test HTML message creation"""
        message = notification_service._create_message(
            to_email="test@example.com",
            subject="HTML Test",
            body="<h1>Test HTML</h1><p>This is a test.</p>",
            is_html=True
        )
        
        assert message['To'] == "test@example.com"
        assert message['Subject'] == "HTML Test"
        assert message['From'] == "Test Bot <test@gmail.com>"
        
        # Check that it's multipart for HTML
        assert message.is_multipart()
    
    def test_create_text_message(self, notification_service):
        """Test plain text message creation"""
        message = notification_service._create_message(
            to_email="test@example.com",
            subject="Text Test",
            body="This is plain text.",
            is_html=False
        )
        
        assert message['To'] == "test@example.com"
        assert message['Subject'] == "Text Test"
        assert message['From'] == "Test Bot <test@gmail.com>"
        
        # Check that it's not multipart for plain text
        assert not message.is_multipart()
        
        appointment_data = {
            'office_name': 'Madrid Centro',
            'date': '2025-09-15',
            'time': '09:30',
            'office_code': 'MAD001'
        }
        
        # Should return True on successful send
        result = service.send_appointment_found(appointment_data)
        assert result is True
    
    def test_send_booking_success_notification(self):
        """Test sending notification when booking succeeds"""
        # This will fail until notifications.py is implemented
        from notifications import EmailService
        
        service = EmailService({})
        
        booking_data = {
            'office_name': 'Madrid Centro',
            'date': '2025-09-15',
            'time': '09:30',
            'confirmation_code': 'CONF123456',
            'office_address': 'Calle Mayor 1, Madrid'
        }
        
        result = service.send_booking_success(booking_data)
        assert result is True
    
    def test_send_error_notification(self):
        """Test sending notification when errors occur"""
        # This will fail until notifications.py is implemented
        from notifications import EmailService
        
        service = EmailService({})
        
        error_data = {
            'error_type': 'NetworkError',
            'error_message': 'Failed to connect to government site',
            'timestamp': '2025-09-09 17:00:00',
            'retry_in': '5 minutes'
        }
        
        result = service.send_error_notification(error_data)
        assert result is True
    
    @patch('smtplib.SMTP')
    def test_smtp_connection_handling(self, mock_smtp):
        """Test SMTP connection is properly managed"""
        # This will fail until notifications.py is implemented
        from notifications import EmailService
        
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        service = EmailService({
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_address': 'test@gmail.com',
            'email_password': 'password'
        })
        
        # Should establish SMTP connection
        result = service._connect_smtp()
        
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'password')
        assert result == mock_server
    
    def test_email_template_formatting(self):
        """Test that email templates are properly formatted"""
        # This will fail until notifications.py is implemented
        from notifications import EmailService
        
        service = EmailService({})
        
        data = {
            'office_name': 'Madrid Centro',
            'date': '2025-09-15',
            'time': '09:30'
        }
        
        subject, body = service._format_appointment_email(data)
        
        assert 'Madrid Centro' in subject
        assert '2025-09-15' in body
        assert '09:30' in body
        assert len(body) > 50  # Should be a substantial email
    
    def test_email_validation(self):
        """Test email address validation"""
        # This will fail until notifications.py is implemented
        from notifications import EmailService
        
        service = EmailService({})
        
        # Valid emails
        assert service._validate_email('test@gmail.com') is True
        assert service._validate_email('user.name@domain.co.uk') is True
        
        # Invalid emails
        assert service._validate_email('invalid-email') is False
        assert service._validate_email('') is False
        assert service._validate_email(None) is False
    
    def test_connection_retry_on_failure(self):
        """Test that email service retries on connection failure"""
        # This will fail until notifications.py is implemented
        from notifications import EmailService
        
        service = EmailService({
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_address': 'test@gmail.com',
            'email_password': 'password',
            'max_retries': 3
        })
        
        # Should attempt retries on failure
        with patch('smtplib.SMTP', side_effect=Exception("Connection failed")):
            result = service.send_appointment_found({'office_name': 'Test'})
            assert result is False
    
    def test_load_config_from_env(self):
        """Test loading email configuration from environment variables"""
        # This will fail until notifications.py is implemented
        from notifications import EmailService
        
        # Should load config from .env file
        service = EmailService.from_env()
        
        assert service.smtp_server == 'smtp.gmail.com'
        assert service.smtp_port == 587
        assert service.email_address == 'shahmirahmed.004@gmail.com'
        assert service.recipient_email == 'shahmirahmed.004@gmail.com'

if __name__ == "__main__":
    # Run with: python -m pytest tests/test_notifications.py -v
    pytest.main([__file__, "-v"])
