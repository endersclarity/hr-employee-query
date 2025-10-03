"""Tests for health endpoint with pool status."""

import pytest
from unittest.mock import patch, MagicMock
from app.api.routes import health


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test cases for /api/health endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint_success(self):
        """Test health endpoint returns pool status when healthy (AC6)."""
        mock_pool_status = {
            "pool_size": 5,
            "checked_in": 4,
            "checked_out": 1,
            "overflow": 0,
            "total": 5
        }

        with patch('app.api.routes.get_db_session') as mock_get_session, \
             patch('app.api.routes.get_pool_status', return_value=mock_pool_status):

            mock_db = MagicMock()
            mock_db.execute.return_value = None
            mock_get_session.return_value = mock_db

            response = await health()

            assert response.status == "healthy"
            assert response.database == "connected"
            assert response.pool_status is not None
            assert response.pool_status["pool_size"] == 5
            assert response.pool_status["total"] == 5

    @pytest.mark.asyncio
    async def test_health_endpoint_database_failure(self):
        """Test health endpoint when database connection fails."""
        with patch('app.api.routes.get_db_session') as mock_get_session:
            mock_db = MagicMock()
            mock_db.execute.side_effect = Exception("Connection failed")
            mock_get_session.return_value = mock_db

            response = await health()

            assert response.status == "unhealthy"
            assert response.database == "disconnected"
            assert response.error is not None

    @pytest.mark.asyncio
    async def test_pool_status_metrics(self):
        """Test that pool status includes all required metrics."""
        mock_pool_status = {
            "pool_size": 5,
            "checked_in": 3,
            "checked_out": 2,
            "overflow": 1,
            "total": 6
        }

        with patch('app.api.routes.get_db_session') as mock_get_session, \
             patch('app.api.routes.get_pool_status', return_value=mock_pool_status):

            mock_db = MagicMock()
            mock_db.execute.return_value = None
            mock_get_session.return_value = mock_db

            response = await health()

            pool_status = response.pool_status
            assert "pool_size" in pool_status
            assert "checked_in" in pool_status
            assert "checked_out" in pool_status
            assert "overflow" in pool_status
            assert "total" in pool_status
