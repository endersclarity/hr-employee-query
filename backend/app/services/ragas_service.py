import os
import asyncio
import math
import structlog
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

logger = structlog.get_logger()

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

        # Format results as answer string (what user receives)
        # Limit to first 5 results to avoid token limits
        formatted_results = str(results[:5]) if results else "No results returned"

        # Create Ragas dataset format
        # For NL→SQL evaluation:
        # - question: the natural language query
        # - answer: formatted results (what user sees)
        # - contexts: the SQL query that generated these results
        # - ground_truth: not required for these metrics
        dataset_dict = {
            'question': [nl_query],
            'answer': [formatted_results],
            'contexts': [[sql]]  # contexts must be list of lists
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
        def sanitize_score(value):
            """Convert NaN/Inf to 0.0, ensure valid float."""
            try:
                score = float(value)
                if math.isnan(score) or math.isinf(score):
                    return 0.0
                return score
            except (TypeError, ValueError):
                return 0.0

        scores = {
            'faithfulness': sanitize_score(evaluation_result.get('faithfulness', 0.0)),
            'answer_relevance': sanitize_score(evaluation_result.get('answer_relevancy', 0.0)),
            'context_utilization': sanitize_score(evaluation_result.get('context_utilization', 0.0))
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
