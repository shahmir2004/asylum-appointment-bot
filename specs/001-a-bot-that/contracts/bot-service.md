# Bot Service API Contract

## Overview
The Bot Service provides core web automation functionality for asylum appointment booking. This service handles site interaction, appointment detection, and booking execution.

## Library Interface

### CLI Commands

#### Start Monitoring
```bash
bot-service monitor --user-id=1 --interval=120 --output=json
```

**Purpose**: Start continuous monitoring for available appointments
**Parameters**:
- `--user-id`: Integer, required, references user profile
- `--interval`: Integer, optional, seconds between checks (default: 120)
- `--output`: String, optional, format for output (json|text, default: json)

**Returns**:
```json
{
  "session_id": 123,
  "status": "started",
  "monitoring_interval": 120,
  "offices_count": 15,
  "timestamp": "2025-09-09T10:00:00Z"
}
```

**Error Cases**:
- Invalid user ID: Exit code 1, stderr message
- Already monitoring: Exit code 2, stderr message  
- Site unreachable: Exit code 3, stderr message

#### Stop Monitoring
```bash
bot-service stop --session-id=123 --output=json
```

**Purpose**: Stop active monitoring session
**Parameters**:
- `--session-id`: Integer, required, active session to stop
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "session_id": 123,
  "status": "stopped",
  "total_checks": 45,
  "duration_minutes": 90,
  "timestamp": "2025-09-09T11:30:00Z"
}
```

#### Check Single Office
```bash
bot-service check-office --office-code=MAD001 --user-id=1 --output=json
```

**Purpose**: Perform one-time check of specific Madrid office
**Parameters**:
- `--office-code`: String, required, office identifier
- `--user-id`: Integer, required, for credential access
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "office_code": "MAD001",
  "office_name": "Madrid Centro",
  "appointments_found": 3,
  "earliest_date": "2025-09-15",
  "earliest_time": "09:30",
  "check_timestamp": "2025-09-09T10:05:00Z",
  "response_time_ms": 2340
}
```

#### Attempt Booking
```bash
bot-service book --slot-id=456 --user-id=1 --output=json
```

**Purpose**: Attempt to book specific appointment slot
**Parameters**:
- `--slot-id`: Integer, required, appointment slot to book
- `--user-id`: Integer, required, for credential access
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "booking_attempt_id": 789,
  "slot_id": 456,
  "status": "success",
  "confirmation_code": "CONF123456",
  "appointment_date": "2025-09-15",
  "appointment_time": "09:30",
  "office_name": "Madrid Centro",
  "timestamp": "2025-09-09T10:06:00Z"
}
```

**Error Cases**:
- Slot no longer available: Exit code 4
- CAPTCHA required: Exit code 5
- Credentials invalid: Exit code 6
- Site error: Exit code 7

#### List Offices
```bash
bot-service list-offices --active-only --output=json
```

**Purpose**: Get list of Madrid offices for asylum appointments
**Parameters**:
- `--active-only`: Boolean flag, optional, only show active offices
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "offices": [
    {
      "office_code": "MAD001",
      "name": "Madrid Centro",
      "district": "Centro",
      "address": "Calle Mayor 1, Madrid",
      "is_active": true,
      "last_checked": "2025-09-09T10:00:00Z"
    }
  ],
  "total_count": 15,
  "active_count": 14
}
```

### Python Library Interface

#### BotService Class
```python
from bot_service import BotService, MonitoringSession

class BotService:
    def __init__(self, db_path: str, proxy_manager=None, captcha_solver=None):
        """Initialize bot service with database and optional services"""
        
    async def start_monitoring(self, user_id: int, interval: int = 120) -> MonitoringSession:
        """Start continuous monitoring for appointments"""
        
    async def stop_monitoring(self, session_id: int) -> dict:
        """Stop active monitoring session"""
        
    async def check_office(self, office_code: str, user_id: int) -> dict:
        """Check single office for appointments"""
        
    async def attempt_booking(self, slot_id: int, user_id: int) -> dict:
        """Attempt to book specific appointment slot"""
        
    async def list_offices(self, active_only: bool = True) -> list:
        """Get list of Madrid offices"""
```

#### MonitoringSession Class
```python
class MonitoringSession:
    def __init__(self, session_id: int, user_id: int, interval: int):
        """Initialize monitoring session"""
        
    async def run(self) -> None:
        """Execute monitoring loop"""
        
    async def pause(self) -> None:
        """Pause monitoring temporarily"""
        
    async def resume(self) -> None:
        """Resume paused monitoring"""
        
    def get_status(self) -> dict:
        """Get current session status"""
```

### Event Callbacks

#### Appointment Found Event
```python
@callback
def on_appointment_found(office_code: str, slots: list) -> None:
    """Called when new appointments are discovered"""
    
@callback  
def on_booking_success(booking_result: dict) -> None:
    """Called when appointment successfully booked"""
    
@callback
def on_booking_failure(error_info: dict) -> None:
    """Called when booking attempt fails"""
    
@callback
def on_site_error(error_info: dict) -> None:
    """Called when site interaction fails"""
```

## Data Contracts

### Appointment Slot Schema
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "office_code": {"type": "string", "pattern": "^MAD[0-9]{3}$"},
    "office_name": {"type": "string"},
    "appointment_date": {"type": "string", "format": "date"},
    "appointment_time": {"type": "string", "format": "time"},
    "slot_type": {"type": "string", "enum": ["asylum_initial", "asylum_renewal"]},
    "is_available": {"type": "boolean"},
    "discovered_at": {"type": "string", "format": "date-time"}
  },
  "required": ["id", "office_code", "appointment_date", "appointment_time", "slot_type"]
}
```

### Booking Result Schema
```json
{
  "type": "object",
  "properties": {
    "booking_attempt_id": {"type": "integer"},
    "slot_id": {"type": "integer"},
    "status": {"type": "string", "enum": ["success", "failed", "timeout"]},
    "confirmation_code": {"type": "string", "minLength": 6},
    "error_type": {"type": "string", "enum": ["captcha", "credentials", "network", "site_error"]},
    "error_message": {"type": "string"},
    "response_time_ms": {"type": "integer", "minimum": 0},
    "timestamp": {"type": "string", "format": "date-time"}
  },
  "required": ["booking_attempt_id", "slot_id", "status", "timestamp"]
}
```

## Integration Points

### Database Interactions
- Read user credentials for site authentication
- Store discovered appointment slots
- Log all booking attempts and results
- Update session status and statistics

### External Service Dependencies
- Proxy Manager: IP rotation for stealth
- CAPTCHA Solver: Handle anti-bot challenges
- Notification Service: Alert on booking success/failure

### Government Site Integration
- Login form automation
- Office selection navigation
- Appointment calendar parsing
- Booking form submission
- Confirmation page extraction

## Error Handling

### Retry Strategies
- Network timeouts: 3 retries with exponential backoff
- CAPTCHA challenges: Single retry with different solver
- Site errors: 5 retries with increasing delays
- Credential failures: No retry, require user intervention

### Error Classification
- **Temporary**: Network issues, site maintenance, CAPTCHA
- **Permanent**: Invalid credentials, slot no longer available
- **Critical**: Site structure changes, anti-bot detection

### Fallback Behaviors
- Switch to backup proxy on IP ban
- Reduce check frequency on repeated errors
- Notify user of persistent failures
- Graceful degradation of monitoring

## Performance Requirements

### Response Times
- Office check: <10 seconds per office
- Booking attempt: <30 seconds total
- Session startup: <5 seconds
- Status queries: <1 second

### Concurrency
- Maximum 3 concurrent office checks
- Single booking attempt per session
- Non-blocking status queries
- Background cleanup operations

### Resource Usage
- Memory: <100MB per monitoring session
- CPU: <20% during active monitoring
- Network: <1MB per office check
- Storage: <10MB per month of logs
