"""API route handlers for query and health endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
from datetime import datetime, timezone
from app.api.models import QueryRequest, QueryResponse, HealthResponse
from app.db.session import get_db_session, get_pool_status
from app.db.models import QueryLog
from app.services.query_service import execute_query
from app.services import report_service, ragas_service

router = APIRouter()


@router.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process natural language query and return structured results.

    Returns results immediately with evaluation_status='pending'.
    RAGAS evaluation runs in background task, updating query_log asynchronously.
    Use GET /api/query/{query_log_id} to poll for updated scores.

    Multi-layered security validation:
    1. Input sanitization (remove comments, semicolons)
    2. LLM SQL generation
    3. SQL validation (sqlparse, whitelist SELECT)
    4. Database execution with timeout (3s)
    """
    try:
        # Apply 3s timeout for query processing (RAGAS runs separately in background)
        async with asyncio.timeout(3):
            # Execute query through query service
            response = await execute_query(request.query)

            # Queue RAGAS evaluation as background task if query succeeded
            if response.success and response.query_log_id:
                background_tasks.add_task(
                    ragas_service.evaluate_and_update_async,
                    response.query_log_id,
                    response.query,
                    response.generated_sql,
                    response.results
                )

            return response

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=500,
            detail="Request timeout"
        )


@router.get("/api/reports/analysis")
async def get_analysis():
    """
    Generate comparative analysis report with weak query identification and recommendations.

    Returns:
        Dictionary with:
        - total_queries: Total number of queries logged
        - average_scores: Average Ragas scores across all queries
        - weak_queries: Queries with scores < 0.7
        - recommendations: Actionable improvement suggestions
    """
    try:
        report = report_service.get_analysis_report()
        return report
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analysis report: {str(e)}"
        )


@router.get("/api/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint that verifies API and database connectivity.

    Returns:
        HealthResponse with status, database connection state, pool status, and timestamp.
        Returns 200 if healthy, 503 if unhealthy.
    """
    try:
        # Test database connection
        from sqlalchemy import text
        db = get_db_session()
        db.execute(text("SELECT 1"))
        db.close()

        pool_status = get_pool_status()

        return HealthResponse(
            status="healthy",
            database="connected",
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            pool_status=pool_status
        )

    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            database="disconnected",
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            error=str(e)
        )


@router.get("/api/query/{query_log_id}")
async def get_query_status(query_log_id: int):
    """
    Get RAGAS evaluation status and scores for a query.

    Frontend polls this endpoint to check if background RAGAS evaluation completed.

    Returns:
        - evaluation_status: 'pending', 'evaluating', 'completed', 'failed'
        - ragas_scores: Dict with scores (only if status='completed')
    """
    try:
        db = get_db_session()
        try:
            query_log = db.query(QueryLog).filter(QueryLog.id == query_log_id).first()

            if not query_log:
                raise HTTPException(status_code=404, detail="Query log not found")

            response = {
                "query_log_id": query_log.id,
                "evaluation_status": query_log.evaluation_status,
                "ragas_scores": None
            }

            if query_log.evaluation_status == 'completed':
                response["ragas_scores"] = {
                    "faithfulness": float(query_log.faithfulness_score) if query_log.faithfulness_score else 0.0,
                    "answer_relevance": float(query_log.answer_relevance_score) if query_log.answer_relevance_score else 0.0,
                    "context_utilization": float(query_log.context_precision_score) if query_log.context_precision_score else 0.0
                }

            return response

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve query status: {str(e)}"
        )
