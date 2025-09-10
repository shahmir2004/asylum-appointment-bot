"""
Email notification service for asylum appointment booking bot.

Uses Gmail SMTP with provided credentials to send notifications about:
- Appointment availability alerts
- Booking confirmations
- Error notifications
- System status updates
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, date, time
import logging
import os
from typing import Optional, Dict, List, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Gmail SMTP email service for asylum bot notifications"""
    
    def __init__(self, username: str, password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        """
        Initialize email service with Gmail credentials
        
        Args:
            username: Gmail email address
            password: Gmail app password (not regular password)
            smtp_server: SMTP server (default: smtp.gmail.com)
            smtp_port: SMTP port (default: 587 for TLS)
        """
        self.username = username
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.connection = None
        
        logger.info(f"EmailService initialized for {username}")
    
    def connect(self) -> bool:
        """
        Connect to Gmail SMTP server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create secure SSL context
            context = ssl.create_default_context()
            
            # Create SMTP session
            self.connection = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.connection.starttls(context=context)  # Enable TLS encryption
            self.connection.login(self.username, self.password)
            
            logger.info("Successfully connected to Gmail SMTP")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to SMTP: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from SMTP server"""
        if self.connection:
            try:
                self.connection.quit()
                logger.info("Disconnected from Gmail SMTP")
            except Exception as e:
                logger.warning(f"Error disconnecting from SMTP: {e}")
            finally:
                self.connection = None
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test SMTP connection and credentials
        
        Returns:
            dict: Test result with success status and details
        """
        result = {
            'success': False,
            'message': '',
            'timestamp': datetime.now().isoformat(),
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port
        }
        
        try:
            if self.connect():
                result['success'] = True
                result['message'] = 'SMTP connection test successful'
                self.disconnect()
            else:
                result['message'] = 'SMTP connection failed'
                
        except Exception as e:
            result['message'] = f'SMTP test error: {str(e)}'
            
        logger.info(f"SMTP connection test: {result['message']}")
        return result
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email notification
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            dict: Send result with success status and details
        """
        result = {
            'success': False,
            'message': '',
            'timestamp': datetime.now().isoformat(),
            'to_email': to_email,
            'subject': subject
        }
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = self.username
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add plain text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Connect if not already connected
            if not self.connection:
                if not self.connect():
                    result['message'] = 'Failed to connect to SMTP server'
                    return result
            
            # Send email
            self.connection.send_message(message)
            
            result['success'] = True
            result['message'] = 'Email sent successfully'
            logger.info(f"Email sent to {to_email}: {subject}")
            
        except smtplib.SMTPRecipientsRefused as e:
            result['message'] = f'Invalid recipient email: {e}'
            logger.error(result['message'])
        except smtplib.SMTPDataError as e:
            result['message'] = f'SMTP data error: {e}'
            logger.error(result['message'])
        except Exception as e:
            result['message'] = f'Error sending email: {str(e)}'
            logger.error(result['message'])
        
        return result
    
    def send_appointment_alert(self, to_email: str, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send appointment availability alert
        
        Args:
            to_email: Recipient email address
            appointment_data: Dictionary with appointment details
            
        Returns:
            dict: Send result
        """
        subject = f"🚨 Asylum Appointment Available - {appointment_data.get('office_name', 'Madrid Office')}"
        
        # Format appointment date and time
        appointment_date = appointment_data.get('date')
        appointment_time = appointment_data.get('time')
        
        if isinstance(appointment_date, date):
            date_str = appointment_date.strftime("%A, %B %d, %Y")
        else:
            date_str = str(appointment_date)
            
        if isinstance(appointment_time, time):
            time_str = appointment_time.strftime("%I:%M %p")
        else:
            time_str = str(appointment_time)
        
        # Plain text body
        body = f"""
APPOINTMENT AVAILABLE!

An asylum appointment slot has been detected:

📅 Date: {date_str}
🕐 Time: {time_str}
🏢 Office: {appointment_data.get('office_name', 'Unknown')}
📍 Location: {appointment_data.get('office_address', 'Madrid')}
🔗 Office Code: {appointment_data.get('office_code', 'Unknown')}

⚠️ IMPORTANT: This is an automated alert. Log in to the government website immediately to book this appointment as slots fill up quickly.

Website: https://icp.administracionelectronica.gob.es

Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
Asylum Appointment Bot
        """.strip()
        
        # HTML body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="color: #155724; margin: 0;">🚨 APPOINTMENT AVAILABLE!</h2>
        </div>
        
        <p>An asylum appointment slot has been detected:</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">📅 Date</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{date_str}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">🕐 Time</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{time_str}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">🏢 Office</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{appointment_data.get('office_name', 'Unknown')}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">📍 Location</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{appointment_data.get('office_address', 'Madrid')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">🔗 Office Code</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{appointment_data.get('office_code', 'Unknown')}</td>
            </tr>
        </table>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0;"><strong>⚠️ IMPORTANT:</strong> This is an automated alert. Log in to the government website immediately to book this appointment as slots fill up quickly.</p>
        </div>
        
        <p><a href="https://icp.administracionelectronica.gob.es" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Government Website</a></p>
        
        <hr style="margin: 30px 0;">
        <p style="color: #6c757d; font-size: 12px;">
            Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            Asylum Appointment Bot
        </p>
        
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_booking_confirmation(self, to_email: str, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send booking confirmation notification
        
        Args:
            to_email: Recipient email address  
            booking_data: Dictionary with booking details
            
        Returns:
            dict: Send result
        """
        subject = f"✅ Booking Confirmation - {booking_data.get('confirmation_code', 'Unknown')}"
        
        # Format appointment date and time
        appointment_date = booking_data.get('appointment_date')
        appointment_time = booking_data.get('appointment_time')
        
        if isinstance(appointment_date, date):
            date_str = appointment_date.strftime("%A, %B %d, %Y")
        else:
            date_str = str(appointment_date)
            
        if isinstance(appointment_time, time):
            time_str = appointment_time.strftime("%I:%M %p")
        else:
            time_str = str(appointment_time)
        
        # Check if this was a dry run
        is_dry_run = booking_data.get('dry_run', True)
        dry_run_notice = "\n⚠️ NOTE: This was a DRY RUN booking simulation. No actual appointment was booked." if is_dry_run else ""
        
        # Plain text body
        body = f"""
BOOKING CONFIRMATION

Your asylum appointment has been {'simulated' if is_dry_run else 'booked'} successfully!

📋 Confirmation Code: {booking_data.get('confirmation_code', 'Unknown')}
📅 Date: {date_str}
🕐 Time: {time_str}
🏢 Office: {booking_data.get('office_name', 'Unknown')}
📍 Address: {booking_data.get('office_address', 'Madrid')}
📞 Office Phone: {booking_data.get('office_phone', 'N/A')}

👤 Booked for: {booking_data.get('user_name', 'Unknown')}
📧 Email: {booking_data.get('user_email', to_email)}
🛂 Passport: {booking_data.get('passport_number', 'Unknown')}
{dry_run_notice}

IMPORTANT REMINDERS:
• Arrive 15 minutes early
• Bring original documents and photocopies
• Bring passport and all supporting documents
• Contact the office if you need to reschedule

Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
Asylum Appointment Bot
        """.strip()
        
        # HTML body with dry run styling
        dry_run_html = """
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0;"><strong>⚠️ NOTE:</strong> This was a DRY RUN booking simulation. No actual appointment was booked.</p>
        </div>
        """ if is_dry_run else ""
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        
        <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="color: #0c5460; margin: 0;">✅ BOOKING CONFIRMATION</h2>
        </div>
        
        <p>Your asylum appointment has been <strong>{'simulated' if is_dry_run else 'booked'}</strong> successfully!</p>
        
        {dry_run_html}
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">📋 Confirmation Code</td>
                <td style="border: 1px solid #dee2e6; padding: 12px; font-family: monospace;">{booking_data.get('confirmation_code', 'Unknown')}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">📅 Date</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{date_str}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">🕐 Time</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{time_str}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">🏢 Office</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{booking_data.get('office_name', 'Unknown')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">📍 Address</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{booking_data.get('office_address', 'Madrid')}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">📞 Office Phone</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{booking_data.get('office_phone', 'N/A')}</td>
            </tr>
        </table>
        
        <h3>Booking Details</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">👤 Name</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{booking_data.get('user_name', 'Unknown')}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">📧 Email</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{booking_data.get('user_email', to_email)}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 12px; font-weight: bold;">🛂 Passport</td>
                <td style="border: 1px solid #dee2e6; padding: 12px;">{booking_data.get('passport_number', 'Unknown')}</td>
            </tr>
        </table>
        
        <div style="background-color: #e2e3e5; border: 1px solid #d3d3d4; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4 style="margin-top: 0;">IMPORTANT REMINDERS:</h4>
            <ul style="margin-bottom: 0;">
                <li>Arrive 15 minutes early</li>
                <li>Bring original documents and photocopies</li>
                <li>Bring passport and all supporting documents</li>
                <li>Contact the office if you need to reschedule</li>
            </ul>
        </div>
        
        <hr style="margin: 30px 0;">
        <p style="color: #6c757d; font-size: 12px;">
            Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            Asylum Appointment Bot
        </p>
        
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_error_notification(self, to_email: str, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send error notification
        
        Args:
            to_email: Recipient email address
            error_data: Dictionary with error details
            
        Returns:
            dict: Send result
        """
        subject = f"⚠️ Asylum Bot Error - {error_data.get('error_type', 'Unknown Error')}"
        
        body = f"""
ERROR NOTIFICATION

The asylum appointment bot encountered an error:

❌ Error Type: {error_data.get('error_type', 'Unknown')}
📝 Error Message: {error_data.get('error_message', 'No details available')}
🕐 Occurred At: {error_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
🔄 Operation: {error_data.get('operation', 'Unknown')}

Additional Details:
{json.dumps(error_data.get('context', {}), indent=2)}

The bot will continue monitoring and attempt to recover automatically.

---
Asylum Appointment Bot
        """.strip()
        
        return self.send_email(to_email, subject, body)
    
    def send_system_status(self, to_email: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send system status notification
        
        Args:
            to_email: Recipient email address
            status_data: Dictionary with system status
            
        Returns:
            dict: Send result
        """
        status = status_data.get('status', 'unknown')
        status_emoji = "✅" if status == "healthy" else "⚠️" if status == "warning" else "❌"
        
        subject = f"{status_emoji} Asylum Bot Status - {status.title()}"
        
        body = f"""
SYSTEM STATUS UPDATE

{status_emoji} Overall Status: {status.upper()}

📊 Statistics:
• Uptime: {status_data.get('uptime', 'Unknown')}
• Last Check: {status_data.get('last_check', 'Never')}
• Appointments Found: {status_data.get('appointments_found', 0)}
• Booking Attempts: {status_data.get('booking_attempts', 0)}
• Successful Bookings: {status_data.get('successful_bookings', 0)}

🔧 Component Status:
• Database: {status_data.get('database_status', 'Unknown')}
• Web Scraper: {status_data.get('scraper_status', 'Unknown')}
• Email Service: {status_data.get('email_status', 'Unknown')}
• Monitoring: {status_data.get('monitoring_status', 'Unknown')}

Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
Asylum Appointment Bot
        """.strip()
        
        return self.send_email(to_email, subject, body)

class NotificationService:
    """High-level notification service for asylum bot"""
    
    def __init__(self, email_service: EmailService, default_recipient: str):
        """
        Initialize notification service
        
        Args:
            email_service: Configured EmailService instance
            default_recipient: Default email address for notifications
        """
        self.email_service = email_service
        self.default_recipient = default_recipient
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def from_env(cls) -> 'NotificationService':
        """Create NotificationService from environment variables"""
        gmail_username = os.getenv('GMAIL_USERNAME')
        gmail_password = os.getenv('GMAIL_PASSWORD')
        recipient_email = os.getenv('RECIPIENT_EMAIL', gmail_username)
        
        if not gmail_username or not gmail_password:
            raise ValueError("GMAIL_USERNAME and GMAIL_PASSWORD must be set in environment")
        
        email_service = EmailService(gmail_username, gmail_password)
        return cls(email_service, recipient_email)
    
    def notify_appointment_found(self, appointment_data: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """Send appointment found notification"""
        recipient = recipient or self.default_recipient
        result = self.email_service.send_appointment_alert(recipient, appointment_data)
        return result['success']
    
    def notify_booking_confirmed(self, booking_data: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """Send booking confirmation notification"""
        recipient = recipient or self.default_recipient
        result = self.email_service.send_booking_confirmation(recipient, booking_data)
        return result['success']
    
    def notify_error(self, error_data: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """Send error notification"""
        recipient = recipient or self.default_recipient
        result = self.email_service.send_error_notification(recipient, error_data)
        return result['success']
    
    def notify_status(self, status_data: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """Send status notification"""
        recipient = recipient or self.default_recipient
        result = self.email_service.send_system_status(recipient, status_data)
        return result['success']
    
    def test_notifications(self) -> Dict[str, Any]:
        """Test notification system"""
        return self.email_service.test_connection()
