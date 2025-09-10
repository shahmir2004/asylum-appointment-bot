# Asylum Appointment Booking Bot (MVP)

🤖 **Automated bot for monitoring and booking asylum appointments in Madrid, Spain**

This bot monitors the Spanish government website for available asylum appointment slots and automatically attempts to book them. Built with Python, Playwright, and designed for safety with comprehensive dry-run mode.

## ⚠️ Important Disclaimers

- **MVP Mode**: This is a Minimum Viable Product designed for testing and validation
- **Dry Run by Default**: All booking attempts are simulated by default for safety
- **Educational Purpose**: This bot is for educational and personal use only
- **No Guarantees**: No guarantee of successful bookings or appointments
- **Use Responsibly**: Respect government website terms of service and rate limits

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ 
- Gmail account for notifications
- Valid asylum seeker credentials (name, email, phone, nationality, passport number)

### 1. Clone Repository

```bash
git clone <repository-url>
cd icpBot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file with your credentials:

```bash
# Email Configuration (Required)
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password

# User Information (Required)
USER_NAME=Your Full Name
USER_EMAIL=your-email@gmail.com
USER_PHONE=+34612345678
USER_NATIONALITY=US
USER_PASSPORT_NUMBER=123456789

# Optional Configuration
MONITORING_INTERVAL=120        # Seconds between checks (default: 120)
DRY_RUN_MODE=true             # Safe mode - simulates bookings (default: true)
AUTO_BOOKING_ENABLED=false    # Auto-book when appointments found (default: false)
LOG_LEVEL=INFO                # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### 4. Run the Bot

```bash
python run.py
```

Or using the CLI:

```bash
python -m src.cli monitor --user-email=your-email@gmail.com
```

## 📋 Features

### ✅ Implemented Features

- **🔍 Continuous Monitoring**: Monitors Madrid asylum offices every 2 minutes
- **📧 Email Notifications**: Instant alerts when appointments are found
- **🛡️ Safety First**: Dry-run mode simulates bookings without real submission
- **📊 Comprehensive Logging**: Detailed logs with emoji-enhanced messages
- **🔄 Error Recovery**: Progressive retry logic with network error handling
- **🛑 Graceful Shutdown**: Ctrl+C handling with proper resource cleanup
- **💾 Database Tracking**: SQLite database for appointments and booking attempts
- **🏥 Madrid Office Support**: Monitors multiple Madrid asylum offices

### 🎯 Core Components

1. **Scraping Service** (`src/scraper.py`)
   - Playwright-based web automation
   - Spanish date/time parsing
   - Appointment slot detection

2. **Booking Service** (`src/booking.py`)
   - Simulated booking attempts (MVP safety)
   - User credential management
   - Confirmation code generation

3. **Notification Service** (`src/notifications.py`)
   - Gmail SMTP integration
   - HTML email templates
   - Multiple notification types

4. **Database Models** (`src/models.py`)
   - User profiles and Madrid offices
   - Appointment slots and booking attempts
   - SQLAlchemy ORM with relationships

5. **Main Orchestrator** (`src/main.py`)
   - Coordinates all services
   - Health checks and monitoring
   - Progressive retry logic

## 📁 Project Structure

```
icpBot/
├── src/                      # Core application code
│   ├── main.py              # Main orchestrator
│   ├── cli.py               # Command-line interface
│   ├── models.py            # Database models
│   ├── scraper.py           # Web scraping service
│   ├── booking.py           # Booking service
│   ├── notifications.py     # Email notifications
│   ├── config.py            # Configuration management
│   └── database.py          # Database utilities
├── tests/                   # Unit and integration tests
│   ├── test_models.py       # Database model tests
│   ├── test_notifications.py # Email notification tests
│   ├── test_config.py       # Configuration tests
│   └── test_integration.py  # End-to-end tests
├── logs/                    # Application logs
├── .env                     # Environment configuration
├── requirements.txt         # Python dependencies
└── run.py                   # Simple startup script
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_USERNAME` | ✅ | - | Gmail address for notifications |
| `SMTP_PASSWORD` | ✅ | - | Gmail app password (not account password) |
| `USER_NAME` | ✅ | - | Your full name for appointments |
| `USER_EMAIL` | ✅ | - | Your email address |
| `USER_PHONE` | ✅ | - | Phone number with country code (+34...) |
| `USER_NATIONALITY` | ✅ | - | Nationality code (US, UK, etc.) |
| `USER_PASSPORT_NUMBER` | ✅ | - | Passport number |
| `DATABASE_URL` | ❌ | `sqlite:///asylum_bot.db` | Database connection |
| `SMTP_SERVER` | ❌ | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | ❌ | `587` | SMTP port |
| `MONITORING_INTERVAL` | ❌ | `120` | Seconds between checks |
| `DRY_RUN_MODE` | ❌ | `true` | Simulate bookings safely |
| `AUTO_BOOKING_ENABLED` | ❌ | `false` | Auto-book appointments |
| `MAX_BOOKING_ATTEMPTS` | ❌ | `5` | Max booking retries |
| `LOG_LEVEL` | ❌ | `INFO` | Logging detail level |
| `LOG_FILE` | ❌ | `logs/asylum_bot.log` | Log file path |

### Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account Settings → Security → App passwords
3. Generate an app password for "Mail"
4. Use this 16-character password as `SMTP_PASSWORD`

## 🎮 Usage Examples

### Monitor with Email Notifications

```bash
# Start monitoring with default settings
python run.py

# Monitor specific user with custom interval
python -m src.cli monitor --user-email=user@example.com --interval=60
```

### Check Specific Office

```bash
# Check specific Madrid office for appointments
python -m src.cli check-office --office-code=MAD001 --user-email=user@example.com
```

### Configuration Management

```bash
# Validate current configuration
python -m src.cli config --validate

# Show configuration status
python -m src.cli config --show
```

### View Logs and Status

```bash
# Show recent logs
python -m src.cli logs --tail=50

# Check bot health
python -m src.cli health
```

## 📊 Monitoring and Logging

### Log Levels

- **DEBUG**: Detailed technical information
- **INFO**: General operational messages with emojis
- **WARNING**: Important notices and potential issues
- **ERROR**: Error conditions requiring attention

### Log File Location

Logs are written to `logs/asylum_bot.log` by default. Example log entries:

```
2025-12-09 10:30:00 - INFO - 🚀 Starting continuous monitoring (interval: 120s)
2025-12-09 10:32:00 - INFO - 🔍 Checking Madrid Centro office for appointments...
2025-12-09 10:32:05 - INFO - ✅ Cycle summary: 0 appointments found, 0 booking attempts, 0 errors
2025-12-09 10:32:05 - INFO - ⏳ Waiting 120s until next check...
```

### Database

The bot maintains a SQLite database with:

- **User Profiles**: Personal information for bookings
- **Madrid Offices**: Available appointment offices
- **Appointment Slots**: Detected available appointments
- **Booking Attempts**: History of all booking attempts

## 🛡️ Safety Features

### Dry Run Mode (Default)

By default, the bot runs in dry-run mode:
- ✅ Monitors government website
- ✅ Detects available appointments  
- ✅ Sends email notifications
- ✅ Simulates booking process
- ❌ **Does NOT submit real booking requests**

### Live Mode (Optional)

To enable real bookings:
1. Set `DRY_RUN_MODE=false` in `.env`
2. Set `AUTO_BOOKING_ENABLED=true` in `.env`
3. **Use at your own risk**

### Rate Limiting

- Default 120-second intervals between checks
- Progressive backoff on errors
- Respectful of government website resources

## 🧪 Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_models.py -v
pytest tests/test_notifications.py -v
pytest tests/test_config.py -v
```

### Manual Testing

```bash
# Test email notifications
python -m src.cli test --email-notifications

# Test configuration
python -m src.cli config --validate

# Test database connection
python -m src.cli health --components=database
```

## 🚨 Troubleshooting

### Common Issues

1. **Gmail Authentication Fails**
   - Use app password, not account password
   - Enable 2-Factor Authentication first
   - Check `SMTP_USERNAME` and `SMTP_PASSWORD`

2. **No Appointments Found**
   - This is normal - appointments are rare
   - Check government website manually to verify
   - Ensure bot is running and not crashed

3. **Website Loading Errors**
   - Government site may be temporarily down
   - Bot will retry automatically with progressive backoff
   - Check internet connection

4. **Configuration Errors**
   - Run `python -m src.cli config --validate`
   - Check all required environment variables
   - Verify email and phone number formats

### Debug Mode

Enable detailed logging:

```bash
# Set debug logging in .env
LOG_LEVEL=DEBUG

# Or run with debug flag
python -m src.cli monitor --debug
```

### Getting Help

1. Check the logs in `logs/asylum_bot.log`
2. Validate configuration with `python -m src.cli config --validate`
3. Test individual components with `python -m src.cli health`
4. Review this README for configuration requirements

## 📜 License

This project is for educational and personal use only. Users are responsible for complying with all applicable laws and terms of service.

## ⚠️ Legal Notice

- This bot interacts with government websites
- Users must comply with website terms of service
- Respect rate limits and don't abuse the service
- No warranty or guarantee of functionality
- Use at your own risk

## 🔄 Version

**MVP Version 1.0** - Basic monitoring and notification functionality with comprehensive safety features.

---

**Built with ❤️ and Python for the asylum-seeking community**
