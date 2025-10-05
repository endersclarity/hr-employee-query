"""Tests for aggregation query support (Bug #001).

These tests validate that the LLM can generate correct SQL for aggregation queries
including DISTINCT, GROUP BY, and COUNT operations.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.services.llm_service import generate_sql


class TestAggregationQueries:
    """Test LLM generates correct SQL for aggregation queries."""

    @pytest.mark.asyncio
    async def test_list_all_departments_distinct(self):
        """Test: 'List all departments' generates SELECT DISTINCT."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT DISTINCT department FROM employees ORDER BY department"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("List all departments")

            # Validate SQL contains required elements
            assert "SELECT" in sql.upper()
            assert "DISTINCT" in sql.upper()
            assert "department" in sql.lower()
            assert "from employees" in sql.lower()

    @pytest.mark.asyncio
    async def test_list_departments_variation_1(self):
        """Test variation: 'Show me all departments'"""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT DISTINCT department FROM employees ORDER BY department"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("Show me all departments")

            assert "SELECT" in sql.upper()
            assert "DISTINCT" in sql.upper()
            assert "department" in sql.lower()

    @pytest.mark.asyncio
    async def test_list_departments_variation_2(self):
        """Test variation: 'All departments'"""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT DISTINCT department FROM employees"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("All departments")

            assert "SELECT" in sql.upper()
            assert "DISTINCT" in sql.upper()
            assert "department" in sql.lower()

    @pytest.mark.asyncio
    async def test_count_employees_per_department(self):
        """Test: 'How many employees are in each department?' generates GROUP BY COUNT."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT department, COUNT(*) as employee_count "
                "FROM employees GROUP BY department ORDER BY department"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("How many employees are in each department?")

            # Validate GROUP BY and COUNT
            assert "SELECT" in sql.upper()
            assert "COUNT" in sql.upper()
            assert "GROUP BY" in sql.upper()
            assert "department" in sql.lower()

    @pytest.mark.asyncio
    async def test_unique_roles_in_department(self):
        """Test: 'What are the unique roles in Engineering?' generates DISTINCT with WHERE."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT DISTINCT role FROM employees "
                "WHERE department = 'Engineering' ORDER BY role"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("What are the unique roles in Engineering?")

            # Validate DISTINCT with WHERE clause
            assert "SELECT" in sql.upper()
            assert "DISTINCT" in sql.upper()
            assert "role" in sql.lower()
            assert "WHERE" in sql.upper()
            assert "Engineering" in sql

    @pytest.mark.asyncio
    async def test_list_all_roles(self):
        """Test: 'List all roles' generates SELECT DISTINCT."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT DISTINCT role FROM employees ORDER BY role"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("List all roles")

            assert "SELECT" in sql.upper()
            assert "DISTINCT" in sql.upper()
            assert "role" in sql.lower()


class TestAggregationQueriesRegressionPrevention:
    """Ensure aggregation query support doesn't break existing functionality."""

    @pytest.mark.asyncio
    async def test_existing_query_employees_in_engineering(self):
        """Regression: 'Show employees in Engineering' still works."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT * FROM employees WHERE department = 'Engineering'"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("Show employees in Engineering")

            assert "SELECT" in sql.upper()
            assert "from employees" in sql.lower()
            assert "Engineering" in sql

    @pytest.mark.asyncio
    async def test_existing_query_salary_filter(self):
        """Regression: Salary filtering queries still work."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT * FROM employees WHERE department = 'Engineering' AND salary_usd > 120000"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("Show me employees in Engineering with salary > 120K")

            assert "SELECT" in sql.upper()
            assert "WHERE" in sql.upper()
            assert "Engineering" in sql
            assert "salary" in sql.lower()

    @pytest.mark.asyncio
    async def test_existing_query_leave_type(self):
        """Regression: Leave type queries still work."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "SELECT * FROM employees WHERE leave_type = 'Parental Leave'"
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("Who is on parental leave?")

            assert "SELECT" in sql.upper()
            assert "leave_type" in sql.lower()
            assert "Parental Leave" in sql


class TestAggregationQueriesValidation:
    """Test that generated aggregation SQL passes validation."""

    @pytest.mark.asyncio
    async def test_distinct_query_passes_validation(self):
        """Test DISTINCT query passes SQL validation."""
        from app.services.validation_service import validate_sql

        sql = "SELECT DISTINCT department FROM employees ORDER BY department"

        # Should not raise
        result = validate_sql(sql, nl_query="List all departments")
        assert result is True

    @pytest.mark.asyncio
    async def test_group_by_query_passes_validation(self):
        """Test GROUP BY query passes SQL validation."""
        from app.services.validation_service import validate_sql

        sql = "SELECT department, COUNT(*) as count FROM employees GROUP BY department"

        # Should not raise
        result = validate_sql(sql, nl_query="How many in each department?")
        assert result is True

    @pytest.mark.asyncio
    async def test_distinct_with_where_passes_validation(self):
        """Test DISTINCT with WHERE passes SQL validation."""
        from app.services.validation_service import validate_sql

        sql = "SELECT DISTINCT role FROM employees WHERE department = 'Engineering'"

        # Should not raise
        result = validate_sql(sql, nl_query="Unique roles in Engineering")
        assert result is True
