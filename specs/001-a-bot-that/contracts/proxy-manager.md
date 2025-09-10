# Proxy Manager API Contract

## Overview
The Proxy Manager handles IP rotation and stealth measures to avoid detection by the government booking site. This service manages proxy pools, rotation strategies, and request anonymization.

## Library Interface

### CLI Commands

#### Start Proxy Pool
```bash
proxy-manager start --pool-size=10 --rotation-strategy=round-robin --output=json
```

**Purpose**: Initialize and start proxy pool management
**Parameters**:
- `--pool-size`: Integer, optional, number of proxies to maintain (default: 10)
- `--rotation-strategy`: String, optional, rotation method (round-robin|random|least-used, default: round-robin)
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "pool_id": "pool_001",
  "status": "started",
  "pool_size": 10,
  "active_proxies": 8,
  "rotation_strategy": "round-robin",
  "timestamp": "2025-09-09T10:00:00Z"
}
```

#### Get Proxy
```bash
proxy-manager get-proxy --pool-id=pool_001 --sticky-session=false --output=json
```

**Purpose**: Request a proxy for use
**Parameters**:
- `--pool-id`: String, required, proxy pool identifier
- `--sticky-session`: Boolean, optional, maintain same proxy for session (default: false)
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "proxy_id": "proxy_123",
  "proxy_url": "http://user:pass@192.168.1.100:8080",
  "country": "ES",
  "city": "Madrid",
  "is_residential": true,
  "last_used": "2025-09-09T09:55:00Z",
  "success_rate": 0.95,
  "assigned_at": "2025-09-09T10:00:00Z"
}
```

#### Release Proxy
```bash
proxy-manager release --proxy-id=proxy_123 --success=true --response-time=2340 --output=json
```

**Purpose**: Return proxy to pool with usage statistics
**Parameters**:
- `--proxy-id`: String, required, proxy to release
- `--success`: Boolean, required, whether request was successful
- `--response-time`: Integer, optional, response time in milliseconds
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "proxy_id": "proxy_123",
  "status": "released",
  "updated_success_rate": 0.96,
  "total_requests": 47,
  "timestamp": "2025-09-09T10:02:00Z"
}
```

#### Health Check
```bash
proxy-manager health --pool-id=pool_001 --output=json
```

**Purpose**: Check health status of proxy pool
**Parameters**:
- `--pool-id`: String, required, proxy pool to check
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "pool_id": "pool_001",
  "total_proxies": 10,
  "healthy_proxies": 8,
  "unhealthy_proxies": 2,
  "average_response_time": 1850,
  "average_success_rate": 0.92,
  "last_health_check": "2025-09-09T10:00:00Z"
}
```

#### Rotate Pool
```bash
proxy-manager rotate --pool-id=pool_001 --force=false --output=json
```

**Purpose**: Force rotation of proxy pool
**Parameters**:
- `--pool-id`: String, required, proxy pool to rotate
- `--force`: Boolean, optional, force rotation even if proxies are healthy
- `--output`: String, optional, format for output

**Returns**:
```json
{
  "pool_id": "pool_001",
  "proxies_replaced": 3,
  "new_pool_size": 10,
  "rotation_reason": "scheduled_rotation",
  "timestamp": "2025-09-09T10:05:00Z"
}
```

### Python Library Interface

#### ProxyManager Class
```python
from proxy_manager import ProxyManager, ProxyPool

class ProxyManager:
    def __init__(self, config: dict):
        """Initialize proxy manager with configuration"""
        
    async def create_pool(self, pool_size: int = 10, strategy: str = "round-robin") -> ProxyPool:
        """Create and start new proxy pool"""
        
    async def get_proxy(self, pool_id: str, sticky_session: bool = False) -> ProxyInfo:
        """Get proxy from pool for use"""
        
    async def release_proxy(self, proxy_id: str, success: bool, response_time: int = None) -> None:
        """Release proxy back to pool with stats"""
        
    async def health_check(self, pool_id: str) -> dict:
        """Check health of proxy pool"""
        
    async def rotate_pool(self, pool_id: str, force: bool = False) -> dict:
        """Rotate proxies in pool"""
```

#### ProxyPool Class
```python
class ProxyPool:
    def __init__(self, pool_id: str, size: int, strategy: str):
        """Initialize proxy pool"""
        
    async def get_proxy(self, sticky_session: bool = False) -> ProxyInfo:
        """Get next proxy from pool"""
        
    async def release_proxy(self, proxy_info: ProxyInfo, success: bool, response_time: int = None) -> None:
        """Return proxy to pool"""
        
    async def add_proxy(self, proxy_config: dict) -> bool:
        """Add new proxy to pool"""
        
    async def remove_proxy(self, proxy_id: str) -> bool:
        """Remove proxy from pool"""
        
    def get_stats(self) -> dict:
        """Get pool statistics"""
```

#### ProxyInfo Class
```python
class ProxyInfo:
    def __init__(self, proxy_id: str, url: str, country: str, city: str):
        """Initialize proxy information"""
        
    @property
    def is_healthy(self) -> bool:
        """Check if proxy is healthy based on recent performance"""
        
    @property
    def success_rate(self) -> float:
        """Get current success rate (0.0 to 1.0)"""
        
    def update_stats(self, success: bool, response_time: int = None) -> None:
        """Update proxy performance statistics"""
```

### Configuration Interface

#### Proxy Provider Config
```python
PROXY_CONFIG = {
    "providers": [
        {
            "name": "residential_provider_1",
            "type": "residential",
            "endpoint": "https://api.provider1.com/proxies",
            "auth": {
                "username": "user",
                "password": "pass"
            },
            "locations": ["ES-Madrid", "ES-Barcelona"],
            "rotation_minutes": 30
        }
    ],
    "pool_settings": {
        "default_size": 10,
        "max_size": 50,
        "health_check_interval": 300,
        "rotation_interval": 1800,
        "failure_threshold": 0.7
    },
    "request_settings": {
        "timeout_seconds": 30,
        "max_retries": 3,
        "user_agents": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]
    }
}
```

## Data Contracts

### Proxy Information Schema
```json
{
  "type": "object",
  "properties": {
    "proxy_id": {"type": "string"},
    "proxy_url": {"type": "string", "format": "uri"},
    "country": {"type": "string", "minLength": 2, "maxLength": 2},
    "city": {"type": "string"},
    "is_residential": {"type": "boolean"},
    "success_rate": {"type": "number", "minimum": 0, "maximum": 1},
    "last_used": {"type": "string", "format": "date-time"},
    "response_time_avg": {"type": "integer", "minimum": 0},
    "total_requests": {"type": "integer", "minimum": 0},
    "is_healthy": {"type": "boolean"}
  },
  "required": ["proxy_id", "proxy_url", "country", "is_residential"]
}
```

### Pool Statistics Schema
```json
{
  "type": "object",
  "properties": {
    "pool_id": {"type": "string"},
    "total_proxies": {"type": "integer", "minimum": 0},
    "healthy_proxies": {"type": "integer", "minimum": 0},
    "unhealthy_proxies": {"type": "integer", "minimum": 0},
    "average_response_time": {"type": "integer", "minimum": 0},
    "average_success_rate": {"type": "number", "minimum": 0, "maximum": 1},
    "requests_per_minute": {"type": "number", "minimum": 0},
    "last_rotation": {"type": "string", "format": "date-time"},
    "next_rotation": {"type": "string", "format": "date-time"}
  },
  "required": ["pool_id", "total_proxies", "healthy_proxies", "unhealthy_proxies"]
}
```

## Integration Points

### External Proxy Providers
- Authenticate with proxy service APIs
- Fetch available proxy lists
- Monitor proxy health and performance
- Handle provider-specific rotation requirements

### Bot Service Integration
- Provide proxies for web automation requests
- Receive feedback on proxy performance
- Handle proxy failures during booking attempts
- Support sticky sessions for multi-step processes

### Health Monitoring
- Continuous health checks of all proxies
- Performance metrics collection
- Automatic removal of failed proxies
- Alert on low proxy availability

## Stealth Features

### IP Rotation Strategies
- **Round Robin**: Cycle through proxies in order
- **Random**: Select random proxy for each request
- **Least Used**: Prefer proxies with lowest usage
- **Performance Based**: Prefer proxies with best performance

### Request Anonymization
- Random user agent selection
- Browser fingerprint randomization
- Request timing variation
- Header order randomization

### Detection Avoidance
- Proxy warmup before use
- Gradual request ramp-up
- Geographic consistency (Madrid-based IPs preferred)
- Session persistence for multi-step flows

## Error Handling

### Proxy Failure Response
- Automatic failover to backup proxy
- Blacklist failed proxies temporarily
- Escalate to different proxy provider
- Graceful degradation if no proxies available

### Rate Limiting
- Respect proxy provider limits
- Implement backoff on provider errors
- Queue requests during high usage
- Load balance across multiple providers

### Recovery Strategies
- Automatic proxy pool refresh
- Provider failover mechanisms
- Emergency direct connection (last resort)
- User notification of service degradation

## Performance Requirements

### Response Times
- Proxy assignment: <500ms
- Health check: <10 seconds
- Pool rotation: <30 seconds
- Statistics queries: <1 second

### Availability
- 99% proxy availability during business hours
- <5% proxy failure rate
- Automatic recovery within 60 seconds
- Maximum 30 seconds between retries

### Scalability
- Support up to 100 concurrent proxy requests
- Handle 1000+ requests per hour per proxy
- Dynamic pool sizing based on demand
- Multi-provider load balancing
