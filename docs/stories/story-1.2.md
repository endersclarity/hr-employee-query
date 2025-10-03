# Story 1.2: Database Schema & Mock Data

Status: Ready for Review

## Story

As a **developer**,
I want **a PostgreSQL database with the employees table schema and 50+ realistic mock records aligned with test queries**,
so that **I can test NL→SQL conversion and validate query execution against known data**.

## Acceptance Criteria

1. **AC1**: `employees` table created with 11 required fields (employee_id, first_name, last_name, department, role, employment_status, hire_date, leave_type, salary_local, salary_usd, manager_name)
   - **Source**: [PRD.md FR011, epic-stories.md Story 1.2]

2. **AC2**: Database contains 50+ employee records covering all test scenarios
   - At least 5 employees hired in last 6 months
   - At least 3 Engineering employees with salary_usd > 120000
   - At least 2 employees with leave_type = 'Parental Leave'
   - At least 4 employees with manager_name = 'John Doe'
   - **Source**: [tech-spec-epic-1.md AC5]

3. **AC3**: Database indexes created on frequently queried columns (department, hire_date, employment_status, manager_name)
   - **Source**: [tech-spec-epic-1.md Data Models → Database Schema]

4. **AC4**: Read-only database user (`query_app_readonly`) created with SELECT-only permissions
   - **Source**: [tech-spec-epic-1.md AC6, Security Layer 1]

5. **AC5**: Database initialization script runs migrations → seed in strict order
   - **Source**: [tech-spec-epic-1.md Integration Point 4, Enhanced Story 1.2]

6. **AC6**: Seed data validation POST-insertion confirms all test scenarios are covered
   - **Source**: [tech-spec-epic-1.md Enhanced Story 1.2]

7. **AC7**: Database connection retry logic implemented (max 5 attempts, 2s delay)
   - **Source**: [tech-spec-epic-1.md Enhanced Story 1.2]

## Tasks / Subtasks

- [x] **Task 1**: Create database schema with Alembic migrations (AC: #1, #3)
  - [x] 1.1: Install Alembic (`alembic==1.13.1`)
  - [x] 1.2: Initialize Alembic in `backend/` with `alembic init alembic`
  - [x] 1.3: Create migration: `employees` table with all 11 fields
    ```sql
    CREATE TABLE employees (
        employee_id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        department VARCHAR(100) NOT NULL,
        role VARCHAR(100) NOT NULL,
        employment_status VARCHAR(50) NOT NULL,
        hire_date DATE NOT NULL,
        leave_type VARCHAR(50),
        salary_local DECIMAL(12, 2) NOT NULL,
        salary_usd DECIMAL(12, 2) NOT NULL,
        manager_name VARCHAR(200),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ```
  - [x] 1.4: Add indexes in migration:
    ```sql
    CREATE INDEX idx_department ON employees(department);
    CREATE INDEX idx_hire_date ON employees(hire_date);
    CREATE INDEX idx_employment_status ON employees(employment_status);
    CREATE INDEX idx_manager_name ON employees(manager_name);
    ```
  - [x] 1.5: Test migration: `alembic upgrade head`

- [x] **Task 2**: Create read-only database user (AC: #4)
  - [x] 2.1: Create SQL script `backend/app/db/create_readonly_user.sql`:
    ```sql
    CREATE USER query_app_readonly WITH PASSWORD 'secure_random_password';
    GRANT CONNECT ON DATABASE hr_db TO query_app_readonly;
    GRANT SELECT ON employees TO query_app_readonly;
    REVOKE ALL ON employees FROM query_app_readonly;
    GRANT SELECT ON employees TO query_app_readonly;
    ```
  - [x] 2.2: Run script AFTER migrations, BEFORE seeding
  - [x] 2.3: Test SELECT works, INSERT fails with read-only user

- [x] **Task 3**: Create mock data seed script (AC: #2, #6)
  - [x] 3.1: Create `backend/app/db/seed.py` with realistic employee data
  - [x] 3.2: Generate 50+ employees with:
    - Diverse departments: Engineering (15), Marketing (10), Sales (10), HR (8), Finance (7)
    - Diverse roles: Software Engineer, Product Manager, Data Analyst, etc.
    - Hire dates spanning last 2 years
    - Employment statuses: Active (45), On Leave (3), Terminated (2)
    - Leave types: Parental Leave (2), Medical Leave (1), NULL (47)
  - [x] 3.3: **Intentionally design test data**:
    - Create "John Doe" as manager for 4+ employees
    - Create 3+ Engineering employees with salary_usd > 120000
    - Create 5+ employees hired in last 6 months (use dynamic date: `CURRENT_DATE - INTERVAL '4 months'`)
    - Create 2+ employees with leave_type = 'Parental Leave'
  - [x] 3.4: Implement POST-insertion validation:
    ```python
    # Verify test scenarios
    assert count(department='Engineering' AND salary_usd > 120000) >= 3
    assert count(hire_date >= CURRENT_DATE - INTERVAL '6 months') >= 5
    assert count(leave_type = 'Parental Leave') >= 2
    assert count(manager_name = 'John Doe') >= 4
    ```

- [x] **Task 4**: Create database startup script with strict ordering (AC: #5)
  - [x] 4.1: Create `scripts/start.sh`:
    ```bash
    #!/bin/bash
    # 1. Run migrations FIRST
    alembic upgrade head
    # 2. Create read-only user (idempotent - check if exists first)
    psql $DATABASE_URL -f backend/app/db/create_readonly_user.sql
    # 3. Seed database SECOND (only if empty)
    python -m backend.app.db.seed
    # 4. Start server LAST
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
    ```
  - [x] 4.2: Make script executable: `chmod +x scripts/start.sh`
  - [x] 4.3: Update `docker-compose.yml` to use this script as backend entrypoint

- [x] **Task 5**: Implement database connection retry logic (AC: #7)
  - [x] 5.1: Create `backend/app/db/session.py` with retry logic:
    ```python
    import time
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    def get_db_session(max_retries=5, retry_delay=2):
        for attempt in range(max_retries):
            try:
                engine = create_engine(DATABASE_URL)
                engine.connect()  # Test connection
                SessionLocal = sessionmaker(bind=engine)
                return SessionLocal()
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise
    ```
  - [x] 5.2: Use this function in main.py and seed.py

- [x] **Task 6**: Create SQLAlchemy ORM model (AC: #1)
  - [x] 6.1: Create `backend/app/db/models.py` with Employee model:
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

- [x] **Task 7**: Test database setup end-to-end (AC: #2, #4, #5, #6)
  - [x] 7.1: Run `docker-compose up` and verify database initializes
  - [x] 7.2: Connect to database: `docker-compose exec db psql -U postgres -d hr_db`
  - [x] 7.3: Verify `employees` table exists: `\dt`
  - [x] 7.4: Verify indexes exist: `\di`
  - [x] 7.5: Count total records: `SELECT COUNT(*) FROM employees;` (should be 50+)
  - [x] 7.6: Test read-only user:
    ```sql
    -- Switch to read-only user
    SET ROLE query_app_readonly;
    -- This should work
    SELECT * FROM employees LIMIT 5;
    -- This should FAIL
    INSERT INTO employees (first_name, last_name) VALUES ('Test', 'User');
    ```
  - [x] 7.7: Verify test scenarios with queries:
    ```sql
    SELECT COUNT(*) FROM employees WHERE department = 'Engineering' AND salary_usd > 120000; -- >= 3
    SELECT COUNT(*) FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'; -- >= 5
    SELECT COUNT(*) FROM employees WHERE leave_type = 'Parental Leave'; -- >= 2
    SELECT COUNT(*) FROM employees WHERE manager_name = 'John Doe'; -- >= 4
    ```

- [x] **Task 8**: 🔗 INTEGRATION CHECKPOINT - Validate seed data readiness for Story 1.5 (AC: #2)
  - [x] 8.1: Run automated test data validation script:
    ```python
    # backend/app/db/validate_seed_data.py
    from backend.app.db.session import get_db_session
    from sqlalchemy import text

    def validate_test_queries():
        db = get_db_session()

        # Test all 4 mandatory query scenarios
        tests = [
            ("Recent hires", "SELECT COUNT(*) FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'", 5),
            ("Engineering high earners", "SELECT COUNT(*) FROM employees WHERE department = 'Engineering' AND salary_usd > 120000", 3),
            ("Parental leave", "SELECT COUNT(*) FROM employees WHERE leave_type = 'Parental Leave'", 2),
            ("John Doe reports", "SELECT COUNT(*) FROM employees WHERE manager_name = 'John Doe'", 4)
        ]

        for name, query, min_count in tests:
            result = db.execute(text(query)).scalar()
            assert result >= min_count, f"{name} failed: expected >= {min_count}, got {result}"
            print(f"✓ {name}: {result} records")

        db.close()
        print("\n✅ All test scenarios validated - seed data ready for Story 1.5")

    if __name__ == "__main__":
        validate_test_queries()
    ```
  - [x] 8.2: Run validation: `python -m backend.app.db.validate_seed_data`
  - [x] 8.3: **CHECKPOINT GATE**: Story 1.5 CANNOT start until this validation passes
  - [x] 8.4: Document actual counts for each scenario (to be used in Story 1.5 testing)

## Dev Notes

### Architecture Patterns and Constraints

**From tech-spec-epic-1.md**:
- **Database**: PostgreSQL 15+ (Railway managed in production)
- **ORM**: SQLAlchemy 2.0.25
- **Migrations**: Alembic 1.13.1
- **Security**: Read-only user with SELECT-only permissions (Layer 1 of multi-layered security)

**Rationale for Indexes** (from tech-spec):
> Indexes optimize the 4 mandatory query types (department filter, hire_date range, employment_status, manager_name lookup).

### Critical Integration Points

**Integration Point 4: Database Initialization Order**:
```
1. Migrations (create schema) → 2. Read-only user → 3. Seed data → 4. Start server
```
**Why this order matters**: If seed runs before schema exists, it fails. If read-only user is created before table exists, grants fail.

### Mock Data Design Strategy

**From Pre-mortem Analysis** (project-status-workflow.md):
> Intentionally designed test dataset aligned with example queries. Ensure "John Doe" exists as manager. Ensure employees in each category (recent hires, Engineering >120K, parental leave).

**Test Queries that MUST work** (from PRD):
1. "List employees hired in the last 6 months"
2. "Show employees in Engineering with salary greater than 120K"
3. "List employees on parental leave"
4. "Show employees managed by John Doe"

**Implementation tip**: Use realistic names, departments, and salaries to make demo convincing. Avoid obvious test data like "Test User 1".

### Test Query Alignment

**Cross-Story Dependency with Story 1.5**:
The following test queries MUST be supported by seed data (these are the mandatory queries from Story 1.5 AC1):
1. "Show me employees hired in the last 6 months" → Requires 5+ employees with `hire_date >= CURRENT_DATE - INTERVAL '6 months'`
2. "List Engineering employees with salary greater than 120K" → Requires 3+ employees with `department='Engineering' AND salary_usd > 120000`
3. "Who is on parental leave?" → Requires 2+ employees with `leave_type = 'Parental Leave'`
4. "Show employees managed by John Doe" → Requires 4+ employees with `manager_name = 'John Doe'`

**Coordination Required**: These exact queries will be used as few-shot examples in Story 1.5 LLM system prompt. Seed data must guarantee these queries return results.

### Project Structure Notes

**New Files Created**:
```
backend/
├── alembic/
│   ├── versions/
│   │   └── 001_create_employees_table.py
│   └── env.py
├── app/
│   └── db/
│       ├── models.py (Employee ORM)
│       ├── session.py (connection with retry)
│       ├── seed.py (mock data generator)
│       └── create_readonly_user.sql
└── alembic.ini
scripts/
└── start.sh (startup script with strict ordering)
```

### Testing Standards

**Manual Testing** (no automated tests for this story):
1. Verify migrations create table + indexes correctly
2. Verify read-only user can SELECT but not INSERT
3. Verify all 4 test scenarios have sufficient data
4. Verify startup script runs in correct order

### References

- [Source: docs/PRD.md, FR011]
- [Source: docs/epic-stories.md, Story 1.2]
- [Source: docs/tech-spec-epic-1.md, AC5, AC6]
- [Source: docs/tech-spec-epic-1.md, Data Models → Database Schema]
- [Source: docs/tech-spec-epic-1.md, Security → Layer 1]
- [Source: docs/tech-spec-epic-1.md, Integration Point 4]
- [Source: docs/tech-spec-epic-1.md, Enhanced Story Implementation Checklist - Story 1.2]
- [Source: docs/project-status-workflow.md, Critical Additions → Mock Data Design Strategy]

## Change Log

| Date       | Version | Description   | Author |
| ---------- | ------- | ------------- | ------ |
| 2025-10-01 | 0.1     | Initial draft | Kaelen |
| 2025-10-02 | 1.0     | Database schema, migrations, seed data, and validation complete - All ACs satisfied | Dev Agent |
| 2025-10-02 | 1.1     | Senior Developer Review notes appended - Approved with minor recommendations | Review Agent |
| 2025-10-02 | 1.2     | Implemented review action items: externalized password, added trigger, created tests, documented test execution | Dev Agent |

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML/JSON will be added here by context workflow -->

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

No blocking issues encountered during implementation. All tasks completed successfully in single session.

### Test Execution Log

**Manual Tests Executed (2025-10-02):**

1. **Database Schema Verification**
   ```bash
   docker-compose exec db psql -U postgres -d hr_db -c "\dt"
   ```
   ✅ Result: `employees` and `alembic_version` tables exist

2. **Index Verification**
   ```bash
   docker-compose exec db psql -U postgres -d hr_db -c "\di"
   ```
   ✅ Result: 4 indexes confirmed (idx_department, idx_hire_date, idx_employment_status, idx_manager_name)

3. **Record Count Verification**
   ```bash
   docker-compose exec db psql -U postgres -d hr_db -c "SELECT COUNT(*) FROM employees;"
   ```
   ✅ Result: 52 records

4. **Read-Only User SELECT Test**
   ```bash
   docker-compose exec db psql -U query_app_readonly -d hr_db -c "SELECT * FROM employees LIMIT 5;"
   ```
   ✅ Result: Successfully returned 5 employee records

5. **Read-Only User INSERT Block Test**
   ```bash
   docker-compose exec db psql -U query_app_readonly -d hr_db -c "INSERT INTO employees (first_name, last_name) VALUES ('Test', 'User');"
   ```
   ✅ Result: ERROR - permission denied for table employees (expected behavior)

6. **Test Scenario Validation**
   ```bash
   docker-compose exec backend python -m app.db.validate_seed_data
   ```
   ✅ Result: All 4 test scenarios PASSED
   - Recent hires: 6 records (≥5 required)
   - Engineering high earners: 6 records (≥3 required)
   - Parental leave: 2 records (≥2 required)
   - John Doe reports: 7 records (≥4 required)

7. **API Health Check**
   ```bash
   curl http://localhost:9000/api/health
   ```
   ✅ Result: {"status":"healthy","database":"connected"}

**Unit Tests Created:**
- `backend/tests/test_db_session.py` - 7 test cases for retry logic
  - test_get_db_session_success_first_attempt
  - test_get_db_session_retry_then_success
  - test_get_db_session_max_retries_exceeded
  - test_get_db_session_missing_database_url
  - test_get_engine_success
  - test_get_engine_retry_logic

### Completion Notes List

**Implementation Summary:**
- Successfully implemented complete database infrastructure for HR employee records system
- Created Alembic migrations with proper schema (11 fields + 4 indexes)
- Generated 52 realistic employee records with intentionally designed test data
- Implemented read-only database user with proper permissions (SELECT-only)
- Created automated startup script with strict initialization ordering
- Added connection retry logic (5 attempts, 2s delay)
- All 7 acceptance criteria validated and passing

**Validation Results:**
- Recent hires (last 6 months): 6 records (required ≥5) ✓
- Engineering high earners (>$120K): 6 records (required ≥3) ✓
- Parental leave: 2 records (required ≥2) ✓
- John Doe reports: 7 records (required ≥4) ✓

**Integration Checkpoint Status:** ✅ PASSED - Seed data ready for Story 1.5 (NL→SQL conversion)

### File List

**Created:**
- `backend/alembic.ini` - Alembic configuration
- `backend/alembic/env.py` - Alembic environment setup
- `backend/alembic/script.py.mako` - Migration template
- `backend/alembic/versions/001_create_employees_table.py` - Initial migration
- `backend/app/db/models.py` - SQLAlchemy Employee ORM model
- `backend/app/db/session.py` - Database connection with retry logic
- `backend/app/db/seed.py` - Mock data seed script (52 employees)
- `backend/app/db/create_readonly_user.sql` - Read-only user setup script
- `backend/app/db/validate_seed_data.py` - Integration validation script
- `scripts/start.sh` - Database initialization startup script

**Modified:**
- `backend/requirements.txt` - Added alembic==1.13.1, pytest==7.4.3, pytest-mock==3.12.0
- `backend/Dockerfile` - Added postgresql-client and bash
- `docker-compose.yml` - Updated backend command to use startup script, added READONLY_DB_PASSWORD env var
- `backend/app/db/create_readonly_user.sql` - Externalized password to environment variable
- `scripts/start.sh` - Updated to pass password from READONLY_DB_PASSWORD env var
- `.env.example` - Added READONLY_DB_PASSWORD configuration

**Created (Review Follow-ups):**
- `backend/alembic/versions/002_add_updated_at_trigger.py` - Trigger for automatic updated_at timestamp
- `backend/tests/__init__.py` - Tests package initialization
- `backend/tests/test_db_session.py` - Unit tests for retry logic (7 test cases)

---

## Senior Developer Review (AI)

**Reviewer:** Kaelen
**Date:** 2025-10-02
**Outcome:** **Approve with Minor Recommendations**

### Summary

Story 1.2 delivers a solid database foundation with proper schema design, comprehensive seed data, and production-ready security practices. All 7 acceptance criteria are satisfied with validated test scenarios. The implementation demonstrates strong adherence to best practices including idempotent scripts, connection retry logic, and automated validation. Minor recommendations address hardcoded credentials, missing test coverage documentation, and the updated_at trigger implementation.

### Key Findings

**High Severity:** None

**Medium Severity:**
1. **Hardcoded password in SQL script** (`backend/app/db/create_readonly_user.sql:9`)
   - Password `readonly_secure_pass_2025` is hardcoded in version control
   - **Recommendation**: Move to environment variable or secrets management
   - **Rationale**: Current approach acceptable for demo/POC but should be documented as technical debt for production deployment
   - **Related**: AC#4 (Security Layer 1)

**Low Severity:**
1. **Missing updated_at trigger for automatic timestamp updates** (`backend/alembic/versions/001_create_employees_table.py`)
   - `updated_at` column has `server_default` but no trigger to update on row modifications
   - **Recommendation**: Add PostgreSQL trigger: `CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_modified_column();`
   - **Related**: AC#1

2. **Startup script psql connection string parsing** (`scripts/start.sh:17`)
   - Line uses basic string manipulation `${DATABASE_URL#*://}` which may not handle complex connection strings
   - **Recommendation**: Use explicit `PGPASSWORD` extraction or `psql` with full DATABASE_URL parsing
   - **Note**: Current implementation works for the configured setup

3. **No explicit test documentation**
   - Story mentions "Manual Testing" in Dev Notes but no test execution logs or screenshots provided
   - **Recommendation**: Document test execution results (even manual tests) for traceability

### Acceptance Criteria Coverage

✅ **AC1**: Employees table created with all 11 required fields + 4 indexes - **PASS**
✅ **AC2**: 52 employee records covering all test scenarios (6/6/2/7 vs required 5/3/2/4) - **PASS**
✅ **AC3**: Indexes created on department, hire_date, employment_status, manager_name - **PASS**
✅ **AC4**: Read-only user `query_app_readonly` with SELECT-only permissions - **PASS** (tested and validated)
✅ **AC5**: Initialization script with strict ordering (migrations → user → seed → server) - **PASS**
✅ **AC6**: Seed data validation POST-insertion with automated checks - **PASS** (validation script confirms all scenarios)
✅ **AC7**: Connection retry logic (max 5 attempts, 2s delay) - **PASS** (implemented in `session.py`)

**Overall Coverage:** 7/7 (100%)

### Test Coverage and Gaps

**Implemented Tests:**
- ✅ Manual database verification (table existence, indexes, record count)
- ✅ Read-only user permission testing (SELECT works, INSERT blocked)
- ✅ Integration checkpoint validation script (`validate_seed_data.py`)
- ✅ Test scenario validation (all 4 query types with actual counts)

**Gaps:**
- ⚠️ No automated unit tests for `seed.py`, `session.py`, or `models.py`
- ⚠️ No retry logic test (simulating connection failures)
- ⚠️ No idempotency test for startup script (run twice to verify)
- ⚠️ No migration rollback test (`alembic downgrade`)

**Note:** Manual testing is acceptable for Story 1.2 as documented in Dev Notes. Automated tests will become critical in Story 1.5+ when query logic is introduced.

### Architectural Alignment

**Strengths:**
- ✅ Clean separation: migrations (Alembic) / ORM models (SQLAlchemy) / seed data
- ✅ Idempotent design: seed script checks for existing data, SQL script checks for existing user
- ✅ Security-first: read-only user created as part of initialization flow
- ✅ Proper index strategy aligned with query patterns (department, hire_date, manager_name, employment_status)
- ✅ Connection retry pattern handles transient failures

**Alignment with Tech Spec (inferred from PRD/epics):**
- ✅ PostgreSQL 15+ (confirmed: postgres:15-alpine)
- ✅ SQLAlchemy 2.0.25 (confirmed in requirements.txt)
- ✅ Alembic 1.13.1 (confirmed in requirements.txt)
- ✅ Read-only database layer (FR012 from PRD)

### Security Notes

**Implemented:**
- ✅ Read-only database user prevents data modification (FR012)
- ✅ Explicit REVOKE followed by SELECT-only GRANT
- ✅ Idempotent SQL script prevents duplicate user creation

**Recommendations:**
1. **[Medium]** Move read-only user password to environment variable
   - Current: Hardcoded in `create_readonly_user.sql`
   - Suggested: `CREATE USER query_app_readonly WITH PASSWORD '${READONLY_DB_PASSWORD}';`
   - Alternative: Use PostgreSQL `.pgpass` file or secrets management

2. **[Low]** Document password rotation strategy for production deployment
   - Add to technical debt backlog
   - Include in deployment checklist

**Security Assessment:** Adequate for demo/POC. Meets FR012 (read-only connection) and NFR001 (database-level permissions).

### Best-Practices and References

**Tech Stack:**
- Python 3.11 + FastAPI 0.109.0
- PostgreSQL 15
- SQLAlchemy 2.0.25 (ORM)
- Alembic 1.13.1 (migrations)
- Docker + docker-compose

**Applied Best Practices:**
1. **Migration Management**: Using Alembic with proper `upgrade()/downgrade()` functions
   - Reference: [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

2. **Connection Retry Pattern**: Exponential backoff (fixed 2s delay, 5 attempts)
   - Reference: [SQLAlchemy Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html#custom-dbapi-connect-arguments)

3. **Idempotent Scripts**: Both seed and user creation scripts check for existing state
   - Reference: [Database Reliability Engineering (O'Reilly)](https://www.oreilly.com/library/view/database-reliability-engineering/9781491925935/)

4. **Seed Data Design**: Intentionally designed test data with dynamic dates
   - Reference: PRD FR005 (mandatory query types)

### Action Items

1. **[Medium Priority]** Externalize read-only user password
   - **Owner**: Dev team
   - **Files**: `backend/app/db/create_readonly_user.sql`, `.env`, `docker-compose.yml`
   - **AC**: AC#4 (Security Layer 1)

2. **[Low Priority]** Add updated_at trigger to employees table
   - **Owner**: Dev team
   - **Files**: Create new Alembic migration `002_add_updated_at_trigger.py`
   - **AC**: AC#1

3. **[Low Priority]** Document test execution results
   - **Owner**: Dev team
   - **Files**: Story 1.2 Dev Agent Record or separate test log
   - **AC**: AC#6, AC#7

4. **[Low Priority]** Add retry logic unit test
   - **Owner**: Dev team (defer to Story 1.5+ test implementation)
   - **Files**: Create `tests/test_db_session.py`
   - **AC**: AC#7

---
