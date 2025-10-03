"""API route handlers for query and health endpoints."""

from fastapi import APIRouter, HTTPException
import asyncio
from datetime import datetime, timezone
from app.api.models import QueryRequest, QueryResponse, HealthResponse
from app.db.session import get_db_session, get_pool_status
from app.services.query_service import execute_query
from app.services import report_service

router = APIRouter()


@router.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Process natural language query and return structured results.

    Multi-layered security validation:
    1. Input sanitization (remove comments, semicolons)
    2. LLM SQL generation
    3. SQL validation (sqlparse, whitelist SELECT)
    4. Database execution with timeout (3s)
    """
    try:
        # Apply 10s timeout for all query processing
        async with asyncio.timeout(10):
            # Execute query through query service
            response = await execute_query(request.query)
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
