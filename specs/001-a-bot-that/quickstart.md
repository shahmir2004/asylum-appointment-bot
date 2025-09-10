# Quickstart Guide: Asylum Appointment Booking Bot

**Date**: September 9, 2025  
**Feature**: Automated asylum appointment booking for Madrid offices  
**Status**: Phase 1 Implementation Guide

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.11 or higher
- **Docker**: 20.10+ with docker-compose
- **Memory**: Minimum 2GB RAM, 4GB recommended
- **Storage**: 5GB free space for logs and data
- **Network**: Stable internet connection with HTTPS access

### Required Accounts and Services
1. **Email Service**: SMTP access (Gmail, Outlook, or dedicated provider)
2. **Telegram Bot**: Create bot via @BotFather for notifications
3. **Proxy Service**: Residential proxy provider (optional but recommended)
4. **CAPTCHA Service**: 2captcha or hCaptcha account (optional)

### Development Environment
```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Install Docker and docker-compose
curl -fsSL https://get.docker.com | sh
sudo apt install docker-compose

# Install system dependencies
sudo apt install redis-server postgresql-client
```

## Installation

### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone <repository-url>
cd asylum-appointment-bot

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables**:
```bash
# Database
DATABASE_URL=sqlite:///./asylum_bot.db

# Redis (for job queue)
REDIS_URL=redis://localhost:6379/0

# Government Site Credentials
GOVERNMENT_SITE_USERNAME=your_username
GOVERNMENT_SITE_PASSWORD=your_password

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional: Proxy Service
PROXY_SERVICE_URL=http://proxy-provider.com/api
PROXY_SERVICE_KEY=your_proxy_key

# Optional: CAPTCHA Service
CAPTCHA_SERVICE_API_KEY=your_2captcha_key
```

### 3. Database Initialization
```bash
# Initialize database schema
python -m bot_service.cli db init

# Seed Madrid office data
python -m bot_service.cli db seed-offices
```

### 4. Service Configuration Validation
```bash
# Test email configuration
python -m notification_service.cli test --channels=email

# Test Telegram configuration
python -m notification_service.cli test --channels=telegram

# Test proxy configuration (if configured)
python -m proxy_manager.cli health --pool-id=default

# Test government site access
python -m bot_service.cli test-connection
```

## Docker Deployment

### 1. Docker Compose Setup
```bash
# Build all services
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Service Health Checks
```bash
# Check all services are running
docker-compose ps

# Test service endpoints
curl http://localhost:8001/health  # Bot Service
curl http://localhost:8002/health  # Proxy Manager
curl http://localhost:8003/health  # Job Scheduler
curl http://localhost:8004/health  # Notification Service
```

## Quick Start Usage

### 1. Create User Profile
```bash
# Create user profile with credentials
python -m bot_service.cli user create \
  --email=your_email@example.com \
  --telegram-chat-id=your_chat_id \
  --government-username=your_gov_username \
  --government-password=your_gov_password
```

### 2. Start Monitoring
```bash
# Start appointment monitoring (every 2 minutes)
python -m job_scheduler.cli schedule-monitoring \
  --user-id=1 \
  --interval=120 \
  --priority=high
```

### 3. Monitor Progress
```bash
# Check monitoring status
python -m job_scheduler.cli list --status=active

# View recent activity
python -m bot_service.cli logs --last=10

# Check for discovered appointments
python -m bot_service.cli list-appointments --available-only
```

### 4. Manual Office Check
```bash
# Check specific office manually
python -m bot_service.cli check-office \
  --office-code=MAD001 \
  --user-id=1

# List all Madrid offices
python -m bot_service.cli list-offices --active-only
```

### 5. Stop Monitoring
```bash
# Get active session ID
SESSION_ID=$(python -m job_scheduler.cli list --status=active --format=json | jq -r '.jobs[0].job_id')

# Stop monitoring
python -m job_scheduler.cli cancel --job-id=$SESSION_ID
```

## User Stories Validation

### Story 1: Automated Appointment Detection
**Test Scenario**: Bot automatically discovers new appointment slots

```bash
# Start monitoring
python -m job_scheduler.cli schedule-monitoring --user-id=1 --interval=120

# Simulate appointment availability (test mode)
python -m bot_service.cli simulate-appointment \
  --office-code=MAD001 \
  --date=2025-09-15 \
  --time=09:30

# Verify appointment was detected
python -m bot_service.cli list-appointments --user-id=1 --status=discovered

# Expected: Appointment appears in database within 2 minutes
```

### Story 2: Automatic Booking Execution
**Test Scenario**: Bot automatically books the earliest available appointment

```bash
# Add test appointment slot
python -m bot_service.cli add-test-slot \
  --office-code=MAD001 \
  --date=2025-09-15 \
  --time=09:30

# Enable automatic booking
python -m job_scheduler.cli schedule-booking \
  --slot-id=1 \
  --user-id=1

# Monitor booking attempt
python -m job_scheduler.cli status --job-id=job_book_1

# Expected: Booking attempt completes with success or detailed error
```

### Story 3: User Notification System
**Test Scenario**: User receives immediate notification upon successful booking

```bash
# Trigger booking success notification
python -m notification_service.cli send \
  --user-id=1 \
  --type=booking_success \
  --template=appointment_booked \
  --data='{"date":"2025-09-15","time":"09:30","office":"Madrid Centro","confirmation_code":"CONF123456"}' \
  --channels=email,telegram

# Check delivery status
python -m notification_service.cli status --notification-id=notif_123

# Expected: Notifications delivered successfully to both channels
```

### Story 4: Continuous Monitoring
**Test Scenario**: Bot continues monitoring when no appointments are available

```bash
# Start monitoring with no available appointments
python -m job_scheduler.cli schedule-monitoring --user-id=1 --interval=60

# Monitor for 10 minutes
sleep 600

# Check monitoring statistics
python -m bot_service.cli stats --user-id=1 --period=10m

# Expected: Multiple check attempts logged, no errors, monitoring continues
```

### Story 5: Error Handling and Recovery
**Test Scenario**: Bot handles errors gracefully and continues monitoring

```bash
# Start monitoring
python -m job_scheduler.cli schedule-monitoring --user-id=1 --interval=120

# Simulate network error
python -m bot_service.cli simulate-error --type=network --duration=60

# Check error handling
python -m job_scheduler.cli list --status=retry

# Expected: Failed jobs automatically retry with backoff, monitoring resumes
```

## Troubleshooting

### Common Issues

#### 1. Government Site Access Issues
```bash
# Check credentials
python -m bot_service.cli test-connection --verbose

# Test different proxy
python -m proxy_manager.cli get-proxy --pool-id=default

# Check for site changes
python -m bot_service.cli analyze-site-structure
```

#### 2. Notification Delivery Problems
```bash
# Test email configuration
python -m notification_service.cli test --channels=email --debug

# Verify Telegram bot token
python -m notification_service.cli test --channels=telegram --debug

# Check notification logs
python -m notification_service.cli logs --last=20
```

#### 3. Job Scheduler Issues
```bash
# Check Redis connection
redis-cli ping

# View worker status
python -m job_scheduler.cli workers --status

# Restart failed jobs
python -m job_scheduler.cli retry-failed --max-age=1h
```

#### 4. Database Problems
```bash
# Check database integrity
python -m bot_service.cli db check

# View recent database activity
python -m bot_service.cli db logs --last=50

# Backup database
python -m bot_service.cli db backup --output=backup_$(date +%Y%m%d).db
```

### Log Analysis
```bash
# View all service logs
docker-compose logs -f --tail=100

# Filter by service
docker-compose logs bot-service --tail=50

# Search for errors
docker-compose logs | grep ERROR

# Monitor real-time activity
tail -f logs/asylum_bot.log | grep -E "(BOOKING|ERROR|SUCCESS)"
```

### Performance Monitoring
```bash
# Check system resource usage
docker stats

# Monitor Redis queue depth
redis-cli llen celery

# Check database performance
python -m bot_service.cli db stats

# View response time metrics
python -m bot_service.cli metrics --period=1h
```

## Production Deployment

### Security Hardening
```bash
# Generate secure passwords
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set file permissions
chmod 600 .env
chmod 700 logs/

# Configure firewall
sudo ufw allow 22/tcp  # SSH only
sudo ufw enable
```

### Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client grafana-api

# Configure health check endpoints
python -m bot_service.cli configure-monitoring

# Set up alerts
python -m notification_service.cli setup-alerts
```

### Backup Strategy
```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
python -m bot_service.cli db backup --output=backups/asylum_bot_$DATE.db
find backups/ -name "*.db" -mtime +30 -delete

# Schedule daily backups
echo "0 2 * * * /path/to/backup_script.sh" | crontab -
```

## Success Criteria Validation

### Functional Requirements Checklist
- [ ] **FR-001**: Continuous monitoring implemented and tested
- [ ] **FR-002**: Madrid-only office filtering verified
- [ ] **FR-003**: Earliest appointment selection logic tested
- [ ] **FR-004**: Automatic booking execution confirmed
- [ ] **FR-005**: User authentication system working
- [ ] **FR-006**: Notification system delivering alerts
- [ ] **FR-007**: 2-minute monitoring interval configured
- [ ] **FR-008**: Error handling and recovery tested
- [ ] **FR-009**: Rate limiting compliance verified
- [ ] **FR-010**: Comprehensive logging implemented
- [ ] **FR-011**: Monitoring stops after successful booking
- [ ] **FR-012**: Secure credential management
- [ ] **FR-013**: User control over monitoring process
- [ ] **FR-014**: Asylum service filtering validated

### Performance Validation
```bash
# Test monitoring interval accuracy
python -m bot_service.cli test-timing --duration=10m --expected-interval=120

# Measure booking response time
python -m bot_service.cli benchmark-booking --iterations=5

# Validate notification delivery speed
python -m notification_service.cli benchmark --count=10

# Expected Results:
# - Monitoring checks every 120±5 seconds
# - Booking attempts complete in <30 seconds
# - Notifications delivered in <10 seconds
```

### Integration Testing
```bash
# End-to-end test with all services
python -m tests.integration.test_full_workflow --duration=30m

# Expected: Complete appointment discovery and booking simulation
```

## Next Steps

After successful quickstart validation:

1. **Production Configuration**: Review and harden security settings
2. **Monitoring Setup**: Configure alerts and dashboards
3. **Backup Strategy**: Implement automated backup procedures
4. **Documentation**: Create user-specific operating procedures
5. **Support**: Set up support channels and escalation procedures

For additional help, refer to:
- **User Manual**: `docs/user-manual.md`
- **API Documentation**: `docs/api-reference.md`
- **Troubleshooting Guide**: `docs/troubleshooting.md`
- **FAQ**: `docs/frequently-asked-questions.md`
