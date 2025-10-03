"""Tests for query logging functionality in query_service.py"""

import pytest
from unittest.mock import Mock, patch, call
from decimal import Decimal

from app.services.query_service import _log_query
from app.db.models import QueryLog


class TestLogQuery:
    """Tests for _log_query function"""

    def test_logs_query_with_ragas_scores(self):
        """Test successful query logging with Ragas scores"""
        # Arrange
        nl_query = "show all employees"
        sql = "SELECT * FROM employees"
        results = [{"employee_id": 1, "name": "John"}]
        ragas_scores = {
            "faithfulness": 0.9,
            "answer_relevance": 0.85,
            "context_precision": 0.88
        }
        elapsed_ms = 1500

        mock_db = Mock()
        mock_log = Mock(spec=QueryLog)
        mock_log.id = 123

        with patch('app.services.query_service.get_db_session', return_value=mock_db):
            # Act
            _log_query(nl_query, sql, results, ragas_scores, elapsed_ms)

            # Assert
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()

            # Verify QueryLog was created with correct data
            added_log = mock_db.add.call_args[0][0]
            assert added_log.natural_language_query == nl_query
            assert added_log.generated_sql == sql
            assert added_log.faithfulness_score == 0.9
            assert added_log.answer_relevance_score == 0.85
            assert added_log.context_precision_score == 0.88
            assert added_log.result_count == 1
            assert added_log.execution_time_ms == 1500

    def test_logs_query_with_none_ragas_scores(self):
        """Test logging when Ragas evaluation returns None"""
        # Arrange
        nl_query = "show employees"
        sql = "SELECT * FROM employees"
        results = [{"id": 1}]
        ragas_scores = None
        elapsed_ms = 1200

        mock_db = Mock()

        with patch('app.services.query_service.get_db_session', return_value=mock_db):
            # Act
            _log_query(nl_query, sql, results, ragas_scores, elapsed_ms)

            # Assert
            added_log = mock_db.add.call_args[0][0]
            assert added_log.natural_language_query == nl_query
            assert added_log.faithfulness_score is None
            assert added_log.answer_relevance_score is None
            assert added_log.context_precision_score is None

    def test_handles_empty_results(self):
        """Test logging with empty result set"""
        # Arrange
        nl_query = "show deleted employees"
        sql = "SELECT * FROM employees WHERE status = 'deleted'"
        results = []
        ragas_scores = {"faithfulness": 0.8, "answer_relevance": 0.7, "context_precision": 0.75}
        elapsed_ms = 800

        mock_db = Mock()

        with patch('app.services.query_service.get_db_session', return_value=mock_db):
            # Act
            _log_query(nl_query, sql, results, ragas_scores, elapsed_ms)

            # Assert
            added_log = mock_db.add.call_args[0][0]
            assert added_log.result_count == 0

    def test_graceful_failure_on_db_error(self):
        """Test that logging failure doesn't raise exception"""
        # Arrange
        nl_query = "test query"
        sql = "SELECT 1"
        results = []
        ragas_scores = None
        elapsed_ms = 100

        mock_db = Mock()
        mock_db.commit.side_effect = Exception("Database commit failed")

        with patch('app.services.query_service.get_db_session', return_value=mock_db):
            # Act - should not raise
            _log_query(nl_query, sql, results, ragas_scores, elapsed_ms)

            # Assert - db.close() should still be called
            mock_db.close.assert_called_once()

    def test_closes_db_session_on_exception(self):
        """Test that database session is closed even if exception occurs"""
        # Arrange
        mock_db = Mock()
        mock_db.add.side_effect = Exception("Add failed")

        with patch('app.services.query_service.get_db_session', return_value=mock_db):
            # Act
            _log_query("query", "sql", [], None, 100)

            # Assert
            mock_db.close.assert_called_once()


class TestQueryLogModel:
    """Tests for QueryLog ORM model"""

    def test_querylog_repr(self):
        """Test QueryLog __repr__ method"""
        from datetime import datetime

        # Arrange
        log = QueryLog()
        log.id = 42
        log.natural_language_query = "This is a very long query that should be truncated in the repr method because it exceeds fifty characters"
        log.created_at = datetime(2025, 10, 2, 14, 30, 0)

        # Act
        repr_str = repr(log)

        # Assert
        assert "42" in repr_str
        assert "This is a very long query that should be truncated" in repr_str
        assert "2025-10-02 14:30:00" in repr_str
