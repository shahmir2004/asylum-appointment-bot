# Implementation Plan: Asylum Appointment Booking Bot

**Branch**: `001-a-bot-that` | **Date**: September 9, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-a-bot-that/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Automated asylum appointment booking bot for Madrid offices that continuously monitors the Spanish government booking site (icp.administracionelectronica.gob.es), automatically detects available appointment slots, and books the earliest possible date. Uses Python with Playwright for web automation, Redis/Celery for scheduling, SQLite for data storage, and includes proxy rotation and CAPTCHA handling for stealth operation. Deployed as Docker microservices for scalability and reliability.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: Playwright (web automation), Celery (task scheduling), Redis (message broker), undetected-playwright (stealth), 2captcha/hCaptcha (CAPTCHA solving)  
**Storage**: SQLite (user credentials, booking attempts, appointment history)  
**Testing**: pytest (unit/integration testing), Playwright test runner (E2E testing)  
**Target Platform**: Linux server/VPS, Docker containers
**Project Type**: single (microservice architecture with Docker)  
**Performance Goals**: Check appointments every 2 minutes, handle 10+ concurrent Madrid offices, <30s booking response time  
**Constraints**: Stealth operation (avoid detection), proxy rotation required, CAPTCHA solving capability, resilient to site changes  
**Scale/Scope**: Single user per instance, 15+ Madrid offices, 24/7 monitoring, appointment history tracking

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 4 (bot-service, proxy-manager, job-scheduler, notifier) - VIOLATION: Exceeds 3 projects limit
- Using framework directly? Yes (Playwright, Celery, SQLite directly)
- Single data model? Yes (single SQLite schema, no DTOs)
- Avoiding patterns? Yes (direct DB access, no Repository pattern initially)

**Architecture**:
- EVERY feature as library? Yes (bot_service, proxy_manager, scheduler, notifier libraries)
- Libraries listed: bot_service (web automation), proxy_manager (IP rotation), scheduler (task management), notifier (alerts)
- CLI per library: Yes (each service exposes CLI with --help/--version/--format)
- Library docs: llms.txt format planned? Yes

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes (test MUST fail first)
- Git commits show tests before implementation? Yes
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes (actual SQLite DB, real Redis, actual government site for testing)
- Integration tests for: new libraries, contract changes, shared schemas? Yes
- FORBIDDEN: Implementation before test, skipping RED phase - ENFORCED

**Observability**:
- Structured logging included? Yes (structured JSON logs)
- Frontend logs → backend? N/A (no frontend, CLI-based)
- Error context sufficient? Yes (detailed error logging with context)

**Versioning**:
- Version number assigned? 0.1.0 (MAJOR.MINOR.BUILD)
- BUILD increments on every change? Yes
- Breaking changes handled? Yes (parallel tests, migration plan)

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 1 (Single project with microservice architecture) - Using Docker containers for deployment but single repository structure

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/update-agent-context.sh [claude|gemini|copilot]` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each service contract → contract test task [P] (bot-service, proxy-manager, job-scheduler, notification-service)
- Each data entity → model creation task [P] (UserProfile, MadridOffice, AppointmentSlot, BookingSession, BookingAttempt, NotificationLog, SystemConfiguration)
- Each user story → integration test task (monitoring, booking, notification, error handling, recovery)
- Implementation tasks to make tests pass following TDD approach
- Docker configuration and deployment tasks
- CLI interface tasks for each service

**Ordering Strategy**:
- Phase 1: Contract tests (must fail initially) [P]
- Phase 2: Database models and migrations [P] 
- Phase 3: Core service libraries (following dependency order)
- Phase 4: CLI interfaces for each service [P]
- Phase 5: Integration tests (service-to-service communication)
- Phase 6: End-to-end workflow tests (user stories)
- Phase 7: Docker configuration and deployment
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 4 projects (bot-service, proxy-manager, job-scheduler, notifier) | Critical stealth and reliability requirements demand separation of concerns | 3-project limit would force combining proxy management with bot service, creating detection risk and single point of failure for anti-bot measures |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (with documented complexity deviation)
- [x] Post-Design Constitution Check: PASS (4-project architecture justified)
- [x] All NEEDS CLARIFICATION resolved (through research phase)
- [x] Complexity deviations documented (4 projects for stealth requirements)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*