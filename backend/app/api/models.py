"""Pydantic models for API request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class QueryRequest(BaseModel):
    """Request model for natural language query endpoint."""

    query: str = Field(
        ...,
        max_length=500,
        description="Natural language query"
    )


class QueryResponse(BaseModel):
    """Response model for query endpoint."""

    success: bool
    query: str
    generated_sql: str | None = None
    results: List[Dict[str, Any]] = []
    result_count: int = 0
    execution_time_ms: int = 0
    error: str | None = None
    error_type: str | None = None  # 'VALIDATION_ERROR', 'LLM_ERROR', 'DB_ERROR'
    ragas_scores: Dict[str, float] | None = None  # Ragas evaluation scores


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str  # 'healthy' or 'unhealthy'
    database: str  # 'connected' or 'disconnected'
    timestamp: str
    pool_status: Dict[str, Any] | None = None
    error: str | None = None
