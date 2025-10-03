# Engineering Backlog

This backlog collects cross-cutting or future action items that emerge from reviews and planning.

Routing guidance:

- Use this file for non-urgent optimizations, refactors, or follow-ups that span multiple stories/epics.
- Must-fix items to ship a story belong in that story's `Tasks / Subtasks`.
- Same-epic improvements may also be captured under the epic Tech Spec `Post-Review Follow-ups` section.

| Date | Story | Epic | Type | Severity | Owner | Status | Notes |
| ---- | ----- | ---- | ---- | -------- | ----- | ------ | ----- |
| 2025-10-02 | 1.1 | 1 | Bug | High | Sonnet 4.5 | Resolved | Create missing backend module directories (api/, services/, db/, utils/) with __init__.py files. Blocks Stories 1.4-1.7. Ref: backend/app/ |
| 2025-10-02 | 1.1 | 1 | Security | High | Sonnet 4.5 | Resolved | Harden validate-env.sh environment variable parsing to prevent command injection. Replace export pattern with set -a/source. Ref: scripts/validate-env.sh:7-9 |
| 2025-10-02 | 1.1 | 1 | TechDebt | High | Sonnet 4.5 | Resolved | Resolve React version mismatch - React 19.1.1 installed but tech spec requires 18.3.1. Breaking changes may affect integrations. Ref: frontend/package.json, tech-spec-epic-1.md:51 |
| 2025-10-02 | 1.1 | 1 | Enhancement | Med | Sonnet 4.5 | Resolved | Implement database connectivity check in /api/health endpoint. Currently returns static response. Ref: backend/app/main.py:25-32 |
| 2025-10-02 | 1.1 | 1 | Bug | Med | Sonnet 4.5 | Resolved | Update docker-compose.override.yml.example to reference port 9000 instead of stale port 8000. Ref: docker-compose.override.yml.example:13-16 |
| 2025-10-02 | 1.1 | 1 | Enhancement | Med | Sonnet 4.5 | Resolved | Replace frontend App.jsx with branded placeholder for HR Query System (prep for Story 1.3). Currently has Vite boilerplate. Ref: frontend/src/App.jsx |
| 2025-10-02 | 1.1 | 1 | Enhancement | Low | Sonnet 4.5 | Resolved | Create .dockerignore files for frontend and backend to optimize Docker build context |
| 2025-10-02 | 1.1 | 1 | Enhancement | Low | Sonnet 4.5 | Resolved | Add API key format validation to validate-env.sh (check for sk- prefix) |
| 2025-10-02 | 1.1 | 1 | TechDebt | Low | Sonnet 4.5 | Resolved | Document Node.js version decision - keep Node 18 or upgrade to 20. Resolve tech spec discrepancy |
| 2025-10-02 | 1.2 | 1 | Security | Med | Dev Agent | Resolved | Externalize read-only user password from hardcoded SQL script to environment variable or secrets management. Ref: backend/app/db/create_readonly_user.sql:9 (AC#4) |
| 2025-10-02 | 1.2 | 1 | Enhancement | Low | Dev Agent | Resolved | Add updated_at trigger to employees table for automatic timestamp updates on row modifications. Create Alembic migration 002_add_updated_at_trigger.py. Ref: AC#1 |
| 2025-10-02 | 1.2 | 1 | TechDebt | Low | Dev Agent | Resolved | Document test execution results for traceability. Add test logs to Story 1.2 Dev Agent Record. Ref: AC#6, AC#7 |
| 2025-10-02 | 1.2 | 1 | Testing | Low | Dev Agent | Resolved | Add retry logic unit test in tests/test_db_session.py to simulate connection failures. Defer to Story 1.5+ test implementation phase. Ref: backend/app/db/session.py, AC#7 |
| 2025-10-02 | 1.3 | 1 | Testing | High | Dev Agent | Resolved | Add automated test suite with Jest + React Testing Library for all frontend components. Create __tests__/ directory. Ref: frontend/src/components/, Story 1.3 AC1-AC7 |
| 2025-10-02 | 1.3 | 1 | TechDebt | Med | Dev Agent | Resolved | Add PropTypes validation to all React components (QueryInterface, ResultsTable, ErrorDisplay, LoadingSpinner, App). Install prop-types package. Ref: frontend/src/components/ |
| 2025-10-02 | 1.3 | 1 | Bug | Med | Dev Agent | Resolved | Complete timeout error handling in QueryInterface - add onTimeout callback prop to notify parent component. Ref: frontend/src/components/QueryInterface.jsx:24-32, AC6 |
| 2025-10-02 | 1.3 | 1 | Enhancement | Med | Dev Agent | Resolved | Implement Error Boundary component with react-error-boundary to catch render errors. Ref: frontend/src/App.jsx |
| 2025-10-02 | 1.3 | 1 | Accessibility | Med | Dev Agent | Resolved | Add ARIA labels and accessibility attributes (role="status", role="alert", aria-label, aria-describedby) to all components. Ref: QueryInterface, ErrorDisplay, LoadingSpinner, ResultsTable |
| 2025-10-02 | 1.3 | 1 | TechDebt | Low | Dev Agent | Resolved | Add comment explaining why placeholder mode handleQuerySubmit doesn't use query param. Ref: frontend/src/App.jsx:13 |
| 2025-10-02 | 1.3 | 1 | Enhancement | Low | Dev Agent | Resolved | Standardize color usage via Tailwind theme - update tailwind.config.js and component classes. Ref: tailwind.config.js, frontend/src/components/ |
| 2025-10-02 | 1.3 | 1 | Enhancement | Low | Dev Agent | Resolved | Consider minimum loading duration pattern for better UX (skip spinner if response < 300ms). Ref: frontend/src/App.jsx:18-24 |
| 2025-10-02 | 1.6 | 1 | Security | Med | Sonnet 4.5 | Resolved | Harden table name validation - use sqlparse to extract table names and validate exact match against whitelist. Current substring check could allow `employees_backup`. Ref: backend/app/services/validation_service.py:101-108 |
| 2025-10-02 | 1.6 | 1 | TechDebt | Low | Sonnet 4.5 | Resolved | Fix deprecated datetime.utcnow() in health endpoint. Replace with datetime.now(timezone.utc). Ref: backend/app/api/routes.py:107 |
| 2025-10-02 | 1.6 | 1 | Enhancement | Low | Sonnet 4.5 | Resolved | Add explicit type hints for consistency - `-> bool:` return annotation already present on validate_sql(). Ref: backend/app/services/validation_service.py:42 |
| 2025-10-02 | 1.6 | 1 | Enhancement | Low | Sonnet 4.5 | Resolved | Standardize error messages - now using "allowed" consistently throughout validation. Ref: backend/app/services/validation_service.py:82, 124 |
| 2025-10-02 | 1.7 | 1 | TechDebt | Low | Dev Team | Open | Refactor session management to use FastAPI Depends() pattern for consistency. Use `with session.begin():` context manager. Ref: backend/app/services/query_service.py:39-66, AC6 |
| 2025-10-02 | 1.7 | 1 | Enhancement | Low | Dev Team | Open | Add `truncated: bool` field to QueryResponse model to indicate when results > 1000 rows. Improves UX with "Showing first 1000 of X results" message. Ref: backend/app/services/query_service.py:49-52, AC4 |
| 2025-10-02 | 1.7 | 1 | Enhancement | Med | Platform Team | Open | Add connection pool metrics export to Prometheus/Grafana. Alert on pool exhaustion or high checkout times. Epic 3 deliverable. Ref: AC6 (pool monitoring) |
| 2025-10-02 | 1.7 | 1 | Enhancement | Low | Platform Team | Open | Add query performance monitoring - track slow query distribution (P50, P95, P99). Alert on timeout rate > 1%. Epic 3 deliverable. Ref: AC2, AC3 |
| 2025-10-02 | 1.7 | 1 | Documentation | Low | Dev Team | Open | Document connection pool tuning guidelines - when to adjust pool_size/max_overflow, monitoring, scaling. Create runbook. Ref: backend/app/db/session.py |
| 2025-10-02 | 2.1 | 2 | Enhancement | Med | Story 2.2 | Resolved | Implement `evaluate()` function in ragas_service.py to calculate Faithfulness, Answer Relevance, and Context Precision metrics. Required for AC2 of Epic 2. Blocker for Story 2.2. Ref: backend/app/services/ragas_service.py |
| 2025-10-02 | 2.1 | 2 | Enhancement | Low | TBD | Open | Add type hints to `initialize_ragas()` function for better IDE support. Example: `async def initialize_ragas() -> bool:`. Ref: backend/app/services/ragas_service.py:16 |
| 2025-10-02 | 2.1 | 2 | Documentation | Low | TBD | Open | Document Ragas installation time in deployment guide. Note: "Ragas installation may take 3-5 minutes due to dependency resolution on Windows". Ref: docs/README.md or deployment guide |
| 2025-10-02 | 2.2 | 2 | Enhancement | Med | TBD | Open | Implement actual Ragas metric calculation in evaluate() function - Replace placeholder scores with real Ragas evaluate() calls using imported metrics. AC1 currently infrastructure-only. Ref: backend/app/services/ragas_service.py:56-73 |
| 2025-10-02 | 2.2 | 2 | TechDebt | Low | TBD | Open | Add specific type hint for evaluate() return value - Change dict to Dict[str, float] for better IDE support and type safety. Ref: backend/app/services/ragas_service.py:37 |
| 2025-10-02 | 2.2 | 2 | Testing | Low | TBD | Open | Add performance test with real Ragas overhead measurement - Create integration test that calls real Ragas (not mocked) and asserts 500-850ms overhead target from RISK-1. Ref: tech-spec-epic-2.md |
| 2025-10-02 | 2.2 | 2 | Testing | Low | TBD | Open | Update test assertions when real Ragas implemented - Replace hardcoded 0.0 assertions with realistic score ranges or mock control for actual metric validation. Ref: backend/tests/test_ragas_service.py:62-64 |
