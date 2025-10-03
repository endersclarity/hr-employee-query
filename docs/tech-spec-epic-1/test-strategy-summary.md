# Test Strategy Summary

### Test Levels

**Unit Tests** (Python backend):
- `validation_service.py`: Test SQL validation logic (whitelist SELECT, block dangerous keywords)
- `llm_service.py`: Mock OpenAI responses, test prompt construction
- `query_service.py`: Mock dependencies, test orchestration logic
- **Framework**: pytest
- **Coverage Target**: 80%+ for service layer

**Integration Tests** (Backend):
- Test POST `/api/query` endpoint with real database and mocked LLM
- Test GET `/api/health` endpoint with real database connection
- Test 4 mandatory query flows end-to-end (Stories 1.5, 1.7, 1.8)
- **Framework**: pytest + FastAPI TestClient
- **Coverage**: All API endpoints, all error scenarios

**Frontend Tests** (React):
- Component tests for QueryInterface, ResultsTable, ErrorDisplay
- Test user interactions (input, submit, error display)
- **Framework**: Vitest + React Testing Library
- **Coverage Target**: 70%+ for components (lower priority than backend for MVP)

**End-to-End Tests** (Manual for MVP):
- Test all 4 mandatory queries in deployed environment
- Test malicious query rejection (3 scenarios from AC3)
- Test error handling (long query, empty query, DB failure)
- **Tool**: Manual testing + Postman for API calls
- **When**: Before demo day (Oct 10-11)

### Test Scenarios by Acceptance Criteria

| AC | Test Type | Test Scenario | Expected Result |
|----|-----------|---------------|-----------------|
| AC1 | Manual | Enter query in UI and submit | Query sent to backend, loading spinner shows |
| AC2 | Integration | POST 4 mandatory queries to `/api/query` | All return valid SQL and results |
| AC3 | Unit + Integration | Send malicious queries (DELETE, DROP, UPDATE) | All rejected with 400 error |
| AC4 | Manual | Execute query, inspect UI | Table renders with correct headers and data |
| AC5 | Data Validation | Query database for test data coverage | All scenarios have 2+ matching records |
| AC6 | Manual | Attempt INSERT with app DB connection | PostgreSQL returns permission denied |
| AC7 | Performance | Execute 10 queries, measure latency | P95 < 5 seconds |
| AC8 | Integration | Trigger errors (long query, empty, DB down) | User-friendly error messages displayed |
| AC9 | Manual | Run `docker-compose up` | All services start without errors |
| AC10 | Integration | POST to `/api/query`, validate JSON schema | Response matches QueryResponse Pydantic model |
| AC11 | Integration | GET `/api/health` | Returns 200 with status, database, timestamp fields |
| AC12 | Manual | Execute query, inspect logs | JSON log contains query_executed event with all fields |

### Test Data Requirements

**Mock Employee Data** (Story 1.2):
- 50+ total records
- At least 5 employees hired in last 6 months
- At least 3 Engineering employees with salary_usd > 120000
- At least 2 employees with leave_type = 'Parental Leave'
- At least 4 employees with manager_name = 'John Doe'
- Diverse departments (Engineering, Marketing, Sales, HR, Finance)
- Diverse roles (Software Engineer, Product Manager, Data Analyst, etc.)

**Test Queries** (for manual testing):
1. "Show me employees hired in the last 6 months"
2. "List Engineering employees with salary greater than 120K"
3. "Who is on parental leave?"
4. "Show employees managed by John Doe"
5. "Give me all employees in Marketing"
6. "DELETE FROM employees WHERE department = 'Engineering'" (malicious)
7. "DROP TABLE employees" (malicious)
8. (501-character query) (validation failure)

### Edge Cases and Error Scenarios

**LLM Edge Cases**:
- Query with ambiguous intent ("Show me high earners") → May generate SQL with arbitrary threshold
- Query with typos ("Show emplyees in Enginering") → LLM should correct or fail gracefully
- Query requesting non-existent columns ("Show employee hobbies") → LLM should return INVALID_REQUEST

**Validation Edge Cases**:
- SQL injection via string manipulation ("Show employees'; DROP TABLE employees; --")
- Multi-statement injection ("SELECT * FROM employees; DELETE FROM employees")
- Case variations ("DeLeTe FrOm EmPlOyEeS")

**Database Edge Cases**:
- Query returns 0 results → Display "No results found" message
- Query returns 1000+ results → Limit to 1000, show warning
- Database connection timeout → Return DB_ERROR with retry suggestion

### Test Execution Plan

**Phase 1: Development (During Stories 1.1-1.8)**:
- Write unit tests alongside implementation
- Run tests locally before committing code
- Target: All unit tests passing before Epic 1 completion

**Phase 2: Integration (After Story 1.8)**:
- Run integration tests against local Docker Compose environment
- Test all 4 mandatory queries + 3 malicious queries
- Verify all acceptance criteria (AC1-AC12)

**Phase 3: Deployment Validation (Oct 9-10)**:
- Deploy to Railway
- Run end-to-end tests in production environment
- Measure performance (AC7)
- Verify health check (AC11)

**Phase 4: Demo Preparation (Oct 11-12)**:
- Rehearse demo script with 4 mandatory queries
- Test backup scenarios (local Docker if Railway fails)
- Prepare screenshots/video as last resort

### Success Metrics

Epic 1 is considered **complete and demo-ready** when:
- ✅ All 12 acceptance criteria pass
- ✅ All 4 mandatory queries work end-to-end
- ✅ All malicious queries are blocked
- ✅ 80%+ unit test coverage for backend services
- ✅ Docker Compose starts all services successfully
- ✅ Deployed to Railway with health check passing
- ✅ Performance target met (P95 < 5s)
- ✅ **All 7 integration points validated** (CORS, static files, env vars, DB init order, API key, error mapping, timeouts)
- ✅ **Dependency chain test passes** (1.1 → 1.2 → 1.4 → 1.5 → 1.6 → 1.7 → 1.8)

---
