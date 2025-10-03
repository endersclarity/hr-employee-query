"""Tests for query_service.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.exc import OperationalError, TimeoutError as SQLAlchemyTimeoutError, DatabaseError

from app.services.query_service import execute_query
from app.api.models import QueryResponse


@pytest.mark.asyncio
class TestExecuteQuery:
    """Test cases for execute_query function."""

    @pytest.mark.asyncio
    async def test_successful_query_execution(self):
        """Test successful query execution with results."""
        mock_mappings = [
            {"id": 1, "name": "John Doe", "salary_usd": 85000},
            {"id": 2, "name": "Jane Smith", "salary_usd": 92000}
        ]

        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.ragas_service.evaluate', return_value={'faithfulness': 0.0, 'answer_relevance': 0.0, 'context_precision': 0.0}):

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.mappings.return_value = mock_mappings
            mock_db.execute.return_value = mock_result
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me all employees")

            assert response.success is True
            assert response.result_count == 2
            assert len(response.results) == 2
            assert response.results[0]["name"] == "John Doe"
            assert response.generated_sql == "SELECT * FROM employees"

    @pytest.mark.asyncio
    async def test_zero_results_query(self):
        """Test query that returns no results (AC5)."""
        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees WHERE 1=0"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.ragas_service.evaluate', return_value=None):

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.fetchall.return_value = []
            mock_db.execute.return_value = mock_result
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me employees named XYZ")

            assert response.success is True
            assert response.result_count == 0
            assert response.results == []

    @pytest.mark.asyncio
    async def test_large_result_set_truncation(self):
        """Test that result sets > 1000 rows are truncated (AC4)."""
        # Create 1500 mock rows
        mock_mappings = [
            {"id": i, "name": f"Employee {i}"}
            for i in range(1500)
        ]

        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.logger') as mock_logger, \
             patch('app.services.query_service.ragas_service.evaluate', return_value=None):

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.mappings.return_value = mock_mappings
            mock_db.execute.return_value = mock_result
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me all employees")

            assert response.success is True
            assert response.result_count == 1000
            assert len(response.results) == 1000
            mock_logger.warning.assert_called_once_with("result_set_truncated", count=1500)

    @pytest.mark.asyncio
    async def test_query_timeout_error(self):
        """Test query timeout handling (AC3)."""
        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT pg_sleep(5)"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session:

            mock_db = MagicMock()
            mock_db.execute.side_effect = SQLAlchemyTimeoutError("Query timeout")
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me all employees")

            assert response.success is False
            assert response.error_type == "DB_ERROR"
            assert "timed out" in response.error.lower()

    @pytest.mark.asyncio
    async def test_operational_error_handling(self):
        """Test database connection failure handling."""
        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session:

            mock_db = MagicMock()
            mock_db.execute.side_effect = OperationalError("connection failed", None, None)
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me all employees")

            assert response.success is False
            assert response.error_type == "DB_ERROR"
            assert "connection failed" in response.error.lower()

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """Test SQL validation error handling."""
        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="DROP TABLE employees"), \
             patch('app.services.query_service.validate_sql', side_effect=ValueError("Invalid SQL")):

            response = await execute_query("Delete all employees")

            assert response.success is False
            assert response.error_type == "VALIDATION_ERROR"
            assert "Invalid SQL" in response.error

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self):
        """Test that execution time is tracked correctly (AC2)."""
        mock_mappings = [{"id": 1, "name": "Test"}]

        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.ragas_service.evaluate', return_value=None):

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.mappings.return_value = mock_mappings
            mock_db.execute.return_value = mock_result
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me employees")

            assert response.execution_time_ms >= 0
            assert response.execution_time_ms < 5000  # Should complete in < 5s

    @pytest.mark.asyncio
    async def test_null_value_handling(self):
        """Test that NULL values are properly serialized (Task 3.3)."""
        mock_mappings = [
            {"id": 1, "name": "John", "manager_name": None}
        ]

        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.ragas_service.evaluate', return_value=None):

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.mappings.return_value = mock_mappings
            mock_db.execute.return_value = mock_result
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me employees")

            assert response.success is True
            assert response.results[0]["manager_name"] is None

    @pytest.mark.asyncio
    async def test_database_error_logging(self):
        """Test that database errors are properly logged (Task 4.2)."""
        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.logger') as mock_logger:

            mock_db = MagicMock()
            mock_db.execute.side_effect = DatabaseError("Database error", None, None)
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me employees")

            assert response.success is False
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_query_includes_ragas_scores(self):
        """Test that query response includes ragas_scores field (Story 2.2 AC1)."""
        mock_mappings = [{"id": 1, "name": "John"}]
        mock_ragas_scores = {
            'faithfulness': 0.85,
            'answer_relevance': 0.92,
            'context_precision': 0.78
        }

        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.ragas_service.evaluate', return_value=mock_ragas_scores):

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.mappings.return_value = mock_mappings
            mock_db.execute.return_value = mock_result
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me employees")

            assert response.success is True
            assert response.ragas_scores is not None
            assert response.ragas_scores == mock_ragas_scores
            assert response.ragas_scores['faithfulness'] == 0.85
            assert response.ragas_scores['answer_relevance'] == 0.92
            assert response.ragas_scores['context_precision'] == 0.78

    @pytest.mark.asyncio
    async def test_query_continues_when_ragas_fails(self):
        """Test that query doesn't break when Ragas evaluation fails (Story 2.2 AC2)."""
        mock_mappings = [{"id": 1, "name": "John"}]

        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.ragas_service.evaluate', return_value=None):

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.mappings.return_value = mock_mappings
            mock_db.execute.return_value = mock_result
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me employees")

            assert response.success is True
            assert response.ragas_scores is None
            assert response.results == [{"id": 1, "name": "John"}]

    @pytest.mark.asyncio
    async def test_query_performance_with_ragas(self):
        """Test that total response time remains < 5 seconds with Ragas (Story 2.2 AC3)."""
        mock_mappings = [{"id": 1, "name": "John"}]
        mock_ragas_scores = {
            'faithfulness': 0.85,
            'answer_relevance': 0.92,
            'context_precision': 0.78
        }

        with patch('app.services.query_service.sanitize_input', return_value="test query"), \
             patch('app.services.query_service.generate_sql', return_value="SELECT * FROM employees"), \
             patch('app.services.query_service.validate_sql'), \
             patch('app.services.query_service.get_db_session') as mock_get_session, \
             patch('app.services.query_service.ragas_service.evaluate', return_value=mock_ragas_scores):

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.mappings.return_value = mock_mappings
            mock_db.execute.return_value = mock_result
            mock_get_session.return_value = mock_db

            response = await execute_query("Show me employees")

            assert response.success is True
            assert response.execution_time_ms < 5000  # AC3: < 5 seconds
            assert response.ragas_scores is not None
