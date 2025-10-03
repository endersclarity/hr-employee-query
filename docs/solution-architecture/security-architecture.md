# Security Architecture

### Multi-Layered Security Approach

**Layer 1: Database-Level Permissions**
- Create read-only PostgreSQL user: `query_app_readonly`
- Grant only SELECT permissions on `employees` table
- No INSERT, UPDATE, DELETE, DROP, ALTER privileges
- Even if SQL injection succeeds, damage is limited

**SQL Setup:**
```sql
CREATE USER query_app_readonly WITH PASSWORD 'secure_random_password';
GRANT CONNECT ON DATABASE hr_db TO query_app_readonly;
GRANT SELECT ON employees TO query_app_readonly;
REVOKE ALL ON employees FROM query_app_readonly;
GRANT SELECT ON employees TO query_app_readonly;
```

**Layer 2: Prompt Engineering Safeguards**

System prompt explicitly constrains LLM behavior:
```python
system_prompt = """You are a SQL query generator for an HR employee database.

CRITICAL RULES:
1. Generate ONLY SELECT statements
2. Never generate DELETE, DROP, UPDATE, INSERT, or ALTER statements
3. Only query the 'employees' table
4. Use these columns only: employee_id, first_name, last_name, department, role, employment_status, hire_date, leave_type, salary_local, salary_usd, manager_name

If the user's request cannot be fulfilled with a SELECT query, respond with: "INVALID_REQUEST"

Schema:
{schema_definition}

Examples:
{few_shot_examples}
"""
```

**Layer 3: Input Sanitization**

```python
def sanitize_input(query: str) -> str:
    """Remove potentially malicious characters before LLM processing."""
    # Remove SQL comment indicators
    query = query.replace('--', '').replace('/*', '').replace('*/', '')
    # Remove semicolons (prevent multi-statement injection)
    query = query.replace(';', '')
    # Limit length
    if len(query) > 500:
        raise ValueError("Query too long (max 500 characters)")
    return query.strip()
```

**Layer 4: SQL Query Validation**

```python
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML

def validate_sql(sql: str) -> bool:
    """Validate that SQL is a safe SELECT query."""
    # Parse SQL
    parsed = sqlparse.parse(sql)
    if not parsed:
        raise ValueError("Invalid SQL syntax")

    stmt: Statement = parsed[0]

    # Check if it's a SELECT statement
    if stmt.get_type() != 'SELECT':
        raise ValueError("Only SELECT queries allowed")

    # Check for dangerous keywords
    dangerous_keywords = ['DELETE', 'DROP', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
    sql_upper = sql.upper()
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            raise ValueError(f"Dangerous keyword detected: {keyword}")

    # Check that only 'employees' table is referenced
    if 'employees' not in sql.lower():
        raise ValueError("Only 'employees' table is permitted")

    return True
```

**Layer 5: Rate Limiting (Future Enhancement)**

Not implemented in MVP, but recommended for production:
- Limit to 10 queries per minute per IP
- Use Redis or in-memory counter
- Prevents abuse and API cost runaway

---
