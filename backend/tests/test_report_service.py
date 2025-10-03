"""Tests for report_service.py"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from app.services import report_service
from app.db.models import QueryLog


class TestGetAnalysisReport:
    """Tests for get_analysis_report function"""

    def test_empty_query_logs(self):
        """Test report generation with no query logs"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = []
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            result = report_service.get_analysis_report()

            # Assert
            assert result["total_queries"] == 0
            assert result["average_scores"]["faithfulness"] == 0.0
            assert result["weak_queries"] == []
            assert len(result["recommendations"]) > 0
            assert "No queries executed yet" in result["recommendations"][0]

    def test_all_strong_queries(self):
        """Test report with all queries scoring above 0.7"""
        # Arrange
        mock_logs = [
            self._create_mock_log(1, "query 1", 0.9, 0.85, 0.8),
            self._create_mock_log(2, "query 2", 0.95, 0.9, 0.88),
            self._create_mock_log(3, "query 3", 0.87, 0.82, 0.79)
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            result = report_service.get_analysis_report()

            # Assert
            assert result["total_queries"] == 3
            assert result["average_scores"]["faithfulness"] == 0.91
            assert result["average_scores"]["answer_relevance"] == 0.86
            assert result["average_scores"]["context_precision"] == 0.82
            assert len(result["weak_queries"]) == 0
            assert "All queries performing well" in result["recommendations"][0]

    def test_identifies_weak_queries(self):
        """Test identification of queries with scores < 0.7"""
        # Arrange
        mock_logs = [
            self._create_mock_log(1, "show high earners", 0.65, 0.7, 0.8),  # weak faithfulness
            self._create_mock_log(2, "list employees", 0.9, 0.6, 0.75),     # weak answer_relevance
            self._create_mock_log(3, "salary info", 0.8, 0.85, 0.5),        # weak context_precision
            self._create_mock_log(4, "good query", 0.9, 0.85, 0.88)         # all strong
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            result = report_service.get_analysis_report()

            # Assert
            assert result["total_queries"] == 4
            assert len(result["weak_queries"]) == 3
            assert result["weak_queries"][0]["query"] == "show high earners"
            assert result["weak_queries"][1]["query"] == "list employees"
            assert result["weak_queries"][2]["query"] == "salary info"

    def test_salary_query_recommendation(self):
        """Test recommendations for salary-related weak queries"""
        # Arrange
        mock_logs = [
            self._create_mock_log(1, "show me high salary employees", 0.6, 0.65, 0.7),
            self._create_mock_log(2, "who gets paid the most", 0.65, 0.6, 0.68)
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            result = report_service.get_analysis_report()

            # Assert
            assert any("few-shot examples for salary" in rec.lower() for rec in result["recommendations"])

    def test_handles_none_scores(self):
        """Test handling of None values in Ragas scores"""
        # Arrange
        mock_logs = [
            self._create_mock_log(1, "query 1", None, None, None),
            self._create_mock_log(2, "query 2", 0.8, 0.75, None)
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            result = report_service.get_analysis_report()

            # Assert - should not crash, should calculate averages from available scores
            assert result["total_queries"] == 2
            assert result["average_scores"]["faithfulness"] == 0.8  # only one score available
            assert result["average_scores"]["answer_relevance"] == 0.75

    def test_limits_weak_queries_to_10(self):
        """Test that weak_queries list is limited to 10 items"""
        # Arrange
        mock_logs = [
            self._create_mock_log(i, f"weak query {i}", 0.6, 0.65, 0.68)
            for i in range(15)
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            result = report_service.get_analysis_report()

            # Assert
            assert len(result["weak_queries"]) == 10  # Limited to 10

    def test_db_error_raises_exception(self):
        """Test that database errors are propagated"""
        # Arrange
        mock_db = Mock()
        mock_db.query.side_effect = Exception("Database connection failed")

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act & Assert
            with pytest.raises(Exception, match="Database connection failed"):
                report_service.get_analysis_report()

    def test_faithfulness_recommendation(self):
        """Test faithfulness-specific recommendations"""
        # Arrange - majority of weak queries have low faithfulness
        mock_logs = [
            self._create_mock_log(1, "query 1", 0.6, 0.8, 0.8),
            self._create_mock_log(2, "query 2", 0.65, 0.85, 0.82),
            self._create_mock_log(3, "query 3", 0.68, 0.9, 0.88)
        ]

        mock_db = Mock()
        mock_query = Mock()
        mock_query.order_by().all.return_value = mock_logs
        mock_db.query.return_value = mock_query

        with patch('app.services.report_service.get_db_session', return_value=mock_db):
            # Act
            result = report_service.get_analysis_report()

            # Assert
            assert any("schema details" in rec.lower() for rec in result["recommendations"])

    # Helper methods
    def _create_mock_log(self, id, query, faithfulness, answer_relevance, context_precision):
        """Create mock QueryLog object"""
        mock_log = Mock(spec=QueryLog)
        mock_log.id = id
        mock_log.natural_language_query = query
        mock_log.generated_sql = f"SELECT * FROM employees WHERE {id}"
        mock_log.faithfulness_score = Decimal(str(faithfulness)) if faithfulness else None
        mock_log.answer_relevance_score = Decimal(str(answer_relevance)) if answer_relevance else None
        mock_log.context_precision_score = Decimal(str(context_precision)) if context_precision else None
        mock_log.result_count = 10
        mock_log.execution_time_ms = 500
        mock_log.created_at = datetime(2025, 10, 2, 12, 0, 0)
        return mock_log


class TestIdentifyWeaknessReason:
    """Tests for _identify_weakness_reason helper"""

    def test_low_faithfulness_reason(self):
        """Test reason identification for low faithfulness"""
        # Arrange
        scores = {"faithfulness": 0.6, "answer_relevance": 0.8, "context_precision": 0.85}

        # Act
        reason = report_service._identify_weakness_reason(scores)

        # Assert
        assert "faithfulness" in reason.lower()

    def test_low_answer_relevance_reason(self):
        """Test reason identification for low answer relevance"""
        # Arrange
        scores = {"faithfulness": 0.9, "answer_relevance": 0.65, "context_precision": 0.85}

        # Act
        reason = report_service._identify_weakness_reason(scores)

        # Assert
        assert "answer relevance" in reason.lower()

    def test_low_context_precision_reason(self):
        """Test reason identification for low context precision"""
        # Arrange
        scores = {"faithfulness": 0.85, "answer_relevance": 0.8, "context_precision": 0.6}

        # Act
        reason = report_service._identify_weakness_reason(scores)

        # Assert
        assert "context precision" in reason.lower()
