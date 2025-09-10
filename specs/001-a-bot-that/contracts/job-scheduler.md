# Job Scheduler API Contract

## Overview
The Job Scheduler manages task scheduling, retries, and background job execution for the asylum appointment booking bot. Built on Celery with Redis backend, it handles monitoring tasks, retry logic, and job state management.

## Library Interface

### CLI Commands

#### Start Scheduler
```bash
job-scheduler start --workers=4 --concurrency=2 --output=json
```

**Purpose**: Start the job scheduler with worker processes
**Parameters**:
- `--workers`: Integer, optional, number of worker processes (default: 4)
- `--concurrency`: Integer, optional, tasks per worker (default: 2)
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "scheduler_id": "sched_001",
  "status": "started",
  "workers": 4,
  "concurrency": 2,
  "redis_connected": true,
  "timestamp": "2025-09-09T10:00:00Z"
}
```

#### Schedule Monitoring
```bash
job-scheduler schedule-monitoring --user-id=1 --interval=120 --priority=high --output=json
```

**Purpose**: Schedule recurring monitoring job for a user
**Parameters**:
- `--user-id`: Integer, required, user to monitor for
- `--interval`: Integer, optional, seconds between checks (default: 120)
- `--priority`: String, optional, job priority (low|normal|high, default: normal)
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "job_id": "job_mon_123",
  "task_name": "monitor_appointments",
  "user_id": 1,
  "interval_seconds": 120,
  "priority": "high",
  "status": "scheduled",
  "next_run": "2025-09-09T10:02:00Z",
  "timestamp": "2025-09-09T10:00:00Z"
}
```

#### Schedule Booking
```bash
job-scheduler schedule-booking --slot-id=456 --user-id=1 --delay=0 --output=json
```

**Purpose**: Schedule immediate booking attempt for specific slot
**Parameters**:
- `--slot-id`: Integer, required, appointment slot to book
- `--user-id`: Integer, required, user making the booking
- `--delay`: Integer, optional, seconds to delay execution (default: 0)
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "job_id": "job_book_789",
  "task_name": "attempt_booking",
  "slot_id": 456,
  "user_id": 1,
  "priority": "high",
  "status": "queued",
  "eta": "2025-09-09T10:00:00Z",
  "timestamp": "2025-09-09T10:00:00Z"
}
```

#### Cancel Job
```bash
job-scheduler cancel --job-id=job_mon_123 --output=json
```

**Purpose**: Cancel scheduled or running job
**Parameters**:
- `--job-id`: String, required, job to cancel
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "job_id": "job_mon_123",
  "status": "cancelled",
  "was_running": false,
  "timestamp": "2025-09-09T10:05:00Z"
}
```

#### List Jobs
```bash
job-scheduler list --status=active --user-id=1 --output=json
```

**Purpose**: List jobs matching criteria
**Parameters**:
- `--status`: String, optional, filter by status (active|queued|running|completed|failed|cancelled)
- `--user-id`: Integer, optional, filter by user
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "jobs": [
    {
      "job_id": "job_mon_123",
      "task_name": "monitor_appointments",
      "user_id": 1,
      "status": "running",
      "started_at": "2025-09-09T10:00:00Z",
      "progress": 0.5,
      "next_run": "2025-09-09T10:02:00Z"
    }
  ],
  "total_count": 1,
  "timestamp": "2025-09-09T10:01:00Z"
}
```

#### Get Job Status
```bash
job-scheduler status --job-id=job_mon_123 --output=json
```

**Purpose**: Get detailed status of specific job
**Parameters**:
- `--job-id`: String, required, job to check
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "job_id": "job_mon_123",
  "task_name": "monitor_appointments",
  "status": "running",
  "progress": 0.75,
  "started_at": "2025-09-09T10:00:00Z",
  "estimated_completion": "2025-09-09T10:03:00Z",
  "retry_count": 0,
  "max_retries": 3,
  "last_error": null,
  "result": null
}
```

### Python Library Interface

#### JobScheduler Class
```python
from job_scheduler import JobScheduler, Job

class JobScheduler:
    def __init__(self, redis_url: str, broker_url: str = None):
        """Initialize job scheduler with Redis connection"""
        
    async def start(self, workers: int = 4, concurrency: int = 2) -> bool:
        """Start scheduler and worker processes"""
        
    async def stop(self, graceful: bool = True) -> bool:
        """Stop scheduler and workers"""
        
    async def schedule_monitoring(self, user_id: int, interval: int = 120, priority: str = "normal") -> Job:
        """Schedule recurring appointment monitoring"""
        
    async def schedule_booking(self, slot_id: int, user_id: int, delay: int = 0) -> Job:
        """Schedule immediate booking attempt"""
        
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel scheduled or running job"""
        
    async def get_job_status(self, job_id: str) -> dict:
        """Get detailed job status"""
        
    async def list_jobs(self, status: str = None, user_id: int = None) -> list:
        """List jobs matching criteria"""
```

#### Job Class
```python
class Job:
    def __init__(self, job_id: str, task_name: str, **kwargs):
        """Initialize job instance"""
        
    @property
    def status(self) -> str:
        """Get current job status"""
        
    @property
    def progress(self) -> float:
        """Get job progress (0.0 to 1.0)"""
        
    async def cancel(self) -> bool:
        """Cancel this job"""
        
    async def retry(self) -> bool:
        """Retry failed job"""
        
    def get_result(self) -> dict:
        """Get job result if completed"""
```

### Task Definitions

#### Monitor Appointments Task
```python
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def monitor_appointments(self, user_id: int, office_codes: list = None):
    """Periodic task to check for available appointments"""
    try:
        # Implementation details handled by bot service
        pass
    except Exception as exc:
        # Retry logic with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

#### Attempt Booking Task
```python
@app.task(bind=True, max_retries=3, default_retry_delay=10)
def attempt_booking(self, slot_id: int, user_id: int):
    """One-time task to attempt booking specific slot"""
    try:
        # Implementation details handled by bot service
        pass
    except Exception as exc:
        # Limited retries for booking attempts
        if self.request.retries < 2:
            raise self.retry(exc=exc, countdown=10)
        else:
            # Final failure, notify user
            pass
```

#### Health Check Task
```python
@app.task
def health_check():
    """Periodic health check of system components"""
    return {
        "redis_status": "connected",
        "bot_service_status": "healthy",
        "proxy_manager_status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### Cleanup Task
```python
@app.task
def cleanup_old_jobs():
    """Remove completed/failed jobs older than retention period"""
    pass
```

## Data Contracts

### Job Information Schema
```json
{
  "type": "object",
  "properties": {
    "job_id": {"type": "string"},
    "task_name": {"type": "string"},
    "status": {"type": "string", "enum": ["queued", "running", "completed", "failed", "cancelled", "retry"]},
    "priority": {"type": "string", "enum": ["low", "normal", "high"]},
    "user_id": {"type": "integer"},
    "created_at": {"type": "string", "format": "date-time"},
    "started_at": {"type": "string", "format": "date-time"},
    "completed_at": {"type": "string", "format": "date-time"},
    "progress": {"type": "number", "minimum": 0, "maximum": 1},
    "retry_count": {"type": "integer", "minimum": 0},
    "max_retries": {"type": "integer", "minimum": 0},
    "last_error": {"type": "string"},
    "result": {"type": "object"}
  },
  "required": ["job_id", "task_name", "status", "created_at"]
}
```

### Task Result Schema
```json
{
  "type": "object",
  "properties": {
    "task_name": {"type": "string"},
    "success": {"type": "boolean"},
    "result": {"type": "object"},
    "error_message": {"type": "string"},
    "execution_time_ms": {"type": "integer", "minimum": 0},
    "retry_count": {"type": "integer", "minimum": 0},
    "completed_at": {"type": "string", "format": "date-time"}
  },
  "required": ["task_name", "success", "completed_at"]
}
```

## Integration Points

### Redis Backend
- Job queue management
- Result storage and retrieval
- Worker coordination
- Job state persistence

### Bot Service Integration
- Execute appointment monitoring tasks
- Handle booking attempt requests
- Receive task completion callbacks
- Process retry requests

### Notification Service Integration
- Send alerts on job completion
- Notify on job failures
- Escalate on repeated failures
- Progress updates for long-running tasks

### Database Integration
- Log job execution results
- Store task metadata
- Update user session states
- Maintain job history

## Scheduling Patterns

### Recurring Tasks
- **Appointment Monitoring**: Every 2 minutes during business hours
- **Health Checks**: Every 5 minutes
- **Cleanup Jobs**: Daily at midnight
- **Statistics Collection**: Hourly

### Priority Queues
- **High Priority**: Booking attempts, critical alerts
- **Normal Priority**: Regular monitoring, notifications
- **Low Priority**: Cleanup tasks, statistics

### Retry Strategies
- **Monitoring Tasks**: 3 retries with exponential backoff
- **Booking Tasks**: 2 retries with minimal delay
- **Notification Tasks**: 5 retries with linear backoff
- **Health Checks**: No retries (fast failure)

## Error Handling

### Task Failure Response
```python
# Automatic retry for transient errors
@app.task(bind=True, autoretry_for=(ConnectionError, TimeoutError))
def resilient_task(self):
    pass

# Custom retry logic for specific errors
@app.task(bind=True)
def custom_retry_task(self):
    try:
        # Task logic
        pass
    except SpecificError as exc:
        if should_retry(exc):
            raise self.retry(exc=exc, countdown=calculate_delay())
        else:
            # Permanent failure, notify user
            notify_failure(exc)
```

### Dead Letter Queue
- Failed jobs after max retries
- Manual review and reprocessing
- Error pattern analysis
- Alert on accumulation

### Circuit Breaker Pattern
- Temporary disable tasks on repeated failures
- Automatic recovery after cooldown period
- Escalate to manual intervention
- Prevent cascade failures

## Performance Requirements

### Task Execution
- Monitoring tasks: <30 seconds
- Booking tasks: <60 seconds
- Health checks: <10 seconds
- Cleanup tasks: <5 minutes

### Queue Management
- Job scheduling latency: <1 second
- Queue processing: 10+ jobs per minute
- Worker utilization: >80% during peak hours
- Memory usage: <50MB per worker

### Reliability
- 99.9% task completion rate
- <1% task retry rate
- Recovery from failures: <60 seconds
- Data persistence across restarts

## Monitoring and Observability

### Metrics Collection
- Task execution times
- Success/failure rates
- Queue depths and processing rates
- Worker health and utilization

### Alerting
- High failure rates
- Queue backlog buildup
- Worker process failures
- Redis connection issues

### Debugging Support
- Task execution logs
- Error stack traces
- Performance profiling
- Queue inspection tools
