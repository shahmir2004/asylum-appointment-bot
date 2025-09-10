# icpBot Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-09

## Active Technologies
- Python 3.11+ with Playwright for web automation
- Celery + Redis for job scheduling and task queues
- SQLite for local data persistence
- Docker + docker-compose for microservice deployment
- undetected-playwright for stealth web scraping
- 2captcha/hCaptcha for CAPTCHA solving
- SMTP + Telegram Bot API for notifications
- Proxy rotation for anti-detection measures

## Project Structure
```
src/
├── bot_service/          # Core web automation service
├── proxy_manager/        # IP rotation and stealth management
├── job_scheduler/        # Celery-based task scheduling
├── notification_service/ # Multi-channel alert system
├── models/              # Database models and schemas
├── cli/                 # Command-line interfaces
└── lib/                 # Shared utilities and helpers

tests/
├── contract/            # API contract tests
├── integration/         # Service integration tests
└── unit/               # Unit tests

specs/001-a-bot-that/    # Current feature documentation
├── spec.md             # Feature specification
├── plan.md             # Implementation plan
├── research.md         # Technology research
├── data-model.md       # Database schema
├── quickstart.md       # User guide
└── contracts/          # Service API contracts
```

## Commands
```bash
# Bot Service CLI
bot-service monitor --user-id=1 --interval=120
bot-service check-office --office-code=MAD001 --user-id=1
bot-service book --slot-id=456 --user-id=1
bot-service list-offices --active-only

# Job Scheduler CLI
job-scheduler schedule-monitoring --user-id=1 --interval=120 --priority=high
job-scheduler schedule-booking --slot-id=456 --user-id=1
job-scheduler cancel --job-id=job_mon_123
job-scheduler list --status=active

# Proxy Manager CLI
proxy-manager start --pool-size=10 --rotation-strategy=round-robin
proxy-manager get-proxy --pool-id=pool_001
proxy-manager health --pool-id=pool_001

# Notification Service CLI
notification-service send --user-id=1 --type=booking_success --template=appointment_booked
notification-service test --channels=email,telegram
```

## Code Style
- Python: Follow PEP 8, use type hints, async/await patterns
- Error handling: Use custom exceptions with detailed context
- Logging: Structured JSON logs with correlation IDs
- Testing: TDD approach - write tests first, then implementation
- Database: Use SQLAlchemy ORM with explicit schema migrations
- API: REST-style with JSON request/response, OpenAPI documentation

## Architecture Principles
- Library-first: Every feature as standalone library with CLI
- Microservices: Separate services for bot, proxy, scheduler, notifications
- Stealth-first: All web interactions through proxy rotation and fingerprint randomization
- Resilient: Retry mechanisms, circuit breakers, graceful degradation
- Observable: Comprehensive logging, metrics, health checks
- Testable: Contract tests, integration tests, end-to-end validation

## Recent Changes
- 001-a-bot-that: Added asylum appointment booking bot with Python + Playwright + Docker architecture

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->