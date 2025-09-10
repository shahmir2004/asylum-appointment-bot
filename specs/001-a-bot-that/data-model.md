# Data Model: Asylum Appointment Booking Bot

**Date**: September 9, 2025  
**Feature**: Automated asylum appointment booking for Madrid offices  
**Status**: Phase 1 Design

## Core Entities

### User Profile
Represents the person seeking asylum appointment booking.

**Fields**:
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `email`: TEXT NOT NULL (notification recipient)
- `telegram_chat_id`: TEXT NULL (optional Telegram notifications)
- `credentials_encrypted`: TEXT NOT NULL (encrypted government site credentials)
- `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `updated_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `is_active`: BOOLEAN DEFAULT TRUE

**Validation Rules**:
- Email must be valid format
- Credentials must be encrypted before storage
- Only one active user profile per bot instance

**State Transitions**:
- Created → Active (when credentials validated)
- Active → Inactive (when user stops monitoring)
- Active → Error (when credentials fail validation)

### Madrid Office
Represents a government office in Madrid that handles asylum appointments.

**Fields**:
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `name`: TEXT NOT NULL (official office name)
- `address`: TEXT NOT NULL (physical address)
- `district`: TEXT NOT NULL (Madrid district/area)
- `office_code`: TEXT UNIQUE NOT NULL (government site identifier)
- `is_active`: BOOLEAN DEFAULT TRUE (office still operational)
- `last_checked`: DATETIME NULL (last scan timestamp)
- `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP

**Validation Rules**:
- Office code must be unique and not empty
- Name must be non-empty
- Address must be Madrid-based

**Relationships**:
- One-to-many with AppointmentSlot
- One-to-many with BookingAttempt

### Appointment Slot
Represents an available appointment time slot at a Madrid office.

**Fields**:
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `office_id`: INTEGER NOT NULL (foreign key to Madrid Office)
- `appointment_date`: DATE NOT NULL
- `appointment_time`: TIME NOT NULL
- `slot_type`: TEXT NOT NULL (e.g., "asylum_initial", "asylum_renewal")
- `is_available`: BOOLEAN DEFAULT TRUE
- `discovered_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `expires_at`: DATETIME NULL (when slot is no longer bookable)
- `booking_reference`: TEXT NULL (if successfully booked)

**Validation Rules**:
- Appointment date must be in the future
- Slot type must be asylum-related
- Office ID must reference valid Madrid office

**Relationships**:
- Many-to-one with MadridOffice
- One-to-many with BookingAttempt

**State Transitions**:
- Discovered → Available (when first detected)
- Available → Booking (when bot attempts to book)
- Booking → Booked (when successfully reserved)
- Booking → Failed (when booking attempt fails)
- Available → Expired (when slot is no longer available)

### Booking Session
Represents a monitoring session where the bot continuously scans for appointments.

**Fields**:
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `user_id`: INTEGER NOT NULL (foreign key to User Profile)
- `status`: TEXT NOT NULL (active, paused, completed, error)
- `started_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `ended_at`: DATETIME NULL
- `check_interval_seconds`: INTEGER DEFAULT 120 (2 minutes)
- `total_checks_performed`: INTEGER DEFAULT 0
- `successful_booking_id`: INTEGER NULL (foreign key to BookingAttempt)
- `error_message`: TEXT NULL
- `last_activity`: DATETIME DEFAULT CURRENT_TIMESTAMP

**Validation Rules**:
- Check interval must be at least 30 seconds (respect rate limits)
- Status must be one of predefined values
- User ID must reference valid user

**Relationships**:
- Many-to-one with UserProfile
- One-to-many with BookingAttempt
- One-to-one with successful BookingAttempt (optional)

**State Transitions**:
- Created → Active (when monitoring starts)
- Active → Paused (when user pauses monitoring)
- Paused → Active (when user resumes)
- Active → Completed (when appointment successfully booked)
- Active → Error (when unrecoverable error occurs)

### Booking Attempt
Represents an attempt to book a specific appointment slot.

**Fields**:
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `session_id`: INTEGER NOT NULL (foreign key to Booking Session)
- `slot_id`: INTEGER NOT NULL (foreign key to Appointment Slot)
- `attempt_timestamp`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `status`: TEXT NOT NULL (pending, success, failed, timeout)
- `error_type`: TEXT NULL (captcha, credentials, network, site_error)
- `error_message`: TEXT NULL
- `response_time_ms`: INTEGER NULL
- `confirmation_code`: TEXT NULL (if booking successful)
- `captcha_solved`: BOOLEAN DEFAULT FALSE
- `proxy_used`: TEXT NULL (proxy IP if used)

**Validation Rules**:
- Status must be one of predefined values
- Error type required if status is failed
- Confirmation code required if status is success

**Relationships**:
- Many-to-one with BookingSession
- Many-to-one with AppointmentSlot

**State Transitions**:
- Created → Pending (when attempt starts)
- Pending → Success (when booking confirmed)
- Pending → Failed (when booking fails)
- Pending → Timeout (when attempt times out)

### Notification Log
Tracks all notifications sent to the user.

**Fields**:
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `user_id`: INTEGER NOT NULL (foreign key to User Profile)
- `notification_type`: TEXT NOT NULL (email, telegram, error)
- `subject`: TEXT NOT NULL
- `message`: TEXT NOT NULL
- `sent_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `delivery_status`: TEXT DEFAULT 'pending' (pending, sent, failed)
- `external_reference`: TEXT NULL (email ID, Telegram message ID)
- `retry_count`: INTEGER DEFAULT 0

**Validation Rules**:
- Notification type must be supported channel
- Message must not be empty
- Retry count cannot exceed 3

**Relationships**:
- Many-to-one with UserProfile

### System Configuration
Stores bot configuration and operational parameters.

**Fields**:
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `key`: TEXT UNIQUE NOT NULL
- `value`: TEXT NOT NULL
- `description`: TEXT NULL
- `updated_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `is_encrypted`: BOOLEAN DEFAULT FALSE

**Validation Rules**:
- Key must be unique and follow naming convention
- Encrypted values must be properly encoded

**Common Configuration Keys**:
- `check_interval_seconds`: Default monitoring interval
- `max_retry_attempts`: Maximum booking retry attempts
- `proxy_rotation_enabled`: Enable/disable proxy usage
- `captcha_service_enabled`: Enable/disable CAPTCHA solving
- `notification_channels`: Active notification methods

## Database Schema Relationships

```sql
-- Foreign Key Constraints
AppointmentSlot.office_id → MadridOffice.id
BookingSession.user_id → UserProfile.id
BookingAttempt.session_id → BookingSession.id
BookingAttempt.slot_id → AppointmentSlot.id
NotificationLog.user_id → UserProfile.id
BookingSession.successful_booking_id → BookingAttempt.id
```

## Data Access Patterns

### High Frequency Operations
1. **Appointment Scanning**: Query all active Madrid offices for last check time
2. **Slot Discovery**: Insert new appointment slots when found
3. **Booking Attempts**: Insert booking attempt records
4. **Session Updates**: Update last activity timestamp

### Medium Frequency Operations
1. **Session Management**: Start/stop/pause monitoring sessions
2. **Configuration Updates**: Modify system parameters
3. **Notification Sending**: Insert notification log entries

### Low Frequency Operations
1. **User Management**: Create/update user profiles
2. **Office Management**: Add/update Madrid office information
3. **Historical Analysis**: Query booking success rates and patterns

## Data Retention Policy

### Immediate Cleanup
- Failed booking attempts older than 7 days
- Expired appointment slots older than 1 day
- Notification logs older than 30 days

### Long-term Retention
- User profiles: Until user deletion request
- Successful booking records: 1 year for reference
- System configuration: Indefinitely
- Madrid office data: Indefinitely (reference data)

### Privacy Considerations
- All user credentials encrypted at rest
- Personal information limited to operational needs
- Audit trail for data access and modifications
- Support for user data deletion (GDPR compliance)

## Performance Considerations

### Indexing Strategy
```sql
-- High-frequency query indexes
CREATE INDEX idx_appointment_slots_office_date ON AppointmentSlot(office_id, appointment_date);
CREATE INDEX idx_booking_attempts_session_timestamp ON BookingAttempt(session_id, attempt_timestamp);
CREATE INDEX idx_madrid_offices_active ON MadridOffice(is_active);
CREATE INDEX idx_booking_sessions_status ON BookingSession(status, last_activity);
```

### Query Optimization
- Use prepared statements for repeated queries
- Limit result sets for historical data queries
- Implement connection pooling for concurrent access
- Regular VACUUM operations for SQLite maintenance

## Data Migration Strategy

### Version 0.1.0 → 0.2.0
- Add new fields with defaults
- Create migration scripts for schema changes
- Backup existing data before migration
- Rollback procedures for failed migrations

### Deployment Considerations
- Database initialization scripts
- Seed data for Madrid offices
- Configuration defaults setup
- Health check queries for monitoring
