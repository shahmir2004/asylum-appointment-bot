# Research Report: Asylum Appointment Booking Bot

**Date**: September 9, 2025  
**Feature**: Automated asylum appointment booking for Madrid offices  
**Status**: Phase 0 Complete

## Research Findings

### Web Automation Technology Decision
**Decision**: Playwright with undetected-playwright wrapper  
**Rationale**: 
- Faster and more reliable than Selenium for modern web applications
- Better headless mode support with stealth capabilities
- Superior handling of dynamic JavaScript content typical in government sites
- Active development and maintenance for anti-detection features
- Built-in support for multiple browser engines (Chromium, Firefox, WebKit)

**Alternatives considered**:
- Selenium: Slower, more detectable, larger resource footprint
- Requests + BeautifulSoup: Cannot handle JavaScript-heavy sites like government portals
- Scrapy: Excellent for static content but limited JavaScript support

### CAPTCHA Handling Strategy
**Decision**: 2captcha service integration with hCaptcha solver fallback  
**Rationale**:
- Government sites commonly implement CAPTCHA challenges
- 2captcha offers reliable human-powered solving with API integration
- hCaptcha support for newer challenge types
- Cost-effective compared to manual intervention delays

**Alternatives considered**:
- OCR-based solutions: Unreliable for modern CAPTCHA types
- Machine learning approaches: Complex implementation, detection risk
- Manual intervention: Defeats automation purpose

### Stealth and Anti-Detection
**Decision**: Multi-layered approach with proxy rotation and browser fingerprint randomization  
**Rationale**:
- Government sites likely implement bot detection measures
- Residential proxies provide legitimate IP addresses
- Browser fingerprint randomization prevents tracking
- Request timing variation mimics human behavior

**Alternatives considered**:
- VPN-only approach: Limited IP variety, potential for mass blocking
- No stealth measures: High risk of detection and blocking
- TOR network: Too slow for real-time appointment booking

### Task Scheduling and Concurrency
**Decision**: Celery with Redis as message broker  
**Rationale**:
- Mature task queue system with retry mechanisms
- Redis provides fast in-memory storage for task state
- Built-in support for periodic tasks and scheduling
- Horizontal scaling capability if needed

**Alternatives considered**:
- APScheduler: Simpler but less robust for production use
- Custom threading: Complex error handling and state management
- Cron jobs: Limited state management and error recovery

### Data Storage Strategy
**Decision**: SQLite for local data persistence  
**Rationale**:
- Lightweight, serverless database perfect for single-user applications
- ACID compliance ensures data integrity for booking attempts
- No additional server infrastructure required
- Easy backup and migration

**Alternatives considered**:
- PostgreSQL: Overkill for single-user application
- File-based storage: No transaction support, complex querying
- In-memory only: Data loss risk on restart

### Notification System
**Decision**: Multi-channel approach (Email + Telegram Bot API)  
**Rationale**:
- Email provides reliable delivery with detailed information
- Telegram offers instant mobile notifications
- Multiple channels ensure message delivery
- Both support rich formatting for appointment details

**Alternatives considered**:
- SMS: More expensive, limited formatting options
- Push notifications: Requires mobile app development
- Webhook-only: Requires additional service integration

### Deployment Architecture
**Decision**: Docker microservices with docker-compose orchestration  
**Rationale**:
- Each service can scale independently
- Isolated environments prevent service conflicts
- Easy deployment to various cloud providers or VPS
- Configuration management through environment variables

**Alternatives considered**:
- Monolithic deployment: Harder to scale and maintain
- Kubernetes: Overkill for single-user application
- Manual installation: Complex dependency management

### Rate Limiting and Ethical Considerations
**Decision**: Configurable delays with respect for site resources  
**Rationale**:
- 2-minute default intervals balance responsiveness with site respect
- Exponential backoff on errors prevents overwhelming the site
- Monitoring for rate limit responses to adjust behavior
- Ethical automation that doesn't deny service to manual users

**Alternatives considered**:
- Aggressive polling: Risk of blocking and unethical resource usage
- Manual checking: Defeats automation purpose
- Random intervals: Less predictable but potentially less detectable

## Technical Risk Assessment

### High Risk Areas
1. **Site Structure Changes**: Government sites may update without notice
   - Mitigation: Robust element selection with fallbacks, monitoring alerts
2. **Anti-Bot Measures**: Increasing sophistication of detection systems
   - Mitigation: Regular updates to stealth measures, proxy rotation
3. **Legal Compliance**: Automated booking may violate terms of service
   - Mitigation: Review site terms, implement respectful rate limiting

### Medium Risk Areas
1. **Proxy Service Reliability**: External dependency for stealth operation
   - Mitigation: Multiple proxy providers, fallback mechanisms
2. **CAPTCHA Solving Delays**: External service response times
   - Mitigation: Timeout handling, alternative solvers

### Low Risk Areas
1. **Technical Implementation**: Well-established technology stack
2. **Data Storage**: Simple local database requirements

## Performance Targets

### Response Time Goals
- Appointment detection: <10 seconds per office scan
- Booking completion: <30 seconds from detection to confirmation
- System restart: <60 seconds to resume monitoring

### Reliability Goals
- 99.5% uptime during business hours (8 AM - 8 PM Madrid time)
- <0.1% false positive rate for appointment detection
- <5% failed booking rate due to technical issues

### Scalability Considerations
- Single user per instance (current scope)
- Potential for multi-user deployment with authentication layer
- Horizontal scaling through additional bot instances

## Integration Requirements

### Government Site Integration
- Form submission automation for appointment booking
- Session management for authenticated access
- Error page detection and handling
- Appointment confirmation extraction

### External Service Integration
- 2captcha API for CAPTCHA solving
- Proxy service API for IP rotation
- Email SMTP for notifications
- Telegram Bot API for instant alerts

### Monitoring Integration
- Health check endpoints for each microservice
- Log aggregation for debugging and monitoring
- Metrics collection for performance analysis

## Conclusion

The research supports the proposed Python + Playwright + Docker architecture for reliable, stealthy automation of asylum appointment booking. The multi-layered approach to stealth, robust error handling, and ethical rate limiting provide a solid foundation for the implementation phase.

All technical dependencies are well-established with active communities and commercial support where needed. The microservice architecture allows for independent scaling and maintenance of each component.

Key success factors:
1. Comprehensive testing against the actual government site
2. Robust error handling and recovery mechanisms  
3. Respectful rate limiting and ethical operation
4. Continuous monitoring and adaptation to site changes
