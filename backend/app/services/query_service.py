"""Query service for executing SQL queries against the database."""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, TimeoutError, IntegrityError, DatabaseError
import structlog

from app.db.session import get_db_session
from app.api.models import QueryResponse
from app.services.llm_service import generate_sql
from app.services.validation_service import sanitize_input, validate_sql
from app.services import ragas_service
from app.db.models import QueryLog

logger = structlog.get_logger()


def _serialize_value(value):
    """Convert database values to JSON-serializable types."""
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, date):
        return value.isoformat()
    return value


def _log_query(nl_query: str, sql: str, results: list, elapsed_ms: int) -> int | None:
    """
    Log query execution to query_logs table.

    RAGAS scores are calculated asynchronously in background task.
    Initial status is 'pending', will be updated to 'evaluating' -> 'completed'/'failed'.

    Args:
        nl_query: Natural language query
        sql: Generated SQL
        results: Query results
        elapsed_ms: Execution time in milliseconds

    Returns:
        Query log ID for background task reference, or None if logging failed
    """
    try:
        db = get_db_session()
        try:
            query_log = QueryLog(
                natural_language_query=nl_query,
                generated_sql=sql,
                evaluation_status='pending',  # Will be updated by background task
                result_count=len(results),
                execution_time_ms=elapsed_ms
            )
            db.add(query_log)
            db.commit()
            query_log_id = query_log.id
            logger.info("query_logged", query_log_id=query_log_id, evaluation_status='pending')
            return query_log_id
        finally:
            db.close()
    except Exception as e:
        logger.error("query_logging_failed", error=str(e))
        return None  # Don't block query response on logging failure


async def execute_query(nl_query: str) -> QueryResponse:
    """
    Execute a natural language query against the database.

    Args:
        nl_query: Natural language query string

    Returns:
        QueryResponse with results or error information
    """
    start_time = datetime.now()

    try:
        # Step 1: Sanitize input
        sanitized_query = sanitize_input(nl_query)

        # Step 2: Generate SQL from LLM
        sql = await generate_sql(sanitized_query)

        # Step 3: Validate SQL
        validate_sql(sql, nl_query=nl_query)

        # Step 4: Execute SQL with timeout
        db = get_db_session()
        try:
            result = db.execute(
                text(sql).execution_options(timeout=3)
            )

            # Convert to list of dicts using SQLAlchemy 2.0 pattern
            # Serialize Decimal and date types to JSON-compatible types
            results = [
                {key: _serialize_value(value) for key, value in row.items()}
                for row in result.mappings()
            ]

            # Check result size (AC4: max 1000 rows)
            if len(results) > 1000:
                logger.warning("result_set_truncated", count=len(results))
                results = results[:1000]

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Log query to query_logs table with 'pending' status
            # RAGAS evaluation will run in background task
            query_log_id = _log_query(nl_query, sql, results, elapsed_ms)

            return QueryResponse(
                success=True,
                query=nl_query,
                generated_sql=sql,
                results=results,
                result_count=len(results),
                execution_time_ms=elapsed_ms,
                query_log_id=query_log_id,  # For background task
                evaluation_status='pending'  # RAGAS scores will be calculated async
            )

        finally:
            db.close()

    except TimeoutError:
        logger.warning("query_timeout", query=nl_query, sql=sql if 'sql' in locals() else None)
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return QueryResponse(
            success=False,
            query=nl_query,
            error="Query execution timed out (>3s). Try simplifying your query.",
            error_type="DB_ERROR",
            execution_time_ms=elapsed_ms
        )

    except OperationalError as e:
        logger.error("db_connection_error", error=str(e))
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return QueryResponse(
            success=False,
            query=nl_query,
            error="Database connection failed. Please try again.",
            error_type="DB_ERROR",
            execution_time_ms=elapsed_ms
        )

    except IntegrityError as e:
        logger.error("db_integrity_error", error=str(e), sql=sql if 'sql' in locals() else None)
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return QueryResponse(
            success=False,
            query=nl_query,
            error="Database integrity error occurred.",
            error_type="DB_ERROR",
            execution_time_ms=elapsed_ms
        )

    except ValueError as e:
        # Validation error
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return QueryResponse(
            success=False,
            query=nl_query,
            error=str(e),
            error_type="VALIDATION_ERROR",
            execution_time_ms=elapsed_ms
        )

    except DatabaseError as e:
        logger.error("db_execution_error", error=str(e), sql=sql if 'sql' in locals() else None)
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return QueryResponse(
            success=False,
            query=nl_query,
            error=f"Database error: {str(e)}",
            error_type="DB_ERROR",
            execution_time_ms=elapsed_ms
        )

    except Exception as e:
        logger.error("query_execution_error", error=str(e), query=nl_query)
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return QueryResponse(
            success=False,
            query=nl_query,
            error=str(e),
            error_type="LLM_ERROR",
            execution_time_ms=elapsed_ms
        )
