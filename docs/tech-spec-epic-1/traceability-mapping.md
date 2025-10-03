# Traceability Mapping

This table maps acceptance criteria → technical specification sections → implementation components → test strategies.

| AC | PRD Requirement | Spec Section(s) | Component(s) | Test Approach |
|----|----------------|-----------------|--------------|---------------|
| **AC1** | FR001 (User input interface) | Services & Modules → QueryInterface | `frontend/src/components/QueryInterface.jsx` | Manual UI test: Enter query, verify submission |
| **AC2** | FR002, FR005 (NL→SQL, mandatory queries) | APIs & Interfaces → OpenAI Integration, Workflows → Query Flow | `backend/app/services/llm_service.py` | Integration test: 4 example queries → verify SQL output |
| **AC3** | FR006, FR010 (SQL validation, malicious detection) | Security → Layer 4 SQL Validation | `backend/app/services/validation_service.py` | Unit test: Malicious queries → verify rejection with 400 error |
| **AC4** | FR004 (Tabular results) | Services & Modules → ResultsTable | `frontend/src/components/ResultsTable.jsx` | Manual UI test: Execute query, verify table renders correctly |
| **AC5** | FR011 (Database schema), Story 1.2 | Data Models → Database Schema | `backend/app/db/seed.py` | Data validation: Query database, count matching records |
| **AC6** | FR012, NFR001 (Read-only connection) | Security → Layer 1 DB Permissions | `backend/app/db/session.py` (connection string) | Manual DB test: Attempt INSERT with app credentials → verify rejection |
| **AC7** | NFR002 (Performance <5s) | Performance → Target & Breakdown | All components (end-to-end flow) | Load test: 10 queries, measure P95 latency |
| **AC8** | FR010 (Error messages) | Services & Modules → ErrorDisplay, Workflows → Error Flow | `frontend/src/components/ErrorDisplay.jsx` | Unit + integration test: Trigger errors → verify user-friendly messages |
| **AC9** | NFR003 (Docker deployment) | Deployment Architecture → Docker Compose | `docker-compose.yml` | Manual deployment test: `docker-compose up` → verify all services start |
| **AC10** | FR013 (REST API JSON responses) | APIs & Interfaces → POST /api/query | `backend/app/api/models.py` (QueryResponse) | API integration test: POST request → validate JSON schema |
| **AC11** | NFR003 (Deployment health) | APIs & Interfaces → GET /api/health | `backend/app/api/routes.py` | API test: GET `/api/health` → verify 200 + status fields |
| **AC12** | NFR005 (Logging/documentation) | Observability → Key Log Events | `backend/app/utils/logger.py` | Log inspection: Execute query → verify structured JSON log |

### Story → Acceptance Criteria Mapping

| Story | Primary AC(s) Covered | Notes | **Critical Dependencies** |
|-------|----------------------|-------|---------------------------|
| **Story 1.1** (Project Foundation) | AC9 | Docker Compose setup | **None** - Blocks ALL other stories |
| **Story 1.2** (Database & Mock Data) | AC5, AC6 | Database schema + seed data + read-only user | Depends on: 1.1; Blocks: 1.7, 1.8 |
| **Story 1.3** (React Frontend UI) | AC1, AC4, AC8 | Input field, results table, error display | Depends on: 1.1; Blocks: 1.8 |
| **Story 1.4** (FastAPI Backend) | AC10, AC11 | API endpoints + health check + **CORS** | Depends on: 1.1; Blocks: 1.5, 1.6, 1.7, 1.8 |
| **Story 1.5** (LLM Integration) | AC2 | NL→SQL conversion + **API key validation** | Depends on: 1.4; Blocks: 1.7, 1.8 |
| **Story 1.6** (SQL Validation) | AC3 | Security layer + **validation logging** | Depends on: 1.4, 1.5; Blocks: 1.7, 1.8 |
| **Story 1.7** (SQL Execution) | AC7 | DB query + **timeout + size limits** | Depends on: 1.2, 1.4, 1.5, 1.6; Blocks: 1.8 |
| **Story 1.8** (Frontend-Backend Integration) | AC1, AC4, AC7, AC8 | End-to-end + **static file serving + error mapping** | Depends on: 1.3, 1.7; **FINAL STORY** |

### Critical Integration Points (Dependency Analysis)

**Integration Point 1: CORS Configuration** (Story 1.4)
- **Components**: `routes.py` → CORS middleware → `frontend/src/services/api.js`
- **Risk**: Frontend blocked from calling backend APIs
- **Implementation**:
  ```python
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
      allow_credentials=True,
      allow_methods=["GET", "POST"],
      allow_headers=["*"],
  )
  ```

**Integration Point 2: Static File Serving** (Story 1.8)
- **Components**: FastAPI → React build (`frontend/dist/`)
- **Risk**: Production deployment won't serve frontend UI
- **Implementation**:
  ```python
  from fastapi.staticfiles import StaticFiles
  from fastapi.responses import FileResponse

  app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

  @app.get("/{full_path:path}")
  async def serve_react(full_path: str):
      return FileResponse("frontend/dist/index.html")
  ```

**Integration Point 3: Environment Variable Validation** (Story 1.1)
- **Components**: `.env` → Docker Compose → All services
- **Risk**: Missing API keys cause runtime failures
- **Implementation**: Create `scripts/validate-env.sh`:
  ```bash
  #!/bin/bash
  required_vars=("OPENAI_API_KEY" "DATABASE_URL")
  for var in "${required_vars[@]}"; do
      if [ -z "${!var}" ]; then
          echo "ERROR: $var is not set"
          exit 1
      fi
  done
  ```

**Integration Point 4: Database Initialization Order** (Story 1.2)
- **Components**: Alembic migrations → `seed.py`
- **Risk**: Seed fails if schema doesn't exist
- **Implementation**: Update `scripts/start.sh`:
  ```bash
  #!/bin/bash
  # 1. Run migrations FIRST
  alembic upgrade head
  # 2. Seed database SECOND (only if empty)
  python -m app.db.seed
  # 3. Start server LAST
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

**Integration Point 5: OpenAI API Key Validation** (Story 1.5)
- **Components**: `llm_service.py` startup validation
- **Risk**: Integration tests fail without clear error
- **Implementation**:
  ```python
  async def validate_api_key():
      try:
          await openai_client.chat.completions.create(
              model="gpt-4o-mini",
              messages=[{"role": "user", "content": "test"}],
              max_tokens=5
          )
          logger.info("OpenAI API key validated successfully")
      except Exception as e:
          logger.critical(f"OpenAI API key validation failed: {e}")
          raise
  ```

**Integration Point 6: Error Type Mapping** (Story 1.8)
- **Components**: Backend error types → Frontend user messages
- **Risk**: Generic errors instead of helpful messages
- **Implementation**:
  ```javascript
  // frontend/src/services/api.js
  const ERROR_MESSAGES = {
      'VALIDATION_ERROR': 'Query validation failed. Only SELECT queries are permitted.',
      'LLM_ERROR': 'Unable to process query. Please try again or rephrase.',
      'DB_ERROR': 'Database query failed. Please check your query and try again.'
  };
  ```

**Integration Point 7: Request/Response Flow Timeouts** (Stories 1.4, 1.5, 1.7)
- **Components**: API Client → FastAPI → OpenAI → PostgreSQL
- **Risk**: Hanging requests exceed 5s performance target
- **Implementation**:
  ```python
  # API timeout
  @app.post("/api/query", response_model=QueryResponse)
  async def query(request: QueryRequest, timeout: int = 10):
      async with asyncio.timeout(timeout):
          return await query_service.execute(request.query)

  # LLM timeout
  response = await asyncio.wait_for(
      openai_client.chat.completions.create(...),
      timeout=5.0
  )

  # DB timeout
  with db.session.begin():
      db.session.execute(text(sql).execution_options(timeout=3))
  ```

### Enhanced Story Implementation Checklist (Based on Dependency Analysis)

**Story 1.1 Enhancements** (Foundation):
- ✅ Create `.env.example` with ALL required variables (OPENAI_API_KEY, DATABASE_URL, PYTHON_ENV, ALLOWED_ORIGINS, LOG_LEVEL)
- ✅ Add `scripts/validate-env.sh` for startup environment validation
- ✅ Document port requirements (5173, 8000, 5432) in README
- ✅ Add `docker-compose.override.yml.example` for local customization
- ✅ Verify Docker Compose health checks for all services

**Story 1.2 Enhancements** (Database):
- ✅ Update `scripts/start.sh`: migrations → seed → server (strict order)
- ✅ Add database connection retry logic in `db/session.py` (max 5 attempts, 2s delay)
- ✅ Validate seed data POST-insertion (count employees by: department='Engineering' AND salary>120K, hire_date, leave_type, manager_name)
- ✅ Create read-only user BEFORE seeding

**Story 1.3 Enhancements** (Frontend UI):
- ✅ Add client-side query length validation (1-500 chars) BEFORE API call
- ✅ Implement loading state timeout (10s → show timeout error)
- ✅ Add result pagination UI for > 50 results (optional for MVP)

**Story 1.4 Enhancements** (Backend API):
- ✅ Configure CORS middleware with explicit origins from env var
- ✅ Add request ID middleware for distributed tracing
- ✅ Implement global API request timeout (default 10s)
- ✅ Add `/api/health` database connection check

**Story 1.5 Enhancements** (LLM Integration):
- ✅ Validate OpenAI API key on service startup (test completion call)
- ✅ Add LLM request timeout (5s max via `asyncio.wait_for`)
- ✅ Log LLM request/response times for performance analysis
- ✅ Implement query→SQL in-memory cache for demo reliability (optional)

**Story 1.6 Enhancements** (Validation):
- ✅ Log ALL validation failures with: NL query, generated SQL, failure reason
- ✅ Add validation performance benchmark test (< 50ms per query)
- ✅ Test case-insensitive keyword detection ("DeLeTe" should be blocked)

**Story 1.7 Enhancements** (SQL Execution):
- ✅ Implement query execution timeout (3s max via `execution_options(timeout=3)`)
- ✅ Add result set size check BEFORE serialization (max 1000 rows, truncate + warn)
- ✅ Test 0-result queries explicitly (display "No results found")
- ✅ Add connection pool health monitoring

**Story 1.8 Enhancements** (Integration):
- ✅ Verify FastAPI serves React static files: `/` → `frontend/dist/index.html`
- ✅ Create error type mapping in `api.js` (VALIDATION_ERROR, LLM_ERROR, DB_ERROR → user messages)
- ✅ Test end-to-end with ALL 3 error types
- ✅ Add frontend request timeout (10s)
- ✅ Test Railway deployment with static file serving
