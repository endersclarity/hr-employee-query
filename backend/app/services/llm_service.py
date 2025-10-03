import os
import asyncio
from datetime import datetime
from openai import AsyncOpenAI
import structlog

logger = structlog.get_logger()

# Initialize client lazily to avoid errors during import when API key is not set
_client = None


def get_client():
    """Get or create OpenAI client instance."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

# Employee table schema for LLM context
EMPLOYEE_SCHEMA = """
Table: employees
Columns:
- employee_id (INTEGER, PRIMARY KEY)
- first_name (VARCHAR(100))
- last_name (VARCHAR(100))
- department (VARCHAR(100)) - e.g., 'Engineering', 'Marketing', 'Sales', 'HR', 'Finance'
- role (VARCHAR(100)) - e.g., 'Software Engineer', 'Product Manager'
- employment_status (VARCHAR(50)) - 'Active', 'Terminated', 'On Leave'
- hire_date (DATE)
- leave_type (VARCHAR(50)) - 'Parental Leave', 'Medical Leave', 'Sick Leave', or NULL
- salary_local (DECIMAL(12,2))
- salary_usd (DECIMAL(12,2))
- manager_name (VARCHAR(200))
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
"""

# System prompt with security rules and few-shot examples
SYSTEM_PROMPT = f"""You are a SQL query generator for an HR employee database.

CRITICAL RULES:
1. Generate ONLY SELECT statements
2. Never generate DELETE, DROP, UPDATE, INSERT, or ALTER statements
3. Only query the 'employees' table
4. Use these columns only: employee_id, first_name, last_name, department, role, employment_status, hire_date, leave_type, salary_local, salary_usd, manager_name

IMPORTANT: When querying for employees on leave (parental, medical, sick), filter ONLY by leave_type.
Do NOT add employment_status filters - the leave_type field already indicates they are on leave.

If the user's request cannot be fulfilled with a SELECT query, respond with: "INVALID_REQUEST"

Schema:
{EMPLOYEE_SCHEMA}

Examples:
User: "Show me employees in Engineering with salary greater than 120K"
SQL: SELECT * FROM employees WHERE department = 'Engineering' AND salary_usd > 120000

User: "List employees hired in the last 6 months"
SQL: SELECT * FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'

User: "Who is on parental leave?"
SQL: SELECT * FROM employees WHERE leave_type = 'Parental Leave'

User: "Who is currently on parental leave?"
SQL: SELECT * FROM employees WHERE leave_type = 'Parental Leave'

User: "Show employees managed by John Doe"
SQL: SELECT * FROM employees WHERE manager_name = 'John Doe'
"""


async def validate_api_key():
    """Validate OpenAI API key on startup with test completion call."""
    try:
        client = get_client()
        await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        logger.info("OpenAI API key validated successfully")
    except Exception as e:
        logger.critical(f"OpenAI API key validation failed: {e}")
        raise


async def generate_sql(natural_language_query: str) -> str:
    """
    Convert natural language query to SQL using OpenAI GPT-5 Nano.

    Args:
        natural_language_query: User's natural language query

    Returns:
        Generated SQL query string

    Raises:
        Exception: If LLM request fails after retries or times out
    """
    start_time = datetime.now()
    max_retries = 3
    retry_delays = [1, 2, 4]  # Exponential backoff

    for attempt in range(max_retries):
        try:
            client = get_client()
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4o-mini",  # Using GPT-4o-mini for OpenAI SDK 1.x compatibility (GPT-5 requires SDK 2.x)
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": natural_language_query}
                    ],
                    max_tokens=200  # GPT-4o uses max_tokens not max_completion_tokens
                ),
                timeout=5.0  # 5s timeout
            )

            sql = response.choices[0].message.content.strip()

            # Strip common LLM response prefixes (GPT-4o-mini sometimes includes "SQL: ")
            if sql.upper().startswith("SQL:"):
                sql = sql[4:].strip()

            # Check for INVALID_REQUEST
            if sql == "INVALID_REQUEST":
                raise ValueError("Query cannot be fulfilled with SELECT statement")

            # Log performance
            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.info("llm_sql_generated",
                query=natural_language_query,
                sql=sql,
                elapsed_ms=elapsed_ms,
                attempt=attempt + 1
            )

            return sql

        except asyncio.TimeoutError:
            logger.warning("llm_timeout", attempt=attempt + 1)
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delays[attempt])
                continue
            else:
                raise Exception("LLM request timed out after 3 attempts")

        except Exception as e:
            logger.error("llm_error", error=str(e), attempt=attempt + 1)
            if attempt < max_retries - 1 and "rate_limit" in str(e).lower():
                await asyncio.sleep(retry_delays[attempt])
                continue
            else:
                raise
