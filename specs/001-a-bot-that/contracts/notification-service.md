# Notification Service API Contract

## Overview
The Notification Service handles multi-channel alert delivery for booking confirmations, errors, and system status updates. Supports email and Telegram notifications with delivery tracking and retry mechanisms.

## Library Interface

### CLI Commands

#### Send Notification
```bash
notification-service send --user-id=1 --type=booking_success --template=appointment_booked --data='{"date":"2025-09-15","time":"09:30","office":"Madrid Centro"}' --channels=email,telegram --output=json
```

**Purpose**: Send notification through specified channels
**Parameters**:
- `--user-id`: Integer, required, recipient user ID
- `--type`: String, required, notification type for tracking
- `--template`: String, required, message template to use
- `--data`: String, required, JSON data for template variables
- `--channels`: String, required, comma-separated delivery channels
- `--priority`: String, optional, delivery priority (low|normal|high, default: normal)
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "notification_id": "notif_123",
  "user_id": 1,
  "type": "booking_success",
  "channels": ["email", "telegram"],
  "status": "sent",
  "delivery_results": {
    "email": {
      "status": "delivered",
      "message_id": "email_456",
      "delivered_at": "2025-09-09T10:00:30Z"
    },
    "telegram": {
      "status": "delivered", 
      "message_id": "789",
      "delivered_at": "2025-09-09T10:00:25Z"
    }
  },
  "timestamp": "2025-09-09T10:00:00Z"
}
```

#### Get Delivery Status
```bash
notification-service status --notification-id=notif_123 --output=json
```

**Purpose**: Check delivery status of sent notification
**Parameters**:
- `--notification-id`: String, required, notification to check
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "notification_id": "notif_123",
  "overall_status": "delivered",
  "sent_at": "2025-09-09T10:00:00Z",
  "channels": {
    "email": {
      "status": "delivered",
      "attempts": 1,
      "last_attempt": "2025-09-09T10:00:15Z",
      "delivered_at": "2025-09-09T10:00:30Z",
      "external_id": "email_456"
    },
    "telegram": {
      "status": "delivered",
      "attempts": 1,
      "last_attempt": "2025-09-09T10:00:10Z",
      "delivered_at": "2025-09-09T10:00:25Z",
      "external_id": "789"
    }
  }
}
```

#### List Templates
```bash
notification-service templates --type=all --output=json
```

**Purpose**: List available notification templates
**Parameters**:
- `--type`: String, optional, filter by notification type (all|booking|error|system, default: all)
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "templates": [
    {
      "name": "appointment_booked",
      "type": "booking",
      "channels": ["email", "telegram"],
      "variables": ["date", "time", "office", "confirmation_code"],
      "description": "Successful appointment booking confirmation"
    },
    {
      "name": "booking_failed",
      "type": "error", 
      "channels": ["email", "telegram"],
      "variables": ["office", "error_message", "retry_time"],
      "description": "Booking attempt failure notification"
    }
  ],
  "total_count": 2
}
```

#### Test Notification
```bash
notification-service test --user-id=1 --channels=email --output=json
```

**Purpose**: Send test notification to verify configuration
**Parameters**:
- `--user-id`: Integer, required, recipient for test
- `--channels`: String, required, channels to test
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "test_id": "test_321",
  "user_id": 1,
  "channels_tested": ["email"],
  "results": {
    "email": {
      "status": "success",
      "response_time_ms": 1250,
      "message": "Test notification delivered successfully"
    }
  },
  "timestamp": "2025-09-09T10:05:00Z"
}
```

### Python Library Interface

#### NotificationService Class
```python
from notification_service import NotificationService, NotificationTemplate

class NotificationService:
    def __init__(self, config: dict):
        """Initialize notification service with channel configurations"""
        
    async def send_notification(self, user_id: int, template_name: str, data: dict, 
                              channels: list, priority: str = "normal") -> dict:
        """Send notification through specified channels"""
        
    async def get_delivery_status(self, notification_id: str) -> dict:
        """Get delivery status of notification"""
        
    async def retry_failed_delivery(self, notification_id: str, channels: list = None) -> dict:
        """Retry failed notification delivery"""
        
    async def test_channels(self, user_id: int, channels: list) -> dict:
        """Test notification channel configuration"""
        
    def get_templates(self, notification_type: str = None) -> list:
        """List available notification templates"""
```

#### EmailChannel Class
```python
class EmailChannel:
    def __init__(self, smtp_config: dict):
        """Initialize email channel with SMTP configuration"""
        
    async def send(self, recipient: str, subject: str, body: str, 
                   template_data: dict = None) -> dict:
        """Send email notification"""
        
    async def verify_delivery(self, message_id: str) -> bool:
        """Verify email delivery status"""
```

#### TelegramChannel Class  
```python
class TelegramChannel:
    def __init__(self, bot_token: str):
        """Initialize Telegram channel with bot configuration"""
        
    async def send(self, chat_id: str, message: str, parse_mode: str = "HTML") -> dict:
        """Send Telegram message"""
        
    async def send_document(self, chat_id: str, document: bytes, 
                          filename: str, caption: str = None) -> dict:
        """Send document via Telegram"""
```

#### NotificationTemplate Class
```python
class NotificationTemplate:
    def __init__(self, name: str, template_config: dict):
        """Initialize notification template"""
        
    def render(self, data: dict, channel: str) -> dict:
        """Render template for specific channel with data"""
        
    def validate_data(self, data: dict) -> bool:
        """Validate that required template variables are provided"""
```

## Message Templates

### Booking Success Template
**Email Version**:
```html
Subject: ✅ Asylum Appointment Booked Successfully - {{date}} at {{time}}

Dear User,

Great news! Your asylum appointment has been successfully booked:

📅 Date: {{date}}
⏰ Time: {{time}}
🏢 Office: {{office}}
📄 Confirmation Code: {{confirmation_code}}

Please save this confirmation code and arrive 15 minutes early for your appointment.

Important reminders:
- Bring all required documents
- Arrive on time as appointments cannot be rescheduled easily
- Contact the office if you need to cancel

Best regards,
Asylum Appointment Bot
```

**Telegram Version**:
```
🎉 *Appointment Booked Successfully!*

📅 *Date:* {{date}}
⏰ *Time:* {{time}}
🏢 *Office:* {{office}}
📄 *Confirmation:* `{{confirmation_code}}`

✅ Your asylum appointment is confirmed. Please save this information and arrive 15 minutes early.
```

### Booking Failed Template
**Email Version**:
```html
Subject: ❌ Booking Attempt Failed - {{office}}

Dear User,

Unfortunately, the booking attempt for {{office}} was unsuccessful.

Error: {{error_message}}

Don't worry! The bot will continue monitoring and will try again when new appointments become available.

Next check scheduled for: {{retry_time}}

The bot remains active and will notify you immediately when an appointment is successfully booked.

Best regards,
Asylum Appointment Bot
```

**Telegram Version**:
```
❌ *Booking Failed*

🏢 *Office:* {{office}}
⚠️ *Error:* {{error_message}}

🔄 Bot continues monitoring...
⏰ *Next check:* {{retry_time}}

Don't worry! I'll keep trying automatically.
```

### System Error Template
**Email Version**:
```html
Subject: 🚨 System Alert - Bot Requires Attention

Dear User,

The asylum appointment bot has encountered an issue that requires your attention:

Issue: {{error_type}}
Details: {{error_message}}
Occurred at: {{timestamp}}

Action Required: {{action_required}}

The monitoring has been paused until this issue is resolved. Please check the bot configuration and restart monitoring when ready.

Best regards,
Asylum Appointment Bot
```

**Telegram Version**:
```
🚨 *System Alert*

⚠️ *Issue:* {{error_type}}
📝 *Details:* {{error_message}}
🕒 *Time:* {{timestamp}}

🔧 *Action needed:* {{action_required}}

⏸️ Monitoring paused until resolved.
```

## Data Contracts

### Notification Request Schema
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "integer"},
    "template_name": {"type": "string"},
    "notification_type": {"type": "string", "enum": ["booking", "error", "system", "test"]},
    "data": {"type": "object"},
    "channels": {"type": "array", "items": {"type": "string", "enum": ["email", "telegram"]}},
    "priority": {"type": "string", "enum": ["low", "normal", "high"]},
    "scheduled_for": {"type": "string", "format": "date-time"}
  },
  "required": ["user_id", "template_name", "data", "channels"]
}
```

### Delivery Result Schema
```json
{
  "type": "object",
  "properties": {
    "notification_id": {"type": "string"},
    "channel": {"type": "string"},
    "status": {"type": "string", "enum": ["sent", "delivered", "failed", "pending"]},
    "external_id": {"type": "string"},
    "attempt_count": {"type": "integer", "minimum": 1},
    "last_attempt": {"type": "string", "format": "date-time"},
    "delivered_at": {"type": "string", "format": "date-time"},
    "error_message": {"type": "string"},
    "response_time_ms": {"type": "integer", "minimum": 0}
  },
  "required": ["notification_id", "channel", "status", "attempt_count"]
}
```

## Integration Points

### User Profile Integration
- Retrieve user notification preferences
- Get email addresses and Telegram chat IDs
- Respect user notification settings
- Handle user preference updates

### Database Integration
- Log all notification attempts and results
- Store delivery confirmations
- Track notification history
- Maintain template versioning

### External Service Dependencies
- SMTP server for email delivery
- Telegram Bot API for instant messaging
- Email service provider APIs (optional)
- Delivery tracking services (optional)

## Configuration Management

### Email Configuration
```yaml
email:
  smtp:
    host: "smtp.gmail.com"
    port: 587
    use_tls: true
    username: "bot@example.com"
    password: "${EMAIL_PASSWORD}"
  default_sender: "Asylum Bot <bot@example.com>"
  reply_to: "support@example.com"
  tracking_enabled: true
```

### Telegram Configuration
```yaml
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  parse_mode: "HTML"
  disable_notification: false
  timeout_seconds: 30
  retry_on_flood: true
```

### Template Configuration
```yaml
templates:
  base_path: "./templates"
  cache_enabled: true
  auto_reload: false
  default_language: "en"
  supported_languages: ["en", "es"]
```

## Error Handling

### Delivery Failures
- **Email SMTP Errors**: Retry with exponential backoff
- **Telegram API Limits**: Queue messages with rate limiting
- **Network Timeouts**: Retry with different timeout values
- **Authentication Failures**: Alert admin, pause service

### Retry Strategies
```python
RETRY_CONFIG = {
    "email": {
        "max_attempts": 3,
        "backoff_factor": 2.0,
        "retry_delays": [30, 120, 300]  # seconds
    },
    "telegram": {
        "max_attempts": 5,
        "backoff_factor": 1.5,
        "retry_delays": [5, 15, 45, 135, 405]
    }
}
```

### Circuit Breaker
- Temporarily disable channels after repeated failures
- Automatic recovery after cooldown period
- Fallback to alternative channels
- Alert admin on circuit breaker activation

## Performance Requirements

### Response Times
- Notification sending: <5 seconds
- Status queries: <1 second
- Template rendering: <500ms
- Channel testing: <10 seconds

### Throughput
- 100+ notifications per minute
- Support for burst delivery
- Concurrent channel processing
- Queue management for high volume

### Reliability
- 99.5% delivery success rate
- <1% duplicate message rate
- Recovery from failures: <60 seconds
- Message ordering preservation

## Privacy and Security

### Data Protection
- Encrypt sensitive notification data
- Secure API key storage
- Audit trail for all deliveries
- Data retention policies

### Rate Limiting
- Respect external API limits
- User notification frequency limits
- Anti-spam measures
- Fair usage enforcement

### Authentication
- Secure webhook verification
- API key rotation support
- Channel authentication validation
- User authorization checks
