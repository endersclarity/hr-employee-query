"""Tests for LLM service."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from app.services.llm_service import generate_sql, validate_api_key


class TestValidateAPIKey:
    """Test API key validation."""

    @pytest.mark.asyncio
    async def test_validate_api_key_success(self):
        """Test successful API key validation."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            # Should not raise
            await validate_api_key()

            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_api_key_failure(self):
        """Test API key validation failure raises exception."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("Invalid API key")
            )
            mock_get_client.return_value = mock_client

            with pytest.raises(Exception, match="Invalid API key"):
                await validate_api_key()


class TestGenerateSQL:
    """Test SQL generation from natural language."""

    @pytest.mark.asyncio
    async def test_generate_sql_success(self):
        """Test successful SQL generation."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees WHERE department = 'Engineering'"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("Show me Engineering employees")

            assert sql == "SELECT * FROM employees WHERE department = 'Engineering'"
            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_sql_mandatory_query_1(self):
        """Test: 'Show me employees hired in the last 6 months'"""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("Show me employees hired in the last 6 months")

            assert "hire_date" in sql
            assert "INTERVAL" in sql or "months" in sql.lower()

    @pytest.mark.asyncio
    async def test_generate_sql_mandatory_query_2(self):
        """Test: 'List Engineering employees with salary > 120K'"""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees WHERE department = 'Engineering' AND salary_usd > 120000"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("List Engineering employees with salary greater than 120K")

            assert "Engineering" in sql
            assert "salary" in sql.lower()
            assert "120000" in sql or "120" in sql

    @pytest.mark.asyncio
    async def test_generate_sql_mandatory_query_3(self):
        """Test: 'Who is on parental leave?'"""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees WHERE leave_type = 'Parental Leave'"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("Who is on parental leave?")

            assert "leave_type" in sql
            assert "Parental Leave" in sql

    @pytest.mark.asyncio
    async def test_generate_sql_mandatory_query_4(self):
        """Test: 'Show employees managed by John Doe'"""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees WHERE manager_name = 'John Doe'"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            sql = await generate_sql("Show employees managed by John Doe")

            assert "manager_name" in sql
            assert "John Doe" in sql

    @pytest.mark.asyncio
    async def test_generate_sql_timeout(self):
        """Test LLM request timeout triggers retry."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )
            mock_get_client.return_value = mock_client

            with pytest.raises(Exception, match="timed out after 3 attempts"):
                await generate_sql("test query")

            # Should retry 3 times
            assert mock_client.chat.completions.create.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_sql_retry_on_rate_limit(self):
        """Test retry logic activates on rate limit error."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees"

            # First 2 calls fail with rate limit, 3rd succeeds
            mock_client.chat.completions.create = AsyncMock(
                side_effect=[
                    Exception("rate_limit_exceeded"),
                    Exception("rate_limit_exceeded"),
                    mock_response
                ]
            )
            mock_get_client.return_value = mock_client

            sql = await generate_sql("test query")

            assert sql == "SELECT * FROM employees"
            assert mock_client.chat.completions.create.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_sql_invalid_request(self):
        """Test INVALID_REQUEST response triggers error."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "INVALID_REQUEST"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            with pytest.raises(ValueError, match="cannot be fulfilled with SELECT statement"):
                await generate_sql("Delete all employees")

    @pytest.mark.asyncio
    async def test_generate_sql_uses_default_temperature(self):
        """Test LLM uses default temperature (gpt-5-nano only supports default)."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await generate_sql("test query")

            call_args = mock_client.chat.completions.create.call_args
            # gpt-5-nano doesn't support temperature parameter
            assert 'temperature' not in call_args[1]

    @pytest.mark.asyncio
    async def test_generate_sql_uses_gpt5_nano(self):
        """Test LLM uses gpt-5-nano model as specified in Story 1.4."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await generate_sql("test query")

            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == 'gpt-5-nano'

    @pytest.mark.asyncio
    async def test_generate_sql_max_completion_tokens(self):
        """Test LLM is called with max_completion_tokens=200 for gpt-5-nano."""
        with patch('app.services.llm_service.get_client') as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM employees"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await generate_sql("test query")

            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['max_completion_tokens'] == 200
