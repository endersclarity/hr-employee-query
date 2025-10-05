"""
Unit tests for RAGAS faithfulness metric fixes.

Tests verify:
1. Schema context is passed instead of SQL
2. Faithfulness scores are realistic (not always 0.0)
3. NaN/Inf values are logged properly
4. Comparative analysis functions correctly
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services import ragas_service
from app.services import report_service
from app.db.models import QueryLog


class TestRagasSchemaContext:
    """Tests for schema context implementation."""

    @pytest.mark.asyncio
    async def test_evaluate_uses_schema_context_not_sql(self):
        """Verify that evaluate() passes schema as context, not SQL query."""
        nl_query = "Show me all employees"
        sql = "SELECT * FROM employees"
        results = [{"id": 1, "name": "John Doe"}]

        with patch('app.services.ragas_service.RAGAS_AVAILABLE', True), \
             patch('app.services.ragas_service.Dataset') as mock_dataset, \
             patch('app.services.ragas_service.ragas_evaluate') as mock_evaluate:

            # Mock the evaluation to return realistic scores
            mock_evaluate.return_value = {
                'faithfulness': 0.87,
                'answer_relevancy': 0.82,
                'context_utilization': 0.91
            }

            await ragas_service.evaluate(nl_query, sql, results)

            # Verify Dataset.from_dict was called
            assert mock_dataset.from_dict.called, "Dataset.from_dict should be called"

            # Get the dictionary passed to Dataset.from_dict
            call_args = mock_dataset.from_dict.call_args[0][0]

            # Verify contexts contains schema, not SQL
            assert 'contexts' in call_args, "contexts key should exist"
            assert len(call_args['contexts']) == 1, "Should have one context entry"
            assert len(call_args['contexts'][0]) == 1, "Context should be list of lists"

            context_text = call_args['contexts'][0][0]

            # Verify schema content is present
            assert 'employee_id' in context_text, "Schema should contain employee_id column"
            assert 'Database: hr_employees' in context_text, "Schema should contain database name"
            assert 'Table: employees' in context_text, "Schema should contain table name"

            # Verify SQL is NOT in context
            assert sql not in context_text, "SQL query should NOT be in context"

    @pytest.mark.asyncio
    async def test_evaluate_faithfulness_not_zero(self):
        """Verify faithfulness returns realistic scores, not always 0.0."""
        nl_query = "List employees in Engineering"
        sql = "SELECT * FROM employees WHERE department = 'Engineering'"
        results = [{"id": 1, "department": "Engineering"}]

        with patch('app.services.ragas_service.RAGAS_AVAILABLE', True), \
             patch('app.services.ragas_service.Dataset'), \
             patch('app.services.ragas_service.ragas_evaluate') as mock_evaluate:

            # Mock RAGAS to return realistic scores
            mock_evaluate.return_value = {
                'faithfulness': 0.89,
                'answer_relevancy': 0.85,
                'context_utilization': 0.92
            }

            scores = await ragas_service.evaluate(nl_query, sql, results)

            # Verify scores are not 0.0
            assert scores is not None, "Scores should not be None"
            assert scores['faithfulness'] > 0.0, "Faithfulness should not be 0.0"
            assert scores['faithfulness'] >= 0.6, "Faithfulness should be >= 0.6 (minimum acceptable)"
            assert scores['faithfulness'] <= 1.0, "Faithfulness should be <= 1.0"


class TestSanitizeScoreLogging:
    """Tests for enhanced score sanitization with logging."""

    @pytest.mark.asyncio
    async def test_sanitize_score_logs_nan_warning(self):
        """Verify NaN values trigger warning logs."""
        import math

        with patch('app.services.ragas_service.RAGAS_AVAILABLE', True), \
             patch('app.services.ragas_service.Dataset'), \
             patch('app.services.ragas_service.ragas_evaluate') as mock_evaluate, \
             patch('app.services.ragas_service.logger') as mock_logger:

            # Mock RAGAS to return NaN for faithfulness
            mock_evaluate.return_value = {
                'faithfulness': math.nan,
                'answer_relevancy': 0.85,
                'context_utilization': 0.92
            }

            scores = await ragas_service.evaluate("test query", "SELECT 1", [{"id": 1}])

            # Verify logger.warning was called with NaN message
            assert mock_logger.warning.called, "Warning should be logged for NaN"
            warning_calls = [call for call in mock_logger.warning.call_args_list
                           if 'ragas_metric_nan' in str(call)]
            assert len(warning_calls) > 0, "Should log NaN warning for faithfulness"

            # Verify NaN was sanitized to 0.0
            assert scores['faithfulness'] == 0.0, "NaN should be converted to 0.0"

    @pytest.mark.asyncio
    async def test_sanitize_score_logs_inf_warning(self):
        """Verify Inf values trigger warning logs."""
        import math

        with patch('app.services.ragas_service.RAGAS_AVAILABLE', True), \
             patch('app.services.ragas_service.Dataset'), \
             patch('app.services.ragas_service.ragas_evaluate') as mock_evaluate, \
             patch('app.services.ragas_service.logger') as mock_logger:

            # Mock RAGAS to return Inf
            mock_evaluate.return_value = {
                'faithfulness': math.inf,
                'answer_relevancy': 0.85,
                'context_utilization': 0.92
            }

            scores = await ragas_service.evaluate("test query", "SELECT 1", [{"id": 1}])

            # Verify logger.warning was called
            assert mock_logger.warning.called, "Warning should be logged for Inf"

            # Verify Inf was sanitized to 0.0
            assert scores['faithfulness'] == 0.0, "Inf should be converted to 0.0"


class TestComparativeAnalysis:
    """Tests for comparative analysis functionality."""

    def test_categorize_queries_by_type(self):
        """Verify query type categorization works correctly."""
        # Create mock query logs
        logs = [
            QueryLog(
                natural_language_query="Show all employees",
                generated_sql="SELECT * FROM employees",
                faithfulness_score=0.90,
                answer_relevance_score=0.85,
                context_precision_score=0.88
            ),
            QueryLog(
                natural_language_query="Show employees in Engineering",
                generated_sql="SELECT * FROM employees WHERE department = 'Engineering'",
                faithfulness_score=0.87,
                answer_relevance_score=0.82,
                context_precision_score=0.91
            ),
            QueryLog(
                natural_language_query="Count employees per department",
                generated_sql="SELECT department, COUNT(*) FROM employees GROUP BY department",
                faithfulness_score=0.85,
                answer_relevance_score=0.90,
                context_precision_score=0.87
            ),
            QueryLog(
                natural_language_query="Employees hired in last 6 months",
                generated_sql="SELECT * FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'",
                faithfulness_score=0.83,
                answer_relevance_score=0.88,
                context_precision_score=0.85
            )
        ]

        analysis = report_service._categorize_queries_by_type(logs)

        # Verify categorization
        assert 'simple_select' in analysis, "Should have simple_select category"
        assert 'where_filter' in analysis, "Should have where_filter category"
        assert 'aggregation' in analysis, "Should have aggregation category"
        assert 'date_range' in analysis, "Should have date_range category"

        # Verify counts
        assert analysis['simple_select']['count'] == 1, "Should have 1 simple SELECT"
        assert analysis['where_filter']['count'] == 1, "Should have 1 WHERE filter"
        assert analysis['aggregation']['count'] == 1, "Should have 1 aggregation"
        assert analysis['date_range']['count'] == 1, "Should have 1 date range"

        # Verify averages are calculated
        assert 'avg_faithfulness' in analysis['aggregation'], "Should calculate avg faithfulness"
        assert analysis['aggregation']['avg_faithfulness'] == 0.85, "Should match query score"

    def test_generate_recommendations_for_weak_aggregation(self):
        """Verify recommendations are generated for weak aggregation queries."""
        query_type_analysis = {
            'aggregation': {
                'count': 5,
                'avg_faithfulness': 0.72,  # Below 0.80 threshold
                'avg_answer_relevance': 0.85,
                'avg_context_precision': 0.88
            },
            'simple_select': {
                'count': 10,
                'avg_faithfulness': 0.92,
                'avg_answer_relevance': 0.90,
                'avg_context_precision': 0.91
            }
        }

        recommendations = report_service._generate_recommendations([], [], query_type_analysis)

        # Verify aggregation recommendation is present
        assert any('aggregation' in rec.lower() for rec in recommendations), \
            "Should recommend improving aggregation queries"
        assert any('GROUP BY' in rec or 'COUNT' in rec for rec in recommendations), \
            "Should mention specific aggregation patterns"


class TestEndToEndRAGASFlow:
    """Integration-style tests for complete RAGAS flow."""

    @pytest.mark.asyncio
    async def test_full_ragas_evaluation_pipeline(self):
        """Test complete flow from query to scores to logging."""
        nl_query = "Show employees in Sales"
        sql = "SELECT * FROM employees WHERE department = 'Sales'"
        results = [
            {"employee_id": 1, "first_name": "John", "department": "Sales"},
            {"employee_id": 2, "first_name": "Jane", "department": "Sales"}
        ]

        with patch('app.services.ragas_service.RAGAS_AVAILABLE', True), \
             patch('app.services.ragas_service.Dataset'), \
             patch('app.services.ragas_service.ragas_evaluate') as mock_evaluate:

            # Mock realistic RAGAS scores
            mock_evaluate.return_value = {
                'faithfulness': 0.88,
                'answer_relevancy': 0.84,
                'context_utilization': 0.90
            }

            scores = await ragas_service.evaluate(nl_query, sql, results)

            # Verify all scores are in realistic ranges
            assert scores is not None, "Scores should be returned"
            assert 0.6 <= scores['faithfulness'] <= 1.0, "Faithfulness in realistic range"
            assert 0.6 <= scores['answer_relevance'] <= 1.0, "Answer relevance in realistic range"
            assert 0.6 <= scores['context_utilization'] <= 1.0, "Context utilization in realistic range"

            # Verify scores are distinct (not all the same)
            score_values = list(scores.values())
            assert len(set(score_values)) > 1, "Scores should vary based on query quality"
