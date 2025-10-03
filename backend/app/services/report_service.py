"""Report service for query analysis and recommendations."""

from typing import List, Dict
from sqlalchemy import func
import structlog

from app.db.session import get_db_session
from app.db.models import QueryLog

logger = structlog.get_logger()


def get_analysis_report() -> Dict:
    """
    Generate comparative analysis report with weak query identification and recommendations.

    Returns:
        Dictionary with total_queries, average_scores, weak_queries, and recommendations
    """
    try:
        db = get_db_session()
        try:
            # Get all query logs
            logs = db.query(QueryLog).order_by(QueryLog.created_at.desc()).all()

            if not logs:
                return {
                    "total_queries": 0,
                    "average_scores": {
                        "faithfulness": 0.0,
                        "answer_relevance": 0.0,
                        "context_precision": 0.0
                    },
                    "weak_queries": [],
                    "recommendations": ["No queries executed yet. Run some queries to generate recommendations."]
                }

            # Calculate average scores (excluding None values)
            faithfulness_scores = [log.faithfulness_score for log in logs if log.faithfulness_score is not None]
            answer_relevance_scores = [log.answer_relevance_score for log in logs if log.answer_relevance_score is not None]
            context_precision_scores = [log.context_precision_score for log in logs if log.context_precision_score is not None]

            avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0.0
            avg_answer_relevance = sum(answer_relevance_scores) / len(answer_relevance_scores) if answer_relevance_scores else 0.0
            avg_context_precision = sum(context_precision_scores) / len(context_precision_scores) if context_precision_scores else 0.0

            # Identify weak queries (any score < 0.7)
            weak_queries = []
            for log in logs:
                scores = {
                    "faithfulness": float(log.faithfulness_score) if log.faithfulness_score else None,
                    "answer_relevance": float(log.answer_relevance_score) if log.answer_relevance_score else None,
                    "context_precision": float(log.context_precision_score) if log.context_precision_score else None
                }

                # Check if any score is below 0.7
                has_weak_score = any(
                    score is not None and score < 0.7
                    for score in scores.values()
                )

                if has_weak_score:
                    weak_queries.append({
                        "query": log.natural_language_query,
                        "scores": scores,
                        "sql": log.generated_sql,
                        "created_at": log.created_at.isoformat() if log.created_at else None,
                        "reason": _identify_weakness_reason(scores)
                    })

            # Generate actionable recommendations based on weak queries
            recommendations = _generate_recommendations(weak_queries, logs)

            logger.info("analysis_report_generated",
                total_queries=len(logs),
                weak_queries_count=len(weak_queries),
                avg_faithfulness=avg_faithfulness
            )

            return {
                "total_queries": len(logs),
                "average_scores": {
                    "faithfulness": float(round(avg_faithfulness, 2)),
                    "answer_relevance": float(round(avg_answer_relevance, 2)),
                    "context_precision": float(round(avg_context_precision, 2))
                },
                "weak_queries": weak_queries[:10],  # Limit to top 10 for readability
                "recommendations": recommendations
            }

        finally:
            db.close()

    except Exception as e:
        logger.error("analysis_report_failed", error=str(e))
        raise


def _identify_weakness_reason(scores: Dict[str, float | None]) -> str:
    """
    Identify primary reason for weak scores.

    Args:
        scores: Dictionary with faithfulness, answer_relevance, context_precision

    Returns:
        Human-readable reason string
    """
    weak_metrics = []

    if scores.get("faithfulness") and scores["faithfulness"] < 0.7:
        weak_metrics.append("faithfulness")
    if scores.get("answer_relevance") and scores["answer_relevance"] < 0.7:
        weak_metrics.append("answer_relevance")
    if scores.get("context_precision") and scores["context_precision"] < 0.7:
        weak_metrics.append("context_precision")

    if not weak_metrics:
        return "Multiple metrics below threshold"

    if "faithfulness" in weak_metrics:
        return "Low faithfulness - SQL may not accurately reflect schema or query intent"
    elif "answer_relevance" in weak_metrics:
        return "Low answer relevance - results may not align with user's actual question"
    elif "context_precision" in weak_metrics:
        return "Low context precision - SQL may select unnecessary fields or lack focus"

    return "Multiple quality concerns"


def _generate_recommendations(weak_queries: List[Dict], all_logs: List[QueryLog]) -> List[str]:
    """
    Generate actionable recommendations based on query patterns.

    Args:
        weak_queries: List of queries with scores < 0.7
        all_logs: All query logs for pattern analysis

    Returns:
        List of recommendation strings
    """
    recommendations = []

    if not weak_queries:
        recommendations.append("✅ All queries performing well (scores ≥ 0.7). Continue monitoring.")
        return recommendations

    # Analyze common patterns in weak queries
    weak_query_texts = [q["query"].lower() for q in weak_queries]

    # Check for salary-related queries
    if any("salary" in text or "pay" in text or "compensation" in text for text in weak_query_texts):
        recommendations.append(
            "Add few-shot examples for salary comparisons in LLM prompt (e.g., 'high earner' → salary_usd > 80000)"
        )

    # Check for ambiguous queries
    if any(len(text.split()) < 5 for text in weak_query_texts):
        recommendations.append(
            "Provide user guidance for more specific queries (e.g., 'show employees' → 'show all active employees in engineering')"
        )

    # Check for faithfulness issues (low faithfulness scores)
    low_faithfulness_count = sum(
        1 for q in weak_queries
        if q["scores"].get("faithfulness") and q["scores"]["faithfulness"] < 0.7
    )
    if low_faithfulness_count > len(weak_queries) * 0.5:
        recommendations.append(
            "Include database schema details in prompt context to improve SQL faithfulness"
        )

    # Check for context precision issues
    low_precision_count = sum(
        1 for q in weak_queries
        if q["scores"].get("context_precision") and q["scores"]["context_precision"] < 0.7
    )
    if low_precision_count > len(weak_queries) * 0.5:
        recommendations.append(
            "Refine LLM prompt to encourage selecting only necessary columns (avoid SELECT *)"
        )

    # Check for answer relevance issues
    low_relevance_count = sum(
        1 for q in weak_queries
        if q["scores"].get("answer_relevance") and q["scores"]["answer_relevance"] < 0.7
    )
    if low_relevance_count > len(weak_queries) * 0.5:
        recommendations.append(
            "Add semantic validation step to ensure SQL intent matches natural language query"
        )

    # Generic recommendation if weak queries > 30% of total
    if len(weak_queries) > len(all_logs) * 0.3:
        recommendations.append(
            "Consider A/B testing alternative LLM prompts to improve overall query quality"
        )

    return recommendations if recommendations else [
        "Review weak queries manually to identify improvement opportunities"
    ]
