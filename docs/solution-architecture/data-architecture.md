# Data Architecture

### Database Schema

**employees table:**
```sql
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    employment_status VARCHAR(50) NOT NULL,  -- 'Active', 'Terminated', 'On Leave'
    hire_date DATE NOT NULL,
    leave_type VARCHAR(50),  -- nullable, 'Parental Leave', 'Medical Leave', etc.
    salary_local DECIMAL(12, 2) NOT NULL,
    salary_usd DECIMAL(12, 2) NOT NULL,
    manager_name VARCHAR(200),  -- nullable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_department ON employees(department);
CREATE INDEX idx_hire_date ON employees(hire_date);
CREATE INDEX idx_employment_status ON employees(employment_status);
CREATE INDEX idx_manager_name ON employees(manager_name);
```

**Indexes Rationale:**
Indexes on `department`, `hire_date`, `employment_status`, and `manager_name` optimize the 4 mandatory query types from the requirements.

**query_logs table (optional):**
```sql
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    natural_language_query TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    faithfulness_score DECIMAL(3, 2),
    answer_relevance_score DECIMAL(3, 2),
    context_precision_score DECIMAL(3, 2),
    result_count INTEGER,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Mock Data Design (Critical for Demo):**

Must include employees that satisfy all 4 example queries:
- **"Last 6 months hires":** At least 5 employees with `hire_date` within last 6 months
- **"Engineering salary > 120K":** At least 3 employees with `department='Engineering'` AND `salary_usd > 120000`
- **"Parental leave":** At least 2 employees with `leave_type='Parental Leave'`
- **"Managed by John Doe":** At least 4 employees with `manager_name='John Doe'`

**Seed Data Script:** `backend/app/db/seed.py` generates ~50 diverse employee records covering all scenarios.

---
