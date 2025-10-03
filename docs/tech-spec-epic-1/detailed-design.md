# Detailed Design

### Services and Modules

| Module | Responsibility | Inputs | Outputs | Owner/Location |
|--------|---------------|--------|---------|----------------|
| **QueryInterface** (React) | User input capture and submission | User keystrokes | Query string, submit event | `frontend/src/components/QueryInterface.jsx` |
| **ResultsTable** (React) | Display query results in tabular format | Results array from API | Rendered HTML table | `frontend/src/components/ResultsTable.jsx` |
| **ErrorDisplay** (React) | Show error messages to user | Error object from API | Formatted error message | `frontend/src/components/ErrorDisplay.jsx` |
| **API Client** (JS) | HTTP communication with backend | Query string | Promise<Response> | `frontend/src/services/api.js` |
| **routes.py** (FastAPI) | API endpoint routing and request handling | HTTP POST /api/query | JSON response | `backend/app/api/routes.py` |
| **query_service** (Python) | Orchestrate NL→SQL→Results flow | Natural language query | QueryResponse with results + metadata | `backend/app/services/query_service.py` |
| **llm_service** (Python) | OpenAI integration for SQL generation | NL query + schema context | Generated SQL string | `backend/app/services/llm_service.py` |
| **validation_service** (Python) | SQL security validation | SQL string | Boolean (valid/invalid) + error | `backend/app/services/validation_service.py` |
| **Database Layer** (SQLAlchemy) | Execute SQL queries and return results | Validated SQL | List of employee records | `backend/app/db/session.py` |
| **seed.py** (Python) | Generate mock employee data | Database connection | 50+ employee records | `backend/app/db/seed.py` |

### Data Models and Contracts

#### Database Schema (PostgreSQL)

**employees table**:
```sql
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    employment_status VARCHAR(50) NOT NULL,  -- 'Active', 'Terminated', 'On Leave'
    hire_date DATE NOT NULL,
    leave_type VARCHAR(50),  -- NULL or 'Parental Leave', 'Medical Leave', 'Sick Leave'
    salary_local DECIMAL(12, 2) NOT NULL,
    salary_usd DECIMAL(12, 2) NOT NULL,
    manager_name VARCHAR(200),  -- NULL or manager full name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for query performance
CREATE INDEX idx_department ON employees(department);
CREATE INDEX idx_hire_date ON employees(hire_date);
CREATE INDEX idx_employment_status ON employees(employment_status);
CREATE INDEX idx_manager_name ON employees(manager_name);
```

**Rationale**: Indexes optimize the 4 mandatory query types (department filter, hire_date range, employment_status, manager_name lookup).

#### API Request/Response Models (Pydantic)

**QueryRequest** (`backend/app/api/models.py`):
```python
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural language query")
```

**QueryResponse** (`backend/app/api/models.py`):
```python
from typing import List, Dict, Any
from pydantic import BaseModel

class QueryResponse(BaseModel):
    success: bool
    query: str
    generated_sql: str | None = None
    results: List[Dict[str, Any]] = []
    result_count: int = 0
    execution_time_ms: int = 0
    error: str | None = None
    error_type: str | None = None  # 'VALIDATION_ERROR', 'LLM_ERROR', 'DB_ERROR'
```

**HealthResponse**:
```python
class HealthResponse(BaseModel):
    status: str  # 'healthy' or 'unhealthy'
    database: str  # 'connected' or 'disconnected'
    timestamp: str
```

#### ORM Models (SQLAlchemy)

**Employee** (`backend/app/db/models.py`):
```python
from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    employment_status = Column(String(50), nullable=False)
    hire_date = Column(Date, nullable=False)
    leave_type = Column(String(50), nullable=True)
    salary_local = Column(DECIMAL(12, 2), nullable=False)
    salary_usd = Column(DECIMAL(12, 2), nullable=False)
    manager_name = Column(String(200), nullable=True)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP')
```

### APIs and Interfaces

#### REST API Endpoints

**Base URL**: `/api` (production: `https://your-app.railway.app/api`)

---

**POST /api/query**

Execute natural language query and return results.

**Request**:
```http
POST /api/query
Content-Type: application/json

{
  "query": "Show me employees in Engineering with salary greater than 120K"
}
```

**Response (Success - 200)**:
```json
{
  "success": true,
  "query": "Show me employees in Engineering with salary greater than 120K",
  "generated_sql": "SELECT employee_id, first_name, last_name, department, salary_usd FROM employees WHERE department = 'Engineering' AND salary_usd > 120000",
  "results": [
    {
      "employee_id": 42,
      "first_name": "Alice",
      "last_name": "Johnson",
      "department": "Engineering",
      "salary_usd": 135000.00
    }
  ],
  "result_count": 1,
  "execution_time_ms": 1243
}
```

**Response (Validation Error - 400)**:
```json
{
  "success": false,
  "error": "Query validation failed: Only SELECT queries are permitted",
  "error_type": "VALIDATION_ERROR"
}
```

**Response (LLM Error - 500)**:
```json
{
  "success": false,
  "error": "Failed to generate SQL from natural language query",
  "error_type": "LLM_ERROR"
}
```

**Response (Database Error - 500)**:
```json
{
  "success": false,
  "error": "Database query execution failed",
  "error_type": "DB_ERROR"
}
```

**Error Codes**:
- `400` - Invalid request (query too long, empty query, validation failure)
- `500` - Server error (LLM failure, database connection issue)

---

**GET /api/health**

Health check endpoint for monitoring.

**Response (200)**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-01T14:30:00Z"
}
```

**Response (503 - Unhealthy)**:
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "timestamp": "2025-10-01T14:30:00Z"
}
```

#### OpenAI API Integration

**Service**: `llm_service.py`

**System Prompt Template**:
```python
SYSTEM_PROMPT = """You are a SQL query generator for an HR employee database.

CRITICAL RULES:
1. Generate ONLY SELECT statements
2. Never generate DELETE, DROP, UPDATE, INSERT, or ALTER statements
3. Only query the 'employees' table
4. Use these columns only: {column_list}

If the user's request cannot be fulfilled with a SELECT query, respond with: "INVALID_REQUEST"

Schema:
{schema_definition}

Examples:
{few_shot_examples}
"""
```

**LLM Request**:
```python
response = await openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": natural_language_query}
    ],
    temperature=0.0,  # Deterministic output
    max_tokens=200    # SQL queries are concise
)
```

**Error Handling**:
- Rate limit errors → Retry with exponential backoff (max 3 attempts)
- Network errors → Return LLM_ERROR to client
- Invalid API key → Log critical error, return 500

### Workflows and Sequencing

#### Primary Query Flow (Happy Path)

```
[User] → [React QueryInterface] → [API Client] → [POST /api/query]
                                                        ↓
                                                [FastAPI routes.py]
                                                        ↓
                                                [query_service.execute()]
                                                        ↓
                                    ┌───────────────────┴──────────────────┐
                                    ↓                                      ↓
                            [llm_service.generate_sql()]          [sanitize_input()]
                                    ↓
                            (OpenAI API Call)
                                    ↓
                            Generated SQL ────────────────────────────────┐
                                                                          ↓
                                                        [validation_service.validate_sql()]
                                                                          ↓
                                                        ✓ Whitelist SELECT only
                                                        ✓ Block malicious keywords
                                                        ✓ Verify 'employees' table only
                                                                          ↓
                                                        [db.session.execute(sql)]
                                                                          ↓
                                                        [PostgreSQL Query]
                                                                          ↓
                                                        Results (List[Dict])
                                                                          ↓
                                                        [QueryResponse JSON]
                                                                          ↓
                                                        [React ResultsTable]
                                                                          ↓
                                                        [User sees results]
```

**Step-by-Step Sequence**:

1. **User Input**: User types "Show me employees in Engineering with salary > 120K" and clicks Submit
2. **Frontend Validation**: React validates query length (1-500 chars), shows loading spinner
3. **API Request**: Axios POST to `/api/query` with `{query: "..."}`
4. **Input Sanitization**: Remove SQL comments (`--`, `/* */`), semicolons, trim whitespace
5. **LLM Generation**: Send to OpenAI GPT-4o-mini with schema-aware system prompt
6. **SQL Validation**: Parse generated SQL with `sqlparse`, check:
   - Is it a SELECT statement? (Yes → Continue, No → Error)
   - Contains dangerous keywords? (Yes → Error, No → Continue)
   - References only 'employees' table? (Yes → Continue, No → Error)
7. **Database Execution**: Execute validated SQL via read-only connection
8. **Response Assembly**: Package results + metadata into QueryResponse
9. **Frontend Display**: Render results in table, hide loading spinner

**Estimated Latency**: 1.2-3.5 seconds (LLM call = 0.8-2.5s, DB query = 50-300ms, validation = 10-50ms)

#### Error Flow Examples

**Malicious Query Detection**:
```
User: "DELETE FROM employees WHERE department = 'Engineering'"
      ↓
Sanitization: Remove semicolons (none present)
      ↓
LLM: Generates "DELETE FROM employees WHERE department = 'Engineering'"
      ↓
Validation: Detects "DELETE" keyword → REJECT
      ↓
Response: 400 Bad Request, error_type="VALIDATION_ERROR"
      ↓
Frontend: Show error message "Only SELECT queries are permitted"
```

**LLM Failure**:
```
User: "Show me employees in Finance"
      ↓
API Request → llm_service
      ↓
OpenAI API: Rate limit exceeded (429 error)
      ↓
Retry with backoff (3 attempts)
      ↓
All retries fail
      ↓
Response: 500 Server Error, error_type="LLM_ERROR"
      ↓
Frontend: "Unable to process query. Please try again."
```
