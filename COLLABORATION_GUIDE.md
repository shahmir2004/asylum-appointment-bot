# 🤝 Collaboration Guide: Asylum Appointment Bot

**Welcome to the Asylum Appointment Bot project!** This guide will help you set up and collaborate on this Python automation project.

## 📋 **Project Overview**

This bot automatically monitors the Spanish government website for asylum appointment availability in Madrid offices and sends email notifications when slots become available.

### **🎯 Current Status: 95% Complete & Fully Functional**
- ✅ Complete MVP implementation (T001-T026)
- ✅ Advanced stealth capabilities to bypass website blocking
- ✅ Email notifications via Gmail
- ✅ SQLite database with Madrid office data
- ✅ Comprehensive logging and error handling
- ✅ Safety mode (dry-run) enabled by default

---

## 🚀 **Quick Start for New Collaborators**

### **Prerequisites**
- Python 3.11+ installed
- Git installed
- GitHub account
- Gmail account for notifications (optional)

### **1. Clone the Repository**
```bash
# Clone the repository
git clone https://github.com/YourUsername/asylum-appointment-bot.git
cd asylum-appointment-bot

# Switch to the main development branch
git checkout 001-a-bot-that
```

### **2. Set Up Python Environment**
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium
```

### **3. Configure Environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
notepad .env  # Windows
nano .env     # macOS/Linux
```

**Required .env configuration:**
```env
# Email Configuration (for notifications)
GMAIL_USERNAME=your-gmail@gmail.com
GMAIL_PASSWORD=your-app-password  # Gmail App Password, not regular password
RECIPIENT_EMAIL=your-gmail@gmail.com

# Bot Configuration
MONITORING_INTERVAL=120
DRY_RUN_MODE=true
AUTO_BOOKING_ENABLED=false
HEADLESS_BROWSER=true

# User Information (for booking forms)
DEFAULT_USER_NAME=Your Full Name
DEFAULT_USER_EMAIL=your-email@gmail.com
```

### **4. Test the Setup**
```bash
# Test configuration
python test_config.py

# Test email notifications (optional)
python test_email_notifications.py

# Test stealth capabilities
python test_stealth.py
```

### **5. Run the Bot**
```bash
# Start monitoring (safe mode - no real bookings)
python run.py

# Stop with Ctrl+C
```

---

## 🔧 **Development Workflow**

### **Branch Strategy**
- `master` - Stable releases
- `001-a-bot-that` - Main development branch (current)
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes

### **Before Starting Work**
```bash
# Always pull latest changes
git checkout 001-a-bot-that
git pull origin 001-a-bot-that

# Create feature branch
git checkout -b feature/your-feature-name
```

### **Making Changes**
```bash
# Make your changes
# Test your changes
python test_config.py
python -m pytest tests/

# Stage and commit
git add .
git commit -m "feat: add your feature description"

# Push to your branch
git push origin feature/your-feature-name
```

### **Code Review Process**
1. Create Pull Request on GitHub
2. Request review from team members
3. Address feedback
4. Merge when approved

---

## 📁 **Project Structure**

```
asylum-appointment-bot/
├── src/                          # Core application code
│   ├── models.py                 # Database models
│   ├── scraper.py               # Web scraping with stealth
│   ├── notifications.py         # Email notifications
│   ├── booking.py               # Appointment booking logic
│   ├── config.py                # Configuration management
│   ├── main.py                  # Main bot orchestrator
│   ├── cli.py                   # Command-line interface
│   ├── database.py              # Database setup
│   └── stealth/                 # Advanced stealth modules
│       ├── browser_stealth.py   # Browser fingerprint randomization
│       └── behavior_simulator.py # Human behavior simulation
├── tests/                       # Test suite
│   ├── test_models.py
│   ├── test_notifications.py
│   ├── test_scraper.py
│   └── test_integration.py
├── logs/                        # Application logs
├── specs/                       # Project specifications
├── .env                         # Environment configuration
├── requirements.txt             # Python dependencies
├── run.py                       # Easy startup script
└── README.md                    # Project documentation
```

---

## 🛠️ **Common Development Tasks**

### **Testing**
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_models.py -v

# Test with coverage
python -m pytest tests/ --cov=src

# Manual testing
python test_config.py           # Test configuration
python test_stealth.py          # Test stealth capabilities
python test_email_notifications.py  # Test email system
```

### **Debugging**
```bash
# Check logs
tail -f logs/asylum_bot.log

# Test individual components
python -c "from src.models import *; print('Models working')"
python -c "from src.scraper import *; print('Scraper working')"
python -c "from src.notifications import *; print('Notifications working')"
```

### **Database Management**
```bash
# View database contents
python -c "
from src.models import DatabaseManager
from src.database import get_database_session
with get_database_session() as session:
    offices = session.query(MadridOffice).all()
    for office in offices:
        print(f'{office.name} - {office.office_code}')
"
```

---

## 🚨 **Important Safety Notes**

### **⚠️ NEVER commit sensitive data:**
- Gmail passwords
- Personal information
- Database files with real data
- Log files with personal info

### **🛡️ Safety Features:**
- **Dry-run mode enabled by default** - no real bookings
- **Comprehensive logging** - all actions recorded
- **Rate limiting** - respects website limits
- **Error handling** - graceful failure recovery

### **🔒 Security Best Practices:**
- Use Gmail App Passwords, not regular passwords
- Keep `.env` file private (never commit)
- Regular security updates
- Monitor logs for unusual activity

---

## 📞 **Getting Help**

### **Common Issues & Solutions**

**1. Import Errors**
```bash
# Make sure you're in project directory
cd asylum-appointment-bot

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Browser Not Starting**
```bash
# Reinstall Playwright browsers
python -m playwright install chromium

# Check browser installation
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

**3. Email Not Working**
```bash
# Test email configuration
python test_email_notifications.py

# Check Gmail App Password setup:
# 1. Enable 2FA on Gmail
# 2. Generate App Password
# 3. Use App Password in .env file
```

**4. 403 Forbidden Errors**
```bash
# Test stealth capabilities
python test_stealth.py

# The bot includes advanced stealth features, but some blocking is normal
```

### **Communication Channels**
- **GitHub Issues** - Bug reports and feature requests
- **Pull Request Comments** - Code review discussions
- **Direct Messages** - Quick questions and coordination

### **Code Style Guidelines**
- Follow PEP 8 Python style guide
- Use type hints where possible
- Write descriptive commit messages
- Add docstrings to functions
- Include tests for new features

---

## 🎯 **Development Priorities**

### **High Priority (Ready for Development)**
1. **Proxy Integration** - Add residential proxy rotation
2. **CAPTCHA Solving** - Integrate 2captcha service
3. **Multi-Office Support** - Monitor multiple Madrid offices
4. **Telegram Notifications** - Add Telegram bot integration
5. **Docker Deployment** - Containerize for easy deployment

### **Medium Priority**
1. **Advanced Analytics** - Appointment availability tracking
2. **Web Dashboard** - Simple web interface for monitoring
3. **Mobile Alerts** - Push notifications
4. **Performance Optimization** - Speed improvements

### **Documentation Needs**
1. API documentation
2. Deployment guides
3. Troubleshooting guides
4. Video tutorials

---

## 📚 **Learning Resources**

### **Technologies Used**
- **Python 3.11+** - Core language
- **Playwright** - Browser automation
- **SQLAlchemy** - Database ORM
- **SQLite** - Database
- **SMTP** - Email notifications
- **Asyncio** - Asynchronous programming

### **Useful Links**
- [Playwright Documentation](https://playwright.dev/python/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Python Asyncio Guide](https://docs.python.org/3/library/asyncio.html)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)

---

## 🎉 **Welcome to the Team!**

Thank you for contributing to this project. Together we can help people access important government services more efficiently while respecting website policies and maintaining ethical automation practices.

**Happy coding! 🚀**
