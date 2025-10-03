"""Integration tests for /api/reports/analysis endpoint"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime

from app.main import app
from app.db.models import QueryLog


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestAnalysisEndpoint:
    """Integration tests for GET /api/reports/analysis"""

    def test_analysis_endpoint_returns_200(self, client):
        """Test that analysis endpoint returns 200 OK"""
        # Arrange
        mock_logs = []
        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            response = client.get("/api/reports/analysis")

            # Assert
            assert response.status_code == 200

    def test_analysis_endpoint_response_structure(self, client):
        """Test response structure matches specification"""
        # Arrange
        mock_logs = [
            self._create_mock_log(1, "query 1", 0.9, 0.85, 0.8),
            self._create_mock_log(2, "query 2", 0.65, 0.7, 0.75)  # weak query
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            response = client.get("/api/reports/analysis")

            # Assert
            data = response.json()
            assert "total_queries" in data
            assert "average_scores" in data
            assert "weak_queries" in data
            assert "recommendations" in data

            # Verify average_scores structure
            assert "faithfulness" in data["average_scores"]
            assert "answer_relevance" in data["average_scores"]
            assert "context_precision" in data["average_scores"]

    def test_analysis_endpoint_identifies_weak_queries(self, client):
        """Test that weak queries (scores < 0.7) are identified"""
        # Arrange
        mock_logs = [
            self._create_mock_log(1, "strong query", 0.9, 0.85, 0.88),
            self._create_mock_log(2, "weak query 1", 0.65, 0.8, 0.75),
            self._create_mock_log(3, "weak query 2", 0.8, 0.6, 0.85)
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            response = client.get("/api/reports/analysis")

            # Assert
            data = response.json()
            assert data["total_queries"] == 3
            assert len(data["weak_queries"]) == 2
            assert data["weak_queries"][0]["query"] == "weak query 1"
            assert data["weak_queries"][1]["query"] == "weak query 2"

    def test_analysis_endpoint_includes_recommendations(self, client):
        """Test that recommendations are included"""
        # Arrange
        mock_logs = [
            self._create_mock_log(1, "show high salary employees", 0.6, 0.65, 0.7)
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            response = client.get("/api/reports/analysis")

            # Assert
            data = response.json()
            assert len(data["recommendations"]) > 0
            assert isinstance(data["recommendations"], list)
            assert all(isinstance(rec, str) for rec in data["recommendations"])

    def test_analysis_endpoint_handles_empty_logs(self, client):
        """Test endpoint with no query logs"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = []
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            response = client.get("/api/reports/analysis")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["total_queries"] == 0
            assert len(data["weak_queries"]) == 0

    def test_analysis_endpoint_error_handling(self, client):
        """Test error handling when database fails"""
        # Arrange
        mock_db = Mock()
        mock_db.query.side_effect = Exception("Database error")

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            response = client.get("/api/reports/analysis")

            # Assert
            assert response.status_code == 500
            # Response should contain error information (format may vary)
            assert response.json() is not None

    def test_weak_query_contains_scores_and_reason(self, client):
        """Test that weak queries include scores and reason"""
        # Arrange
        mock_logs = [
            self._create_mock_log(1, "problematic query", 0.6, 0.75, 0.8)
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            response = client.get("/api/reports/analysis")

            # Assert
            data = response.json()
            weak_query = data["weak_queries"][0]
            assert "scores" in weak_query
            assert "reason" in weak_query
            assert "query" in weak_query
            assert weak_query["scores"]["faithfulness"] == 0.6

    # Helper methods
    def _create_mock_log(self, id, query, faithfulness, answer_relevance, context_precision):
        """Create mock QueryLog object"""
        mock_log = Mock(spec=QueryLog)
        mock_log.id = id
        mock_log.natural_language_query = query
        mock_log.generated_sql = f"SELECT * FROM employees WHERE id = {id}"
        mock_log.faithfulness_score = Decimal(str(faithfulness))
        mock_log.answer_relevance_score = Decimal(str(answer_relevance))
        mock_log.context_precision_score = Decimal(str(context_precision))
        mock_log.result_count = 5
        mock_log.execution_time_ms = 1000
        mock_log.created_at = datetime(2025, 10, 2, 12, 0, 0)
        return mock_log
