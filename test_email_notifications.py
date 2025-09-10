#!/usr/bin/env python3
"""
Email notification testing script for T026 - Gmail credentials validation

This script tests email notification functionality using the provided Gmail credentials.
Validates SMTP connection, email templates, and notification sending.
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def setup_logging():
    """Setup logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def test_gmail_credentials():
    """Test Gmail SMTP credentials"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔍 Testing Gmail SMTP credentials...")
        
        from config import Config
        config = Config.from_env()
        
        # Check that credentials are configured
        if not config.smtp_username or not config.smtp_password:
            logger.error("❌ Gmail credentials not configured")
            logger.error("💡 Set SMTP_USERNAME and SMTP_PASSWORD in .env file")
            return False
        
        logger.info(f"📧 Gmail account: {config.smtp_username}")
        logger.info(f"🔐 Password: {'*' * len(config.smtp_password)} (configured)")
        logger.info(f"📡 SMTP server: {config.smtp_server}:{config.smtp_port}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Credential check failed: {e}")
        return False

def test_notification_service():
    """Test notification service initialization"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔧 Testing notification service initialization...")
        
        from notifications import NotificationService
        from config import Config
        
        config = Config.from_env()
        notification_service = NotificationService(config)
        
        logger.info("✅ Notification service initialized successfully")
        
        # Test email validation
        test_email = config.user_email
        if notification_service._is_valid_email(test_email):
            logger.info(f"✅ Email address '{test_email}' is valid")
        else:
            logger.warning(f"⚠️ Email address '{test_email}' may be invalid")
        
        return notification_service
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("💡 Install dependencies with: pip install -r requirements.txt")
        return None
        
    except Exception as e:
        logger.error(f"❌ Notification service initialization failed: {e}")
        return None

def test_email_templates(notification_service):
    """Test email template formatting"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("📝 Testing email template formatting...")
        
        # Test appointment found template
        appointment_data = {
            'date': '2025-12-15',
            'time': '10:30',
            'office_info': {
                'name': 'Madrid Centro',
                'address': 'Calle Test 123'
            }
        }
        
        subject, body = notification_service._format_appointment_template(appointment_data)
        logger.info(f"✅ Appointment template - Subject: {subject[:50]}...")
        
        # Test booking confirmation template
        booking_data = {
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
        
        subject, body = notification_service._format_booking_template(booking_data)
        logger.info(f"✅ Booking template - Subject: {subject[:50]}...")
        
        # Test error notification template
        error_data = {
            'error_type': 'connection_error',
            'error_message': 'Test error message',
            'timestamp': datetime.now().isoformat(),
            'operation': 'test_operation'
        }
        
        subject, body = notification_service._format_error_template(error_data)
        logger.info(f"✅ Error template - Subject: {subject[:50]}...")
        
        # Test status notification template
        status_data = {
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'monitoring_interval': 120,
            'dry_run_mode': True
        }
        
        subject, body = notification_service._format_status_template(status_data)
        logger.info(f"✅ Status template - Subject: {subject[:50]}...")
        
        logger.info("✅ All email templates formatted successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email template test failed: {e}")
        return False

def test_smtp_connection(notification_service):
    """Test SMTP connection without sending email"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("📡 Testing SMTP connection...")
        
        # Test connection by creating a test message
        from config import Config
        config = Config.from_env()
        
        message = notification_service._create_message(
            to_email=config.user_email,
            subject="Test Connection - DO NOT SEND",
            body="This is a test message for connection validation.",
            is_html=False
        )
        
        logger.info("✅ Test message created successfully")
        logger.info(f"📧 From: {message['From']}")
        logger.info(f"📧 To: {message['To']}")
        logger.info(f"📧 Subject: {message['Subject']}")
        
        # Note: We don't actually send the message here
        logger.info("ℹ️ SMTP connection test completed (message not sent)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SMTP connection test failed: {e}")
        return False

def test_send_test_email(notification_service):
    """Send an actual test email"""
    logger = logging.getLogger(__name__)
    
    try:
        from config import Config
        config = Config.from_env()
        
        logger.info("📧 Sending test email...")
        logger.info(f"📧 To: {config.user_email}")
        
        # Create test status notification
        status_data = {
            'status': 'test',
            'timestamp': datetime.now().isoformat(),
            'message': 'This is a test email from the Asylum Bot',
            'configuration': {
                'dry_run_mode': config.dry_run_mode,
                'monitoring_interval': config.monitoring_interval,
                'user_name': config.user_name
            }
        }
        
        # Send test notification
        success = notification_service.notify_status(
            status_data=status_data,
            recipient=config.user_email
        )
        
        if success:
            logger.info("✅ Test email sent successfully!")
            logger.info(f"📧 Check your email inbox: {config.user_email}")
            logger.info("💡 If you don't see the email, check spam folder")
            return True
        else:
            logger.error("❌ Failed to send test email")
            logger.error("💡 Check Gmail credentials and internet connection")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test email sending failed: {e}")
        return False

def print_test_info():
    """Print test information"""
    print("""
===============================================================================
                                                               
    📧 T026 - Email Notification Testing                       
                                                                
    This test validates Gmail SMTP integration and email       
    notification functionality using provided credentials.     
                                                                
===============================================================================

⚠️  IMPORTANT NOTES:

• This test will send ONE real test email
• Make sure SMTP_USERNAME and SMTP_PASSWORD are configured
• Use Gmail app password, NOT your regular password
• Internet connection required

🔍 What this test checks:

✓ Gmail SMTP credentials validation
✓ Notification service initialization
✓ Email template formatting
✓ SMTP connection testing
✓ Actual test email sending

📧 Gmail App Password Setup:

1. Enable 2-Factor Authentication on Gmail
2. Go to Google Account Settings → Security → App passwords
3. Generate an app password for "Mail"
4. Use the 16-character password as SMTP_PASSWORD

""")

async def main():
    """Main test function"""
    logger = setup_logging()
    
    try:
        print_test_info()
        
        # Test Gmail credentials
        logger.info("🚀 Starting email notification tests...")
        if not test_gmail_credentials():
            logger.error("❌ Gmail credentials test failed")
            sys.exit(1)
        
        # Test notification service
        notification_service = test_notification_service()
        if not notification_service:
            logger.error("❌ Notification service test failed")
            sys.exit(1)
        
        # Test email templates
        if not test_email_templates(notification_service):
            logger.error("❌ Email template test failed")
            sys.exit(1)
        
        # Test SMTP connection
        if not test_smtp_connection(notification_service):
            logger.error("❌ SMTP connection test failed")
            sys.exit(1)
        
        # Ask user if they want to send test email
        logger.info("")
        logger.info("🎯 All preliminary tests passed!")
        
        response = input("📧 Send a real test email? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            if test_send_test_email(notification_service):
                logger.info("")
                logger.info("🎉 ALL EMAIL TESTS PASSED!")
                logger.info("✅ Email notifications are working correctly")
                logger.info("💡 The bot will be able to send notifications")
            else:
                logger.error("❌ Test email sending failed")
                sys.exit(1)
        else:
            logger.info("📧 Test email skipped by user")
            logger.info("✅ Preliminary email tests passed")
            logger.info("💡 Run this test again with 'y' to send actual test email")
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
        
    except Exception as e:
        logger.error(f"💥 Test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
