# Non-Functional Requirements

### Performance

**Target**: Query response time < 5 seconds (NFR002 from PRD)

**Breakdown**:
- Frontend rendering: < 50ms
- Network latency: 50-200ms (Railway → user)
- API processing time: < 4.7 seconds
  - Input sanitization: 5-10ms
  - LLM API call: 800-2500ms (OpenAI GPT-4o-mini)
  - SQL validation: 10-50ms (sqlparse)
  - Database query: 50-300ms (indexed queries)
  - JSON serialization: 20-100ms

**Optimization Strategies**:
1. **Database Indexing**: Indexes on `department`, `hire_date`, `employment_status`, `manager_name` reduce query time to 50-100ms
2. **LLM Temperature = 0.0**: Deterministic output reduces variance in response time
3. **Result Limiting**: Max 1000 rows prevents large payload serialization delays
4. **Connection Pooling**: SQLAlchemy connection pool (size=10) reuses DB connections
5. **Async Processing**: FastAPI async endpoints + OpenAI async client for non-blocking I/O

**Monitoring**:
- Log `execution_time_ms` for every query
- Track P50, P95, P99 latencies (future enhancement)
- Alert if > 10% of queries exceed 5s threshold

### Security

**Requirement**: Multi-layered security to prevent SQL injection and data manipulation (NFR001 from PRD)

**Layer 1: Database-Level Permissions**
```sql
-- Create read-only user
CREATE USER query_app_readonly WITH PASSWORD 'secure_random_password';
GRANT CONNECT ON DATABASE hr_db TO query_app_readonly;
GRANT SELECT ON employees TO query_app_readonly;
REVOKE ALL ON employees FROM query_app_readonly;
GRANT SELECT ON employees TO query_app_readonly;
```
- Even if SQL injection succeeds, no write operations possible
- Connection string uses `query_app_readonly` user only

**Layer 2: Prompt Engineering Safeguards**
- System prompt explicitly forbids DELETE/DROP/UPDATE/INSERT/ALTER
- LLM instructed to respond "INVALID_REQUEST" for non-SELECT queries
- Schema limited to 'employees' table only in prompt context

**Layer 3: Input Sanitization** (`sanitize_input()` in validation_service.py)
```python
def sanitize_input(query: str) -> str:
    # Remove SQL comment indicators
    query = query.replace('--', '').replace('/*', '').replace('*/', '')
    # Remove semicolons (prevent multi-statement injection)
    query = query.replace(';', '')
    # Enforce length limit
    if len(query) > 500:
        raise ValueError("Query too long (max 500 characters)")
    return query.strip()
```

**Layer 4: SQL Query Validation** (`validate_sql()` in validation_service.py)
```python
import sqlparse

def validate_sql(sql: str) -> bool:
    parsed = sqlparse.parse(sql)
    if not parsed:
        raise ValueError("Invalid SQL syntax")

    stmt = parsed[0]
    if stmt.get_type() != 'SELECT':
        raise ValueError("Only SELECT queries allowed")

    dangerous_keywords = ['DELETE', 'DROP', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
    sql_upper = sql.upper()
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            raise ValueError(f"Dangerous keyword detected: {keyword}")

    if 'employees' not in sql.lower():
        raise ValueError("Only 'employees' table permitted")

    return True
```

**Layer 5: Environment Variable Protection**
- OpenAI API key stored in `.env` file (gitignored)
- Railway secrets for production deployment
- No hardcoded credentials in codebase

**Additional Measures**:
- CORS configured for specific origins only (not `*`)
- HTTPS enforced in production (Railway default)
- No sensitive data logged (PII redacted from logs)

### Reliability/Availability

**Target**: 99% uptime during demo period (acceptable for MVP/interview demo, not production SLA)

**Error Handling Strategy**:

1. **LLM Failures**:
   - Retry with exponential backoff (3 attempts: 1s, 2s, 4s delays)
   - If all retries fail → Return 500 with `LLM_ERROR` error type
   - Fallback: Log error, allow user to retry manually

2. **Database Connection Failures**:
   - SQLAlchemy connection pool (size=10) with automatic retry
   - Health check endpoint (`/api/health`) detects DB connectivity
   - Railway auto-restarts service on crash

3. **Validation Errors**:
   - Return 400 Bad Request with clear error message
   - No retry needed (user must modify query)

4. **Frontend Error Boundaries**:
   - React error boundaries catch component crashes
   - Display user-friendly error message instead of blank screen

**Graceful Degradation**:
- If LLM unavailable: Display "Service temporarily unavailable" instead of crashing
- If database slow: Show loading spinner up to 10s before timeout
- No cascading failures (errors contained to single request)

### Observability

**Logging Framework**: `structlog` for structured JSON logs

**Log Levels**:
- `INFO`: Successful queries, execution metrics
- `WARNING`: Validation failures, retry attempts
- `ERROR`: LLM failures, database errors
- `CRITICAL`: Service startup failures, configuration errors

**Key Log Events**:

```python
# Query execution log
logger.info(
    "query_executed",
    query=nl_query,
    generated_sql=sql,
    result_count=len(results),
    execution_time_ms=elapsed_time,
    user_ip=request.client.host  # For demo analytics
)

# Validation failure log
logger.warning(
    "validation_failed",
    query=nl_query,
    generated_sql=sql,
    error_type="DANGEROUS_KEYWORD",
    keyword_detected="DELETE"
)

# LLM error log
logger.error(
    "llm_error",
    query=nl_query,
    error_message=str(e),
    retry_attempt=attempt_number
)
```

**Metrics to Track** (manual inspection for MVP, automated in production):
- Total queries processed
- Average execution time
- Error rate by type (VALIDATION_ERROR, LLM_ERROR, DB_ERROR)
- Top 10 most common queries

**Railway Logs**:
- All logs streamed to Railway dashboard
- 7-day retention (Railway free tier)
- JSON format for easy parsing
