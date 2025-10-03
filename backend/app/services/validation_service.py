"""SQL validation and input sanitization service.

This module provides multi-layered security validation for SQL queries:
- Layer 3: Input sanitization (remove comments, semicolons)
- Layer 4: SQL validation (sqlparse, whitelist SELECT)
"""

import sqlparse
from sqlparse.sql import IdentifierList, Identifier
import structlog
from datetime import datetime

logger = structlog.get_logger()


def sanitize_input(query: str) -> str:
    """Remove SQL comment indicators and semicolons to prevent injection.

    Args:
        query: Raw user input query string

    Returns:
        Sanitized query string

    Raises:
        ValueError: If query is empty or exceeds length limit
    """
    # Remove SQL comment indicators
    query = query.replace('--', '').replace('/*', '').replace('*/', '')

    # Remove semicolons (prevent multi-statement injection)
    query = query.replace(';', '')

    # Remove leading/trailing whitespace
    query = query.strip()

    # Check for empty query after sanitization
    if not query:
        raise ValueError("Query cannot be empty")

    # Enforce length limit
    if len(query) > 500:
        raise ValueError("Query too long (max 500 characters)")

    return query


def validate_sql(sql: str, nl_query: str = "") -> bool:
    """Validate that SQL query is safe to execute.

    Performs comprehensive security checks:
    1. Is it a SELECT statement?
    2. Does it contain dangerous keywords?
    3. Does it only reference 'employees' table?

    Args:
        sql: Generated SQL query to validate
        nl_query: Original natural language query (for logging)

    Returns:
        True if validation passes

    Raises:
        ValueError: With specific reason if validation fails
    """
    start_time = datetime.now()

    # Parse SQL
    parsed = sqlparse.parse(sql)
    if not parsed:
        logger.warning("validation_failed",
            nl_query=nl_query,
            generated_sql=sql,
            error_type="INVALID_SYNTAX",
            reason="Invalid SQL syntax"
        )
        raise ValueError("Invalid SQL syntax")

    stmt = parsed[0]

    # Check if SELECT statement
    if stmt.get_type() != 'SELECT':
        logger.warning("validation_failed",
            nl_query=nl_query,
            generated_sql=sql,
            error_type="NON_SELECT",
            reason="Only SELECT statements allowed"
        )
        raise ValueError("Only SELECT queries allowed")

    # Check for dangerous keywords (case-insensitive)
    dangerous_keywords = [
        'DELETE', 'DROP', 'UPDATE', 'INSERT', 'ALTER',
        'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE'
    ]
    sql_upper = sql.upper()
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            logger.warning("validation_failed",
                nl_query=nl_query,
                generated_sql=sql,
                error_type="DANGEROUS_KEYWORD",
                keyword_detected=keyword
            )
            raise ValueError(f"Dangerous keyword detected: {keyword}")

    # Check that only 'employees' table is referenced
    # Extract table names ONLY from FROM clause to avoid false positives from column names
    tables = []
    from_seen = False

    for token in stmt.tokens:
        # Skip whitespace tokens
        if token.is_whitespace:
            continue

        # Check for FROM keyword
        if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
            from_seen = True
            continue

        # After FROM, extract table names until we hit another keyword
        if from_seen:
            if isinstance(token, Identifier):
                # Single table reference
                table_name = token.get_real_name()
                if table_name:
                    tables.append(table_name.lower())
                break  # Single table found, done
            elif isinstance(token, IdentifierList):
                # Multiple tables (JOINs)
                for identifier in token.get_identifiers():
                    if isinstance(identifier, Identifier):
                        table_name = identifier.get_real_name()
                        if table_name:
                            tables.append(table_name.lower())
                break  # All tables extracted, done
            elif token.ttype is sqlparse.tokens.Keyword:
                # Hit next keyword (WHERE, ORDER BY, etc), stop parsing
                break

    # Validate exact match against whitelist
    if not tables or 'employees' not in tables:
        logger.warning("validation_failed",
            nl_query=nl_query,
            generated_sql=sql,
            error_type="INVALID_TABLE",
            reason="Only 'employees' table permitted",
            tables_found=tables
        )
        raise ValueError("Only 'employees' table allowed")

    # Performance monitoring
    elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    logger.info("validation_complete",
        nl_query=nl_query,
        generated_sql=sql,
        elapsed_ms=elapsed_ms
    )

    # Alert if validation is slow
    if elapsed_ms > 50:
        logger.warning("validation_slow", elapsed_ms=elapsed_ms)

    # All checks passed
    return True
