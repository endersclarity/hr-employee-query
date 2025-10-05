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
        # Check if ragas is available
        if not RAGAS_AVAILABLE:
            logger.debug("ragas_evaluation_skipped", message="Ragas not available")
            return None

        # Format results as natural language text for RAGAS to parse
        # RAGAS faithfulness needs human-readable statements, not Python dict strings
        # Limit to first 5 results to avoid token limits
        if not results:
            formatted_results = "No results returned from the database."
        else:
            # Convert results to natural language statements
            result_statements = []
            for i, row in enumerate(results[:5], 1):
                # Format each row as a descriptive statement
                row_parts = [f"{key}: {value}" for key, value in row.items()]
                statement = f"Record {i}: " + ", ".join(row_parts)
                result_statements.append(statement)
            formatted_results = " ".join(result_statements)

        # Create Ragas dataset format
        # For NL→SQL evaluation:
        # - question: the natural language query
        # - answer: formatted results (what user sees)
        # - contexts: the DATABASE SCHEMA (not SQL!) for faithfulness validation
        # - ground_truth: not required for these metrics
        dataset_dict = {
            'question': [nl_query],
            'answer': [formatted_results],
            'contexts': [[EMPLOYEE_SCHEMA]]  # Schema for faithfulness validation
        }

        dataset = Dataset.from_dict(dataset_dict)

        # Evaluate using Ragas metrics
        # Ragas evaluate() is synchronous but conflicts with uvloop in FastAPI
        # Run in thread pool to avoid "Can't patch loop of type <class 'uvloop.Loop'>" error
        # Using context_utilization instead of context_precision (which requires ground_truth)
        loop = asyncio.get_event_loop()
        evaluation_result = await loop.run_in_executor(
            None,  # Use default ThreadPoolExecutor
            lambda: ragas_evaluate(
                dataset=dataset,
                metrics=[faithfulness, answer_relevancy, context_utilization]
            )
        )

        # Extract scores from evaluation result
        # Ragas returns a Result object with metrics as attributes
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

        scores = {
            'faithfulness': sanitize_score(evaluation_result.get('faithfulness', 0.0), 'faithfulness'),
            'answer_relevance': sanitize_score(evaluation_result.get('answer_relevancy', 0.0), 'answer_relevance'),
            'context_utilization': sanitize_score(evaluation_result.get('context_utilization', 0.0), 'context_utilization')
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
