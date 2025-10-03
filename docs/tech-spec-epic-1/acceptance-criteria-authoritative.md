# Acceptance Criteria (Authoritative)

These are the atomic, testable criteria that define Epic 1 completion. All must be satisfied for Epic 1 to be considered complete.

### Functional Acceptance Criteria

**AC1**: User can enter a natural language query (1-500 characters) in a text input field and click a submit button
- **Test**: Input "Show me employees in Engineering with salary > 120K" and click submit
- **Expected**: Query is accepted and processed

**AC2**: System successfully converts all 4 mandatory query types to valid SQL:
- **Test 1**: "Show me employees hired in the last 6 months" → `SELECT * FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'`
- **Test 2**: "List Engineering employees with salary > 120K" → `SELECT * FROM employees WHERE department = 'Engineering' AND salary_usd > 120000`
- **Test 3**: "Who is on parental leave?" → `SELECT * FROM employees WHERE leave_type = 'Parental Leave'`
- **Test 4**: "Show employees managed by John Doe" → `SELECT * FROM employees WHERE manager_name = 'John Doe'`
- **Expected**: All generate valid, executable SQL

**AC3**: System blocks malicious queries and returns appropriate error messages
- **Test 1**: "DELETE FROM employees WHERE department = 'Engineering'" → 400 error, "Only SELECT queries permitted"
- **Test 2**: "DROP TABLE employees" → 400 error, validation failure
- **Test 3**: "UPDATE employees SET salary_usd = 0" → 400 error, dangerous keyword detected
- **Expected**: All malicious queries rejected before execution

**AC4**: Query results are displayed in a tabular format with appropriate column headers
- **Test**: Execute "Show me employees in Engineering" → Results table shows columns: employee_id, first_name, last_name, department, role, salary_usd
- **Expected**: Table renders with headers and data rows

**AC5**: Database contains 50+ employee records covering all test scenarios
- **Test**: Query "Show employees hired in last 6 months" returns at least 5 results
- **Test**: Query "Show Engineering employees with salary > 120K" returns at least 3 results
- **Test**: Query "Who is on parental leave?" returns at least 2 results
- **Test**: Query "Show employees managed by John Doe" returns at least 4 results
- **Expected**: All queries return non-empty results

**AC6**: Database connection uses read-only user with SELECT-only permissions
- **Test**: Manually attempt `INSERT INTO employees ...` using application's database connection
- **Expected**: Permission denied error from PostgreSQL

**AC7**: System responds within 5 seconds for all queries (NFR002)
- **Test**: Execute 10 sample queries, measure end-to-end response time
- **Expected**: All queries complete in < 5 seconds (P95 latency)

**AC8**: Error messages are displayed to user when queries fail
- **Test**: Submit query with 501 characters → "Query too long (max 500 characters)"
- **Test**: Submit empty query → "Query cannot be empty"
- **Test**: Disconnect database, submit query → "Database query failed"
- **Expected**: User-friendly error messages displayed in UI

### Non-Functional Acceptance Criteria

**AC9**: Docker Compose starts all services successfully
- **Test**: Run `docker-compose up` from project root
- **Expected**: Frontend (port 5173), backend (port 8000), and PostgreSQL (port 5432) all start without errors

**AC10**: API endpoint returns structured JSON responses
- **Test**: POST `/api/query` with `{"query": "Show me all employees"}` → Response has `success`, `query`, `generated_sql`, `results`, `result_count`, `execution_time_ms` fields
- **Expected**: JSON schema matches QueryResponse Pydantic model

**AC11**: Health check endpoint responds correctly
- **Test**: GET `/api/health` → Returns `{"status": "healthy", "database": "connected", "timestamp": "..."}`
- **Expected**: 200 status code with valid health data

**AC12**: Structured logs capture query execution metrics
- **Test**: Execute a query, check logs for `query_executed` event with fields: `query`, `generated_sql`, `result_count`, `execution_time_ms`
- **Expected**: JSON logs contain all required fields
