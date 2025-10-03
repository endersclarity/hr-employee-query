# Story 1.4: FastAPI Backend & REST API

Status: Ready for Review

## Story

As a **frontend developer**,
I want **a FastAPI REST API with `/api/query` endpoint that accepts natural language queries and returns structured JSON responses**,
so that **the React frontend can communicate with the backend to process user queries**.

## Acceptance Criteria

1. **AC1**: POST `/api/query` endpoint accepts natural language queries and returns structured JSON
   - **Source**: [tech-spec-epic-1.md AC10, epic-stories.md Story 1.4]

2. **AC2**: GET `/api/health` endpoint returns health status and database connectivity
   - **Source**: [tech-spec-epic-1.md AC11]

3. **AC3**: CORS middleware configured with explicit origins (not `*`)
   - **Source**: [tech-spec-epic-1.md Integration Point 1, Enhanced Story 1.4]

4. **AC4**: Request ID middleware added for distributed tracing
   - **Source**: [tech-spec-epic-1.md Enhanced Story 1.4]

5. **AC5**: Global API request timeout implemented (default 10s)
   - **Source**: [tech-spec-epic-1.md Enhanced Story 1.4, Integration Point 7]

6. **AC6**: API returns QueryResponse JSON schema matching Pydantic model
   - **Source**: [tech-spec-epic-1.md Data Models → QueryResponse]

7. **AC7**: Error responses include appropriate HTTP status codes (400, 500, 503)
   - **Source**: [tech-spec-epic-1.md APIs and Interfaces]

## Tasks / Subtasks

- [x] **Task 1**: Create FastAPI application structure (AC: #1, #6)
  - [x] 1.1: Create `backend/app/main.py` with FastAPI app initialization
  - [x] 1.2: Create `backend/app/api/routes.py` for endpoint routing
  - [x] 1.3: Create `backend/app/api/models.py` for Pydantic request/response models:
    ```python
    from pydantic import BaseModel, Field
    from typing import List, Dict, Any

    class QueryRequest(BaseModel):
        query: str = Field(..., min_length=1, max_length=500, description="Natural language query")

    class QueryResponse(BaseModel):
        success: bool
        query: str
        generated_sql: str | None = None
        results: List[Dict[str, Any]] = []
        result_count: int = 0
        execution_time_ms: int = 0
        error: str | None = None
        error_type: str | None = None  # 'VALIDATION_ERROR', 'LLM_ERROR', 'DB_ERROR'

    class HealthResponse(BaseModel):
        status: str  # 'healthy' or 'unhealthy'
        database: str  # 'connected' or 'disconnected'
        timestamp: str
    ```

- [x] **Task 2**: Implement POST `/api/query` endpoint (AC: #1, #5, #6)
  - [x] 2.1: Create route handler in `routes.py`:
    ```python
    from fastapi import APIRouter, HTTPException
    import asyncio
    from datetime import datetime

    router = APIRouter()

    @router.post("/api/query", response_model=QueryResponse)
    async def query(request: QueryRequest):
        start_time = datetime.now()

        try:
            # Placeholder response (will be implemented in Stories 1.5-1.7)
            async with asyncio.timeout(10):  # 10s timeout
                response = QueryResponse(
                    success=True,
                    query=request.query,
                    generated_sql="SELECT * FROM employees LIMIT 10",
                    results=[],
                    result_count=0,
                    execution_time_ms=0
                )
                return response
        except asyncio.TimeoutError:
            raise HTTPException(status_code=500, detail="Request timeout")
    ```
  - [x] 2.2: Add request timeout using `asyncio.timeout(10)`
  - [x] 2.3: Return placeholder QueryResponse (real implementation in later stories)

- [x] **Task 3**: Implement GET `/api/health` endpoint (AC: #2)
  - [x] 3.1: Create health check route:
    ```python
    @router.get("/api/health", response_model=HealthResponse)
    async def health():
        from datetime import datetime
        from backend.app.db.session import get_db_session

        try:
            # Test database connection
            db = get_db_session()
            db.execute("SELECT 1")
            db.close()
            db_status = "connected"
            overall_status = "healthy"
        except Exception as e:
            db_status = "disconnected"
            overall_status = "unhealthy"

        return HealthResponse(
            status=overall_status,
            database=db_status,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    ```
  - [x] 3.2: Test database connectivity in health check
  - [x] 3.3: Return 200 if healthy, 503 if unhealthy

- [x] **Task 4**: Configure CORS middleware (AC: #3)
  - [x] 4.1: Add CORS to `main.py`:
    ```python
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import os

    app = FastAPI(title="HR Query API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    ```
  - [x] 4.2: Read `ALLOWED_ORIGINS` from environment variable
  - [x] 4.3: Test CORS with frontend running on localhost:5173

- [x] **Task 5**: Add request ID middleware (AC: #4)
  - [x] 5.1: Create `backend/app/middleware/request_id.py`:
    ```python
    import uuid
    from starlette.middleware.base import BaseHTTPMiddleware

    class RequestIDMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request_id = str(uuid.uuid4())
            request.state.request_id = request_id
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
    ```
  - [x] 5.2: Add middleware to `main.py`:
    ```python
    from backend.app.middleware.request_id import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)
    ```

- [x] **Task 6**: Set up error handling (AC: #7)
  - [x] 6.1: Create custom exception handler in `main.py`:
    ```python
    from fastapi.responses import JSONResponse

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail, "error_type": "HTTP_ERROR"}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error", "error_type": "SERVER_ERROR"}
        )
    ```
  - [x] 6.2: Test error responses return correct status codes

- [x] **Task 7**: Update requirements.txt (AC: #1)
  - [x] 7.1: Add dependencies to `backend/requirements.txt`:
    ```
    fastapi==0.109.0
    uvicorn[standard]==0.27.0
    pydantic==2.5.3
    python-dotenv==1.0.0
    ```

- [x] **Task 8**: Update main.py to mount router (AC: #1, #2)
  - [x] 8.1: Include router in `main.py`:
    ```python
    from backend.app.api.routes import router
    app.include_router(router)
    ```
  - [x] 8.2: Configure app metadata (title, version, description)

- [x] **Task 9**: Test API endpoints (AC: #1, #2, #3, #5, #6, #7)
  - [x] 9.1: Start server: `uvicorn backend.app.main:app --reload`
  - [x] 9.2: Test POST `/api/query`:
    ```bash
    curl -X POST http://localhost:8000/api/query \
      -H "Content-Type: application/json" \
      -d '{"query": "Show me employees in Engineering"}'
    ```
    - Verify returns QueryResponse JSON
    - Verify `X-Request-ID` header present
  - [x] 9.3: Test GET `/api/health`:
    ```bash
    curl http://localhost:8000/api/health
    ```
    - Verify returns HealthResponse JSON
    - Verify database status shows "connected" or "disconnected"
  - [x] 9.4: Test CORS from frontend (localhost:5173):
    ```javascript
    fetch('http://localhost:8000/api/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query: 'test'})
    })
    ```
    - Verify no CORS errors in browser console
  - [x] 9.5: Test timeout (mock slow response > 10s) → verify 500 error
  - [x] 9.6: Test invalid request (empty query) → verify 400 error with validation message

## Dev Notes

### Architecture Patterns and Constraints

**From solution-architecture.md**:
- **Backend**: FastAPI 0.109.0 + Python 3.11+ with async support
- **Pattern**: REST API with Pydantic data validation
- **Error Handling**: Structured error responses with error_type categorization

**From tech-spec-epic-1.md**:
- **API Endpoints**: POST `/api/query`, GET `/api/health`
- **Response Model**: QueryResponse with success, query, generated_sql, results, result_count, execution_time_ms, error, error_type
- **Error Types**: VALIDATION_ERROR (400), LLM_ERROR (500), DB_ERROR (500), HTTP_ERROR, SERVER_ERROR

**OpenAI Model Selection** (User preference, 2025-10-02):
- **Model**: Use GPT-5 Nano (gpt-5-nano)
- **Rationale**: Cheapest ($0.05/1M input tokens, $0.40/1M output tokens) and fastest OpenAI model with ultra-low latency, sufficient for NL-to-SQL translation
- **Technical Details**: 400k context window, optimized for high-volume straightforward requests
- **Implementation Note**: Configure model name as "gpt-5-nano" in Story 1.5 (OpenAI Integration) when implementing LLM service
- API key already configured in .env file

### Critical Integration Points

**Integration Point 1: CORS Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```
**Why explicit origins**: Prevents CORS attacks in production. `ALLOWED_ORIGINS` can be set to Railway frontend URL.

**Integration Point 7: Request/Response Flow Timeouts**:
- API timeout: 10s (prevents hanging requests)
- LLM timeout: 5s (will be implemented in Story 1.5)
- DB timeout: 3s (will be implemented in Story 1.7)

### Project Structure Notes

**New Files Created**:
```
backend/app/
├── main.py (FastAPI app initialization)
├── api/
│   ├── routes.py (endpoint handlers)
│   └── models.py (Pydantic request/response models)
└── middleware/
    └── request_id.py (request ID middleware)
```

**Placeholder Behavior**:
- POST `/api/query` returns hardcoded SQL and empty results
- Real implementation in Stories 1.5 (LLM), 1.6 (validation), 1.7 (execution)

### Testing Standards

**Manual Testing** (no automated tests for this story):
1. API endpoints respond correctly
2. CORS allows frontend requests
3. Request ID header present in all responses
4. Health check accurately reports database status
5. Error responses have correct structure and status codes
6. Request timeout triggers after 10s

**API Documentation**:
- FastAPI auto-generates docs at `/docs` (Swagger UI)
- Visit `http://localhost:8000/docs` to test endpoints interactively

### References

- [Source: docs/tech-spec-epic-1.md, AC10, AC11]
- [Source: docs/epic-stories.md, Story 1.4]
- [Source: docs/tech-spec-epic-1.md, Data Models → QueryResponse, HealthResponse]
- [Source: docs/tech-spec-epic-1.md, APIs and Interfaces]
- [Source: docs/tech-spec-epic-1.md, Integration Point 1, Integration Point 7]
- [Source: docs/tech-spec-epic-1.md, Enhanced Story Implementation Checklist - Story 1.4]
- [Source: docs/solution-architecture.md, ADR-001]

## Change Log

| Date       | Version | Description              | Author |
| ---------- | ------- | ------------------------ | ------ |
| 2025-10-01 | 0.1     | Initial draft            | Kaelen |
| 2025-10-02 | 1.0     | Implementation completed | Claude Sonnet 4.5 |

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML/JSON will be added here by context workflow -->

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

- Implemented FastAPI application following official documentation patterns verified via Context7
- Fixed test import paths to use relative imports from backend directory
- Resolved test timeouts by mocking database connections in health endpoint tests
- All 20 API tests passing + 6 existing database tests passing

### Completion Notes List

**Implementation Summary:**
- Created complete FastAPI REST API with `/api/query` and `/api/health` endpoints
- Implemented Request ID middleware for distributed tracing (X-Request-ID header)
- Configured CORS middleware with environment-based origins
- Added global exception handlers for structured error responses
- Implemented 10s request timeout using asyncio.timeout
- Created comprehensive Pydantic models (QueryRequest, QueryResponse, HealthResponse)
- All acceptance criteria met with automated test coverage

**Testing:**
- 20 API endpoint tests (100% pass rate)
- Test coverage: query validation, health checks, CORS, middleware, error handling, edge cases
- 6 existing database tests continue to pass

**Technical Notes:**
- Placeholder SQL response in `/api/query` - real LLM/DB integration in Stories 1.5-1.7
- Fixed datetime.utcnow() deprecation warning for future Python compatibility
- Added pytest-asyncio and httpx for comprehensive async testing

### File List

**Created:**
- backend/app/api/models.py
- backend/app/api/routes.py
- backend/app/middleware/__init__.py
- backend/app/middleware/request_id.py
- backend/tests/test_api.py

**Modified:**
- backend/app/main.py (added middleware, routes, exception handlers)
- backend/requirements.txt (added pytest-asyncio, httpx)
