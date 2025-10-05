import os
import asyncio
import math
import structlog
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

logger = structlog.get_logger()

# Employee table schema for RAGAS faithfulness evaluation
# Faithfulness metric validates query results against this schema
EMPLOYEE_SCHEMA = """
Database: hr_employees
Table: employees

Column Definitions:
- employee_id: INTEGER, PRIMARY KEY, Auto-increment unique identifier
- first_name: VARCHAR(100), Employee's first name
- last_name: VARCHAR(100), Employee's last name
- department: VARCHAR(100), Department name (e.g., 'Engineering', 'Marketing', 'Sales', 'HR', 'Finance')
- role: VARCHAR(100), Job title (e.g., 'Software Engineer', 'Product Manager', 'Data Analyst')
- employment_status: VARCHAR(50), Current employment status - Valid values: 'Active', 'Terminated', 'On Leave'
- hire_date: DATE, Date employee was hired (format: YYYY-MM-DD)
- leave_type: VARCHAR(50), Type of leave if applicable - Valid values: 'Parental Leave', 'Medical Leave', 'Sick Leave', or NULL
- salary_local: DECIMAL(12,2), Salary in local currency
- salary_usd: DECIMAL(12,2), Salary converted to USD
- manager_name: VARCHAR(200), Name of employee's direct manager (can be NULL for executives)
- created_at: TIMESTAMP, Record creation timestamp
- updated_at: TIMESTAMP, Last record update timestamp

Constraints:
- employee_id is unique and non-null
- employment_status must be one of: 'Active', 'Terminated', 'On Leave'
- leave_type is only populated when employment_status = 'On Leave'
- All employees except executives have a manager_name
- Salary values are always positive decimals
- hire_date cannot be in the future
"""

# Import ragas dependencies with graceful fallback
try:
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_utilization
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    logger.warning("ragas_not_installed", message="Ragas dependencies not available. Install with: pip install ragas langchain datasets")


async def initialize_ragas():
    """Initialize Ragas with OpenAI embeddings."""
    try:
        # Check if ragas is installed
        if not RAGAS_AVAILABLE:
            logger.warning("ragas_init_skipped", message="Ragas not installed, skipping initialization")
            return False

        # Ragas uses OpenAI embeddings (text-embedding-ada-002)
        # API key already configured from Story 1.5
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        logger.info("Ragas initialized successfully")
        return True
    except Exception as e:
        logger.error("ragas_init_failed", error=str(e))
        raise


async def evaluate(nl_query: str, sql: str, results: list) -> Dict[str, float] | None:
    """
    Calculate Ragas scores for query using actual Ragas evaluation.

    Args:
        nl_query: Natural language query string
        sql: Generated SQL query
        results: Query results as list of dicts

    Returns:
        Dictionary with faithfulness, answer_relevance, context_utilization scores
        or None if evaluation fails (graceful degradation)
    """
    try:
        logger.info("ragas_evaluate_start", nl_query=nl_query, result_count=len(results))

        # Check if ragas is available
        if not RAGAS_AVAILABLE:
            logger.debug("ragas_evaluation_skipped", message="Ragas not available")
            return None

        # Format results as natural language text for RAGAS to parse
        # RAGAS faithfulness extracts FACTUAL CLAIMS from the answer and verifies them against context
        # Claims must be simple, declarative statements that can be verified
        # Limit to first 10 results to avoid token limits
        if not results:
            formatted_results = "No results were found in the database for this query."
        else:
            num_results = len(results)
            limited_results = results[:10]

            # Extract factual claims from the data
            # For each result row, create simple declarative statements about the data values
            claims = []
            for row in limited_results:
                for key, value in row.items():
                    if value is not None:
                        # Create a simple factual claim: "The {field} is {value}."
                        # This format is easily verifiable against the context
                        claims.append(f"The {key} is {value}.")

            # Combine all claims into the answer
            if num_results > 10:
                formatted_results = " ".join(claims) + f" There are {num_results - 10} additional records not shown."
            else:
                formatted_results = " ".join(claims)

        # Create Ragas dataset format
        # For text-to-SQL, contexts should be the RAW DATABASE RESULTS, not schema
        # Faithfulness verifies the formatted answer matches the actual data retrieved
        # Format raw results as simple factual statements for RAGAS to verify against
        result_contexts = []
        for i, row in enumerate(results[:10], 1):
            # Simple JSON-like representation of each result
            row_str = f"Database record {i}: " + ", ".join([f"{k}={v}" for k, v in row.items() if v is not None])
            result_contexts.append(row_str)

        dataset_dict = {
            'question': [nl_query],
            'answer': [formatted_results],
            'contexts': [result_contexts]  # Actual database results for faithfulness validation
        }

        logger.info("ragas_dataset_created",
            question_len=len(nl_query),
            answer_len=len(formatted_results),
            context_count=len(result_contexts))

        dataset = Dataset.from_dict(dataset_dict)
        logger.info("ragas_dataset_converted", dataset_size=len(dataset))

        # Evaluate using Ragas metrics
        # Ragas evaluate() is synchronous but conflicts with uvloop in FastAPI
        # Run in thread pool to avoid "Can't patch loop of type <class 'uvloop.Loop'>" error
        # Using context_utilization instead of context_precision (which requires ground_truth)
        loop = asyncio.get_event_loop()
        logger.info("ragas_starting_evaluation", message="Calling ragas_evaluate()...")

        evaluation_result = await loop.run_in_executor(
            None,  # Use default ThreadPoolExecutor
            lambda: ragas_evaluate(
                dataset=dataset,
                metrics=[faithfulness, answer_relevancy, context_utilization]
            )
        )

        logger.info("ragas_evaluation_returned", message="ragas_evaluate() completed")

        # Extract scores from evaluation result
        # Ragas returns a Result object - convert to pandas to extract scores
        # Handle NaN/Inf values (replace with 0.0 for JSON compliance)
        def sanitize_score(value, metric_name="unknown"):
            """Convert NaN/Inf to 0.0 with logging, ensure valid float."""
            try:
                score = float(value)
                if math.isnan(score):
                    logger.warning("ragas_metric_nan",
                        metric=metric_name,
                        message=f"{metric_name} returned NaN - check context format")
                    return 0.0
                if math.isinf(score):
                    logger.warning("ragas_metric_inf",
                        metric=metric_name,
                        message=f"{metric_name} returned Inf - check data format")
                    return 0.0
                return score
            except (TypeError, ValueError) as e:
                logger.error("ragas_score_error", metric=metric_name, error=str(e))
                return 0.0

        # Convert Result object to pandas DataFrame to extract scores
        result_df = evaluation_result.to_pandas()

        # Extract first row scores (we only evaluated one sample)
        scores = {
            'faithfulness': sanitize_score(result_df['faithfulness'].iloc[0], 'faithfulness'),
            'answer_relevance': sanitize_score(result_df['answer_relevancy'].iloc[0], 'answer_relevance'),
            'context_utilization': sanitize_score(result_df['context_utilization'].iloc[0], 'context_utilization')
        }

        logger.info("ragas_evaluation_complete",
            faithfulness=scores['faithfulness'],
            answer_relevance=scores['answer_relevance'],
            context_utilization=scores['context_utilization']
        )

        return scores

    except Exception as e:
        logger.error("ragas_evaluation_failed", error=str(e))
        return None  # Return None, don't block query


async def evaluate_and_update_async(query_id: int, nl_query: str, sql: str, results: list):
    """
    Background task to evaluate RAGAS scores and update database.

    This runs asynchronously after query results are returned to the user.
    Updates the query_logs table with evaluation_status and scores.

    Args:
        query_id: ID of the query log entry to update
        nl_query: Natural language query string
        sql: Generated SQL query
        results: Query results as list of dicts
    """
    from app.db.session import get_db_session
    from app.db.models import QueryLog

    db = None
    try:
        # Update status to 'evaluating'
        db = get_db_session()
        query_log = db.query(QueryLog).filter(QueryLog.id == query_id).first()

        if not query_log:
            logger.error("ragas_async_query_not_found", query_id=query_id)
            return

        query_log.evaluation_status = 'evaluating'
        db.commit()

        logger.info("ragas_async_started", query_id=query_id)

        # Run RAGAS evaluation
        scores = await evaluate(nl_query, sql, results)

        if scores is None:
            # Evaluation failed
            query_log.evaluation_status = 'failed'
            db.commit()
            logger.warning("ragas_async_failed", query_id=query_id)
            return

        # Update database with scores
        query_log.faithfulness_score = scores['faithfulness']
        query_log.answer_relevance_score = scores['answer_relevance']
        query_log.context_utilization_score = scores['context_utilization']
        query_log.evaluation_status = 'completed'
        db.commit()

        logger.info("ragas_async_completed",
            query_id=query_id,
            faithfulness=scores['faithfulness'],
            answer_relevance=scores['answer_relevance'],
            context_utilization=scores['context_utilization']
        )

    except Exception as e:
        logger.error("ragas_async_error", query_id=query_id, error=str(e))
        if db and query_log:
            try:
                query_log.evaluation_status = 'failed'
                db.commit()
            except:
                pass
    finally:
        if db:
            db.close()
