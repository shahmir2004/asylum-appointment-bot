# Tasks: Asylum Appointment Booking Bot MVP

**Input**: Design documents from `/specs/001-a-bot-that/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## MVP Scope
**Simplified for rapid delivery**: Single Python script that monitors one Madrid office, sends email notifications, no proxy/CAPTCHA/Docker complexity. Focus on core booking flow with provided Gmail credentials.

**Environment Variables Provided**:
```bash
EMAIL_ADDRESS=shahmirahmed.004@gmail.com
EMAIL_PASSWORD=qljvlajlwljwbvdv
RECIPIENT_EMAIL=shahmirahmed.004@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## Path Conventions
**Single project structure**: `src/` and `tests/` at repository root per plan.md

## Phase 3.1: MVP Setup
- [ ] **T001** Create minimal project structure with src/, tests/, logs/ directories
- [ ] **T002** Initialize Python project with requirements.txt (playwright, sqlite3, smtplib, schedule)
- [ ] **T003** [P] Create .env file with provided email credentials and basic configuration
- [ ] **T004** [P] Configure basic logging to logs/asylum_bot.log file

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] **T005** [P] Test email notification in tests/test_notifications.py (must fail initially)
- [ ] **T006** [P] Test Madrid office detection in tests/test_site_scraping.py (must fail initially)  
- [ ] **T007** [P] Test appointment slot parsing in tests/test_appointment_parsing.py (must fail initially)
- [ ] **T008** [P] Test booking attempt in tests/test_booking.py (must fail initially)
- [ ] **T009** [P] Integration test full workflow in tests/test_integration.py (must fail initially)

## Phase 3.3: Core MVP Implementation (ONLY after tests are failing)
- [ ] **T010** [P] Simple database models in src/models.py (UserProfile, MadridOffice, AppointmentSlot, BookingAttempt)
- [ ] **T011** [P] Email notification service in src/notifications.py using provided Gmail SMTP settings
- [ ] **T012** [P] Basic site scraper in src/scraper.py using Playwright for icp.administracionelectronica.gob.es
- [ ] **T013** [P] Appointment booking logic in src/booking.py for single Madrid office
- [ ] **T014** Main monitoring script in src/main.py that ties everything together
- [ ] **T015** Simple CLI interface in src/cli.py for start/stop monitoring
- [ ] **T016** Configuration management in src/config.py for environment variables
- [ ] **T017** Database initialization in src/database.py with SQLite setup

## Phase 3.4: MVP Integration
- [ ] **T018** Connect all components in main.py monitoring loop (every 2 minutes)
- [ ] **T019** Add error handling and basic retry logic for network failures
- [ ] **T020** Implement basic logging for all operations (scanning, booking attempts, emails)
- [ ] **T021** Add graceful shutdown handling (Ctrl+C to stop monitoring)

## Phase 3.5: MVP Polish & Validation
- [ ] **T022** [P] Unit tests for individual components (models, notifications, config)
- [ ] **T023** [P] Create README.md with MVP setup and usage instructions
- [ ] **T024** [P] Create run.py script for easy startup with python run.py
- [ ] **T025** Manual testing with actual government site (test connection only, no real booking)
- [ ] **T026** Validate email notifications work with provided Gmail credentials

## Dependencies
- Setup (T001-T004) must complete first
- Tests (T005-T009) before any implementation (T010+)
- Models (T010) before services (T011-T017)
- Integration (T018-T021) requires all core components
- Polish (T022-T026) comes last

## Parallel Execution Examples
```bash
# Phase 3.1 parallel setup:
Task: "Create .env file with provided email credentials"
Task: "Configure basic logging to logs/asylum_bot.log file"

# Phase 3.2 parallel test creation:
Task: "Test email notification in tests/test_notifications.py"
Task: "Test Madrid office detection in tests/test_site_scraping.py"
Task: "Test appointment slot parsing in tests/test_appointment_parsing.py"
Task: "Test booking attempt in tests/test_booking.py"
Task: "Integration test full workflow in tests/test_integration.py"

# Phase 3.3 parallel core implementation:
Task: "Simple database models in src/models.py"
Task: "Email notification service in src/notifications.py"
Task: "Basic site scraper in src/scraper.py"
Task: "Appointment booking logic in src/booking.py"
```

## MVP File Structure
```
asylum-appointment-bot/
├── src/
│   ├── models.py          # SQLite models (UserProfile, MadridOffice, AppointmentSlot, BookingAttempt)
│   ├── notifications.py   # Email service using provided Gmail SMTP
│   ├── scraper.py         # Playwright scraper for government site
│   ├── booking.py         # Appointment booking logic
│   ├── config.py          # Environment variable management
│   ├── database.py        # SQLite setup and migrations
│   ├── cli.py             # Simple command-line interface
│   └── main.py            # Main monitoring loop
├── tests/
│   ├── test_notifications.py    # Email notification tests
│   ├── test_site_scraping.py    # Site interaction tests
│   ├── test_appointment_parsing.py  # Appointment parsing tests
│   ├── test_booking.py           # Booking logic tests
│   └── test_integration.py      # Full workflow tests
├── logs/
│   └── asylum_bot.log     # Application logs
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── run.py                 # Easy startup script
├── README.md              # Setup and usage guide
└── asylum_bot.db          # SQLite database (created at runtime)
```

## MVP Core Functionality
1. **Monitor**: Check single Madrid office every 2 minutes for appointments
2. **Detect**: Parse appointment availability from government site
3. **Book**: Attempt to book earliest available appointment (simulated for MVP)
4. **Notify**: Send email confirmation using provided Gmail credentials
5. **Log**: Record all activities for debugging and monitoring

## Success Criteria for MVP
- [ ] Successfully connects to icp.administracionelectronica.gob.es
- [ ] Detects appointment availability (or lack thereof) for one Madrid office
- [ ] Sends test email notifications using provided Gmail credentials
- [ ] Logs all operations clearly for debugging
- [ ] Runs continuously with 2-minute intervals until stopped
- [ ] Handles basic errors gracefully (network timeouts, site changes)

## Excluded from MVP (Future Enhancements)
- Multiple office monitoring (start with one for simplicity)
- Proxy rotation and stealth features
- CAPTCHA solving integration
- Celery/Redis job scheduling
- Docker containerization
- Telegram notifications
- Advanced retry strategies
- Real-time booking execution (simulate for safety)

## Notes
- **Safety First**: MVP will simulate booking attempts rather than actually booking
- **Test Carefully**: Use test credentials for government site interaction
- **Incremental**: Each task should be small and immediately testable
- **Fail Fast**: Let tests fail initially to ensure TDD compliance
- **Keep Simple**: Resist urge to add complexity until MVP is working
