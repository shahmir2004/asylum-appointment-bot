# Tasks: Full-Stack Asylum Appointment Bot with Web Interface

**Input**: Design documents from `/specs/001-a-bot-that/` + Full-stack extension requirements
**Prerequisites**: plan.md, data-model.md, contracts/, existing bot implementation (95% complete)

## Execution Flow (main)
```
1. Load existing plan.md and assess current bot implementation
   → Current: Python bot with Playwright, SQLite, email notifications
   → Extension: Add React frontend + FastAPI backend + authentication
2. Load data-model.md and extend for web interface:
   → Add User Authentication entities (roles: developer, user)
   → Add WebSession, ActivityLog entities for frontend
3. Generate tasks for full-stack transformation:
   → Frontend: React/Next.js with beautiful UI components
   → Backend: FastAPI REST API with WebSocket support for real-time logs
   → Authentication: JWT-based auth with role-based access control
   → Integration: Connect existing bot services to web interface
   → Deployment: Render-ready configuration with environment variables
4. Apply task rules following TDD approach:
   → Contract tests first for all new API endpoints
   → Frontend component tests before implementation
   → Integration tests for bot control workflows
   → E2E tests for user scenarios
5. Maintain existing bot functionality while adding web layer
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Project Structure (Full-Stack Extension)
```
backend/
├── src/
│   ├── api/          # FastAPI routes and endpoints
│   ├── auth/         # Authentication and authorization
│   ├── models/       # Extended data models for web
│   ├── services/     # Bot control and web services
│   └── websocket/    # Real-time communication
├── tests/
│   ├── contract/     # API contract tests
│   ├── integration/  # Service integration tests
│   └── unit/         # Unit tests
└── requirements.txt

frontend/
├── src/
│   ├── components/   # Reusable UI components
│   ├── pages/        # Next.js pages/routes
│   ├── services/     # API client services
│   ├── hooks/        # React custom hooks
│   ├── stores/       # State management
│   └── styles/       # CSS/styled-components
├── tests/
│   ├── components/   # Component tests
│   └── e2e/          # End-to-end tests
└── package.json

# Existing bot code (keep current structure)
src/
├── bot_service/      # Existing core bot functionality
├── stealth/          # Existing stealth capabilities
├── models/           # Existing SQLite models
└── cli/              # Existing CLI interfaces

# Deployment
deploy/
├── render.yaml       # Render deployment configuration
├── docker-compose.yml # Local development
└── nginx.conf        # Reverse proxy configuration
```

## Phase 1: Backend Foundation

### Setup and Configuration
- [ ] T001 Create backend project structure with FastAPI dependencies in backend/
- [ ] T002 [P] Configure environment variables for web interface in backend/.env.example
- [ ] T003 [P] Set up FastAPI application with CORS and middleware in backend/src/main.py

### Authentication System
- [ ] T004 [P] Contract test POST /api/auth/login in backend/tests/contract/test_auth_login.py
- [ ] T005 [P] Contract test POST /api/auth/refresh in backend/tests/contract/test_auth_refresh.py
- [ ] T006 [P] Contract test GET /api/auth/me in backend/tests/contract/test_auth_me.py
- [ ] T007 [P] Contract test POST /api/auth/logout in backend/tests/contract/test_auth_logout.py

### Data Models for Web Interface
- [ ] T008 [P] WebUser model with roles (developer/user) in backend/src/models/web_user.py
- [ ] T009 [P] WebSession model for authentication tracking in backend/src/models/web_session.py
- [ ] T010 [P] ActivityLog model for user actions in backend/src/models/activity_log.py
- [ ] T011 [P] BotStatus model for real-time status tracking in backend/src/models/bot_status.py

### Authentication Implementation
- [ ] T012 JWT token service with role-based access in backend/src/auth/jwt_service.py
- [ ] T013 Password hashing and validation service in backend/src/auth/password_service.py
- [ ] T014 Role-based permission decorators in backend/src/auth/permissions.py
- [ ] T015 Authentication middleware for FastAPI in backend/src/auth/middleware.py

### Authentication Endpoints
- [ ] T016 POST /api/auth/login endpoint in backend/src/api/auth.py
- [ ] T017 POST /api/auth/refresh endpoint in backend/src/api/auth.py
- [ ] T018 GET /api/auth/me endpoint in backend/src/api/auth.py
- [ ] T019 POST /api/auth/logout endpoint in backend/src/api/auth.py

## Phase 2: Bot Control API

### Bot Control Contract Tests
- [ ] T020 [P] Contract test GET /api/bot/status in backend/tests/contract/test_bot_status.py
- [ ] T021 [P] Contract test POST /api/bot/start in backend/tests/contract/test_bot_start.py
- [ ] T022 [P] Contract test POST /api/bot/stop in backend/tests/contract/test_bot_stop.py
- [ ] T023 [P] Contract test GET /api/bot/logs in backend/tests/contract/test_bot_logs.py
- [ ] T024 [P] Contract test GET /api/bot/statistics in backend/tests/contract/test_bot_stats.py

### Bot Integration Services
- [ ] T025 BotControlService to manage existing bot processes in backend/src/services/bot_control.py
- [ ] T026 LogsService to read and format bot logs in backend/src/services/logs_service.py
- [ ] T027 StatisticsService for bot performance metrics in backend/src/services/statistics_service.py
- [ ] T028 Bot process manager with subprocess control in backend/src/services/process_manager.py

### Bot Control Endpoints
- [ ] T029 GET /api/bot/status endpoint in backend/src/api/bot.py
- [ ] T030 POST /api/bot/start endpoint with authentication in backend/src/api/bot.py
- [ ] T031 POST /api/bot/stop endpoint with authentication in backend/src/api/bot.py
- [ ] T032 GET /api/bot/logs endpoint with pagination in backend/src/api/bot.py
- [ ] T033 GET /api/bot/statistics endpoint in backend/src/api/bot.py

## Phase 3: Real-Time Communication

### WebSocket Contract Tests
- [ ] T034 [P] WebSocket connection test for real-time logs in backend/tests/contract/test_websocket_logs.py
- [ ] T035 [P] WebSocket authentication test in backend/tests/contract/test_websocket_auth.py

### WebSocket Implementation
- [ ] T036 WebSocket connection manager in backend/src/websocket/connection_manager.py
- [ ] T037 Real-time log streaming service in backend/src/websocket/log_streamer.py
- [ ] T038 WebSocket authentication handler in backend/src/websocket/auth_handler.py
- [ ] T039 WebSocket endpoint for /ws/logs in backend/src/websocket/endpoints.py

## Phase 4: Frontend Foundation

### Frontend Setup
- [ ] T040 Create Next.js project with TypeScript in frontend/
- [ ] T041 [P] Install and configure UI library (Tailwind CSS + shadcn/ui) in frontend/
- [ ] T042 [P] Set up API client service with axios in frontend/src/services/api.ts
- [ ] T043 [P] Configure environment variables for frontend in frontend/.env.example

### Authentication Frontend
- [ ] T044 [P] Login component with form validation in frontend/src/components/Login.tsx
- [ ] T045 [P] Authentication context and provider in frontend/src/contexts/AuthContext.tsx
- [ ] T046 [P] Protected route component in frontend/src/components/ProtectedRoute.tsx
- [ ] T047 [P] User profile component in frontend/src/components/UserProfile.tsx

### Authentication Pages
- [ ] T048 Login page with beautiful design in frontend/src/pages/login.tsx
- [ ] T049 Dashboard layout component in frontend/src/components/Layout.tsx
- [ ] T050 Navigation component with role-based menus in frontend/src/components/Navigation.tsx

## Phase 5: Bot Control Interface

### Bot Control Components
- [ ] T051 [P] Bot status widget component in frontend/src/components/BotStatus.tsx
- [ ] T052 [P] Bot control buttons component in frontend/src/components/BotControls.tsx
- [ ] T053 [P] Real-time logs display component in frontend/src/components/LogsDisplay.tsx
- [ ] T054 [P] Statistics dashboard component in frontend/src/components/Statistics.tsx

### Bot Control Pages
- [ ] T055 Main dashboard page in frontend/src/pages/dashboard.tsx
- [ ] T056 Logs page with filtering and search in frontend/src/pages/logs.tsx
- [ ] T057 Statistics page with charts and metrics in frontend/src/pages/statistics.tsx
- [ ] T058 Settings page for bot configuration in frontend/src/pages/settings.tsx

### Real-Time Features
- [ ] T059 WebSocket hook for real-time updates in frontend/src/hooks/useWebSocket.ts
- [ ] T060 Real-time bot status updates in frontend/src/hooks/useBotStatus.ts
- [ ] T061 Live log streaming with auto-scroll in frontend/src/hooks/useLiveLogs.ts

## Phase 6: User Experience and Polish

### Role-Based Access
- [ ] T062 [P] Developer role features (full access) in frontend/src/components/DeveloperPanel.tsx
- [ ] T063 [P] User role features (limited access) in frontend/src/components/UserPanel.tsx
- [ ] T064 [P] Role-based component rendering in frontend/src/hooks/usePermissions.ts

### UI/UX Polish
- [ ] T065 [P] Beautiful loading states and animations in frontend/src/components/LoadingStates.tsx
- [ ] T066 [P] Error handling and toast notifications in frontend/src/components/ToastProvider.tsx
- [ ] T067 [P] Responsive design for mobile devices in frontend/src/styles/responsive.css
- [ ] T068 [P] Dark/light theme toggle in frontend/src/components/ThemeToggle.tsx

### Data Visualization
- [ ] T069 [P] Appointment statistics charts in frontend/src/components/Charts.tsx
- [ ] T070 [P] Bot performance metrics display in frontend/src/components/Metrics.tsx
- [ ] T071 [P] Historical data visualization in frontend/src/components/History.tsx

## Phase 7: Integration and Testing

### Integration Tests
- [ ] T072 [P] Integration test for bot start/stop workflow in backend/tests/integration/test_bot_workflow.py
- [ ] T073 [P] Integration test for authentication flow in backend/tests/integration/test_auth_flow.py
- [ ] T074 [P] Integration test for real-time logs in backend/tests/integration/test_realtime_logs.py

### Frontend Tests
- [ ] T075 [P] Component tests for authentication in frontend/tests/components/auth.test.tsx
- [ ] T076 [P] Component tests for bot controls in frontend/tests/components/bot-controls.test.tsx
- [ ] T077 [P] E2E tests for full user workflow in frontend/tests/e2e/user-workflow.test.ts

### API Documentation
- [ ] T078 [P] OpenAPI documentation generation in backend/src/api/docs.py
- [ ] T079 [P] API client documentation in frontend/src/services/README.md

## Phase 8: Deployment Configuration

### Render Deployment
- [ ] T080 Create Render deployment configuration in deploy/render.yaml
- [ ] T081 [P] Backend Dockerfile for production in backend/Dockerfile
- [ ] T082 [P] Frontend build configuration for static hosting in frontend/next.config.js
- [ ] T083 [P] Environment variables documentation in deploy/ENVIRONMENT.md

### Local Development
- [ ] T084 Docker Compose for local development in docker-compose.dev.yml
- [ ] T085 [P] Development scripts and README in scripts/dev-setup.sh
- [ ] T086 [P] Database migration scripts in backend/src/migrations/

### Security and Performance
- [ ] T087 [P] Rate limiting and security headers in backend/src/middleware/security.py
- [ ] T088 [P] Frontend security configuration in frontend/src/middleware.ts
- [ ] T089 [P] Performance monitoring setup in backend/src/monitoring/

## Phase 9: User Management and Configuration

### User Management API
- [ ] T090 [P] Contract test GET /api/users for user management in backend/tests/contract/test_users_get.py
- [ ] T091 [P] Contract test POST /api/users for user creation in backend/tests/contract/test_users_post.py
- [ ] T092 [P] Contract test PUT /api/users/{id} for user updates in backend/tests/contract/test_users_put.py

### User Management Implementation
- [ ] T093 UserManagementService for CRUD operations in backend/src/services/user_management.py
- [ ] T094 GET /api/users endpoint (developer only) in backend/src/api/users.py
- [ ] T095 POST /api/users endpoint (developer only) in backend/src/api/users.py
- [ ] T096 PUT /api/users/{id} endpoint in backend/src/api/users.py

### Configuration Management
- [ ] T097 [P] Bot configuration API endpoints in backend/src/api/config.py
- [ ] T098 [P] Configuration management UI in frontend/src/components/ConfigManager.tsx
- [ ] T099 [P] User settings management in frontend/src/components/UserSettings.tsx

## Phase 10: Final Integration and Documentation

### Final Integration
- [ ] T100 Connect existing bot services to new web backend in src/integrations/web_bridge.py
- [ ] T101 [P] Database migration from current SQLite to web-compatible schema in backend/src/migrations/migrate_existing.py
- [ ] T102 [P] Graceful fallback to CLI mode if web interface fails in src/cli/fallback_mode.py

### Documentation
- [ ] T103 [P] User guide for web interface in docs/WEB_USER_GUIDE.md
- [ ] T104 [P] Developer guide for API and architecture in docs/DEVELOPER_GUIDE.md
- [ ] T105 [P] Deployment guide for Render hosting in docs/DEPLOYMENT_GUIDE.md

### Final Testing
- [ ] T106 [P] End-to-end testing of complete workflow in tests/e2e/complete_workflow.py
- [ ] T107 [P] Performance testing under load in tests/performance/load_test.py
- [ ] T108 [P] Security testing and vulnerability scan in tests/security/security_test.py

## Dependencies

### Phase Dependencies
- Authentication (T004-T019) before Bot Control (T020-T033)
- Backend API (T001-T039) before Frontend (T040-T071)
- Core components (T040-T058) before Polish (T062-T071)
- Integration (T072-T079) before Deployment (T080-T089)

### Critical Dependencies
- T008-T011 (Data Models) block all API endpoints
- T012-T015 (Auth Services) block T016-T019 (Auth Endpoints)
- T025-T028 (Bot Services) block T029-T033 (Bot Endpoints)
- T036-T039 (WebSocket) blocks real-time features T059-T061
- T044-T047 (Auth Frontend) blocks all protected pages T055-T058

### Parallel Opportunities
- Frontend and Backend can be developed in parallel after T003
- Component tests (T075-T077) can run parallel with implementation
- Documentation (T078-T079, T103-T105) can be written in parallel
- Deployment configuration (T080-T086) can be prepared early

## Parallel Execution Examples

### Authentication Phase
```bash
# Backend Auth Tests (T004-T007)
Task: "Contract test POST /api/auth/login in backend/tests/contract/test_auth_login.py"
Task: "Contract test POST /api/auth/refresh in backend/tests/contract/test_auth_refresh.py"
Task: "Contract test GET /api/auth/me in backend/tests/contract/test_auth_me.py"
Task: "Contract test POST /api/auth/logout in backend/tests/contract/test_auth_logout.py"

# Data Models (T008-T011)
Task: "WebUser model with roles in backend/src/models/web_user.py"
Task: "WebSession model in backend/src/models/web_session.py"
Task: "ActivityLog model in backend/src/models/activity_log.py"
Task: "BotStatus model in backend/src/models/bot_status.py"
```

### Frontend Development
```bash
# Core Components (T051-T054)
Task: "Bot status widget in frontend/src/components/BotStatus.tsx"
Task: "Bot control buttons in frontend/src/components/BotControls.tsx"
Task: "Real-time logs display in frontend/src/components/LogsDisplay.tsx"
Task: "Statistics dashboard in frontend/src/components/Statistics.tsx"

# Role Components (T062-T063)
Task: "Developer panel in frontend/src/components/DeveloperPanel.tsx"
Task: "User panel in frontend/src/components/UserPanel.tsx"
```

### Final Phase
```bash
# Documentation (T103-T105)
Task: "User guide in docs/WEB_USER_GUIDE.md"
Task: "Developer guide in docs/DEVELOPER_GUIDE.md"
Task: "Deployment guide in docs/DEPLOYMENT_GUIDE.md"

# Testing (T106-T108)
Task: "End-to-end workflow test in tests/e2e/complete_workflow.py"
Task: "Performance test in tests/performance/load_test.py"
Task: "Security test in tests/security/security_test.py"
```

## Expected Deliverables

### Technical Stack
- **Backend**: FastAPI + SQLAlchemy + WebSocket + JWT Authentication
- **Frontend**: Next.js + TypeScript + Tailwind CSS + shadcn/ui
- **Database**: SQLite (existing) extended with web-specific tables
- **Real-time**: WebSocket for live logs and status updates
- **Authentication**: JWT with role-based access (developer/user)
- **Deployment**: Render-ready with environment configuration

### User Experience
- **Beautiful Dashboard**: Modern, responsive design with dark/light themes
- **Real-time Monitoring**: Live bot status, logs, and statistics
- **Role-based Access**: Developer (full control) vs User (monitoring only)
- **Bot Control**: Start/stop bot with visual feedback
- **Comprehensive Logs**: Searchable, filterable, real-time log display
- **Mobile Responsive**: Works seamlessly on all devices

### Security Features
- **JWT Authentication**: Secure token-based authentication
- **Role-based Authorization**: Granular permission control
- **Rate Limiting**: API protection against abuse
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Secure cross-origin resource sharing

### Deployment Ready
- **Render Hosting**: One-click deployment to Render
- **Environment Variables**: Secure configuration management
- **Docker Support**: Containerized for easy deployment
- **Database Migrations**: Automated schema updates
- **Health Checks**: Monitoring and alerting capabilities

## Notes
- All tests must be written FIRST and must FAIL before implementation
- Maintain backward compatibility with existing bot CLI functionality
- Prioritize security and user experience throughout development
- Follow TDD (Test-Driven Development) methodology strictly
- Ensure responsive design for mobile and desktop users
- Implement comprehensive error handling and user feedback
- Document all API endpoints with OpenAPI/Swagger
- Include performance monitoring and optimization
