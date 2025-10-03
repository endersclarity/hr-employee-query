"""Tests for FastAPI endpoints and middleware."""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def setup_llm_mock(mock_get_client, sql="SELECT * FROM employees"):
    """Helper to set up LLM mock with valid SQL response."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = sql

    async def async_create(*args, **kwargs):
        return mock_response
    mock_client.chat.completions.create = async_create
    mock_get_client.return_value = mock_client


class TestQueryEndpoint:
    """Tests for POST /api/query endpoint."""

    @patch('app.services.query_service.get_db_session')
    @patch('app.services.llm_service.get_client')
    def test_query_endpoint_success(self, mock_get_client, mock_get_db_session):
        """Test successful query with valid input."""
        setup_llm_mock(mock_get_client, "SELECT * FROM employees WHERE department = 'Engineering'")

        # Mock database session
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            MagicMock(_mapping={"id": 1, "name": "John", "department": "Engineering"})
        ]
        mock_db.execute.return_value = mock_result
        mock_get_db_session.return_value = mock_db

        response = client.post(
            "/api/query",
            json={"query": "Show me all employees in Engineering"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["query"] == "Show me all employees in Engineering"
        assert data["generated_sql"] is not None
        assert isinstance(data["results"], list)
        assert isinstance(data["result_count"], int)
        assert isinstance(data["execution_time_ms"], int)

    @patch('app.services.query_service.get_db_session')
    @patch('app.services.llm_service.get_client')
    def test_query_endpoint_request_id_header(self, mock_get_client, mock_get_db_session):
        """Test that X-Request-ID header is present."""
        setup_llm_mock(mock_get_client)

        # Mock database session
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        mock_get_db_session.return_value = mock_db

        response = client.post(
            "/api/query",
            json={"query": "test query"}
        )

        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36  # UUID v4 length

    def test_query_endpoint_empty_query(self):
        """Test validation error for empty query."""
        response = client.post(
            "/api/query",
            json={"query": ""}
        )

        assert response.status_code == 422  # Validation error

    def test_query_endpoint_query_too_long(self):
        """Test validation error for query exceeding max length."""
        long_query = "a" * 501  # Exceeds 500 char limit
        response = client.post(
            "/api/query",
            json={"query": long_query}
        )

        assert response.status_code == 422  # Validation error

    def test_query_endpoint_missing_query_field(self):
        """Test validation error when query field is missing."""
        response = client.post(
            "/api/query",
            json={}
        )

        assert response.status_code == 422  # Validation error

    def test_query_endpoint_invalid_json(self):
        """Test error handling for invalid JSON."""
        response = client.post(
            "/api/query",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422


class TestHealthEndpoint:
    """Tests for GET /api/health endpoint."""

    @patch('app.api.routes.get_pool_status')
    @patch('app.api.routes.get_db_session')
    def test_health_endpoint_database_connected(self, mock_get_db_session, mock_get_pool_status):
        """Test health check when database is connected."""
        mock_session = MagicMock()
        mock_get_db_session.return_value = mock_session
        mock_get_pool_status.return_value = {
            "pool_size": 5,
            "checked_in": 4,
            "checked_out": 1,
            "overflow": 0,
            "total": 5
        }

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "timestamp" in data
        assert data["timestamp"].endswith("Z")
        assert "pool_status" in data

        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('app.api.routes.get_db_session')
    def test_health_endpoint_database_disconnected(self, mock_get_db_session):
        """Test health check when database connection fails."""
        mock_get_db_session.side_effect = Exception("Connection failed")

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"
        assert "timestamp" in data

    @patch('app.api.routes.get_db_session')
    def test_health_endpoint_request_id_header(self, mock_get_db_session):
        """Test that X-Request-ID header is present in health checks."""
        mock_session = MagicMock()
        mock_get_db_session.return_value = mock_session

        response = client.get("/api/health")

        assert "X-Request-ID" in response.headers


class TestCORSMiddleware:
    """Tests for CORS middleware configuration."""

    def test_cors_headers_present(self):
        """Test that CORS headers are included in responses."""
        response = client.options(
            "/api/query",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )

        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    @patch('app.services.query_service.get_db_session')
    @patch('app.services.llm_service.get_client')
    def test_cors_allows_configured_origin(self, mock_get_client, mock_get_db_session):
        """Test that configured origins are allowed."""
        setup_llm_mock(mock_get_client)

        # Mock database session
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        mock_get_db_session.return_value = mock_db

        response = client.post(
            "/api/query",
            json={"query": "test"},
            headers={"Origin": "http://localhost:5173"}
        )

        assert response.status_code == 200


class TestErrorHandling:
    """Tests for global error handlers."""

    def test_validation_error_format(self):
        """Test that validation errors return proper structure."""
        # Validation errors are handled by FastAPI's default handler
        response = client.post(
            "/api/query",
            json={"query": ""}
        )

        assert response.status_code == 422

    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["docs"] == "/docs"
        assert data["health"] == "/api/health"


class TestRequestIDMiddleware:
    """Tests for Request ID middleware."""

    def test_unique_request_ids(self):
        """Test that each request gets a unique request ID."""
        response1 = client.get("/")
        response2 = client.get("/")

        request_id1 = response1.headers.get("X-Request-ID")
        request_id2 = response2.headers.get("X-Request-ID")

        assert request_id1 != request_id2

    def test_request_id_format(self):
        """Test that request ID is a valid UUID."""
        import uuid

        response = client.get("/")
        request_id = response.headers.get("X-Request-ID")

        # Should not raise ValueError
        uuid.UUID(request_id)


class TestResponseModels:
    """Tests for Pydantic response model compliance."""

    @patch('app.services.query_service.get_db_session')
    @patch('app.services.llm_service.get_client')
    def test_query_response_schema(self, mock_get_client, mock_get_db_session):
        """Test that query response matches expected schema."""
        setup_llm_mock(mock_get_client)

        # Mock database session
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        mock_get_db_session.return_value = mock_db

        response = client.post(
            "/api/query",
            json={"query": "test"}
        )

        data = response.json()

        required_fields = [
            "success", "query", "generated_sql", "results",
            "result_count", "execution_time_ms", "error", "error_type"
        ]

        for field in required_fields:
            assert field in data

    @patch('app.api.routes.get_db_session')
    def test_health_response_schema(self, mock_get_db_session):
        """Test that health response matches expected schema."""
        mock_session = MagicMock()
        mock_get_db_session.return_value = mock_session

        response = client.get("/api/health")

        data = response.json()

        required_fields = ["status", "database", "timestamp"]

        for field in required_fields:
            assert field in data


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @patch('app.services.query_service.get_db_session')
    @patch('app.services.llm_service.get_client')
    def test_query_with_special_characters(self, mock_get_client, mock_get_db_session):
        """Test query with special characters."""
        setup_llm_mock(mock_get_client, "SELECT * FROM employees WHERE salary_usd > 50000 AND department = 'R&D'")

        # Mock database session
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        mock_get_db_session.return_value = mock_db

        response = client.post(
            "/api/query",
            json={"query": "Find employees with salary > $50k & dept = 'R&D'"}
        )

        assert response.status_code == 200

    @patch('app.services.query_service.get_db_session')
    @patch('app.services.llm_service.get_client')
    def test_query_with_unicode(self, mock_get_client, mock_get_db_session):
        """Test query with Unicode characters."""
        setup_llm_mock(mock_get_client, "SELECT * FROM employees WHERE employee_name IN ('José', 'François')")

        # Mock database session
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        mock_get_db_session.return_value = mock_db

        response = client.post(
            "/api/query",
            json={"query": "Employees named José or François"}
        )

        assert response.status_code == 200

    @patch('app.services.query_service.get_db_session')
    @patch('app.services.llm_service.get_client')
    def test_query_max_length(self, mock_get_client, mock_get_db_session):
        """Test query at exactly max length (500 chars)."""
        setup_llm_mock(mock_get_client)

        # Mock database session
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        mock_get_db_session.return_value = mock_db

        query = "a" * 500
        response = client.post(
            "/api/query",
            json={"query": query}
        )

        assert response.status_code == 200
