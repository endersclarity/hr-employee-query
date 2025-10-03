"""
Unit tests for database session with connection pooling.
Tests the connection pooling functionality in app.db.session module.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import os


@pytest.fixture
def mock_database_url():
    """Set DATABASE_URL for tests"""
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test_db'
    yield
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']


@pytest.fixture(autouse=True)
def reset_engine():
    """Reset the engine singleton between tests"""
    import app.db.session as session_module
    session_module._engine = None
    session_module._SessionLocal = None
    yield
    session_module._engine = None
    session_module._SessionLocal = None


def test_get_db_session_success(mock_database_url):
    """Test successful session creation with connection pool"""
    from app.db.session import get_db_session

    with patch('app.db.session.create_engine') as mock_create_engine, \
         patch('app.db.session.sessionmaker') as mock_sessionmaker:

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_session_factory = MagicMock()
        mock_session = MagicMock()
        mock_session_factory.return_value = mock_session
        mock_sessionmaker.return_value = mock_session_factory

        result = get_db_session()

        # Verify engine created with pooling
        mock_create_engine.assert_called_once()
        call_kwargs = mock_create_engine.call_args[1]
        assert call_kwargs['pool_size'] == 5
        assert call_kwargs['max_overflow'] == 15
        assert call_kwargs['pool_timeout'] == 30
        assert call_kwargs['pool_recycle'] == 3600
        assert call_kwargs['pool_pre_ping'] is True

        # Verify session created
        assert mock_sessionmaker.called
        assert result == mock_session


def test_get_db_session_reuses_engine(mock_database_url):
    """Test that engine is created only once (singleton pattern)"""
    from app.db.session import get_db_session

    with patch('app.db.session.create_engine') as mock_create_engine, \
         patch('app.db.session.sessionmaker') as mock_sessionmaker:

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_session_factory = MagicMock()
        mock_sessionmaker.return_value = mock_session_factory

        # Call twice
        get_db_session()
        get_db_session()

        # Engine should only be created once
        assert mock_create_engine.call_count == 1


def test_get_db_session_missing_database_url():
    """Test error when DATABASE_URL is not set"""
    from app.db.session import get_db_session

    # Ensure DATABASE_URL is not set
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']

    with pytest.raises(ValueError, match="DATABASE_URL environment variable is not set"):
        get_db_session()


def test_get_engine_returns_engine(mock_database_url):
    """Test get_engine returns the pooled engine"""
    from app.db.session import get_engine

    with patch('app.db.session.create_engine') as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        result = get_engine()

        assert result == mock_engine
        mock_create_engine.assert_called_once()


def test_get_pool_status(mock_database_url):
    """Test get_pool_status returns pool metrics"""
    from app.db.session import get_pool_status

    with patch('app.db.session.create_engine') as mock_create_engine:
        mock_engine = MagicMock()
        mock_pool = MagicMock()
        mock_pool.size.return_value = 5
        mock_pool.checkedin.return_value = 3
        mock_pool.checkedout.return_value = 2
        mock_pool.overflow.return_value = 1
        mock_engine.pool = mock_pool
        mock_create_engine.return_value = mock_engine

        status = get_pool_status()

        assert status['pool_size'] == 5
        assert status['checked_in'] == 3
        assert status['checked_out'] == 2
        assert status['overflow'] == 1
        assert status['total'] == 6  # size + overflow


def test_connection_pool_configuration(mock_database_url):
    """Test that connection pool is configured correctly per Story 1.7"""
    from app.db.session import get_engine

    with patch('app.db.session.create_engine') as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        get_engine()

        call_kwargs = mock_create_engine.call_args[1]

        # Verify AC6 requirements
        assert call_kwargs['pool_size'] == 5, "Base pool size should be 5"
        assert call_kwargs['max_overflow'] == 15, "Max overflow should be 15"
        assert call_kwargs['pool_timeout'] == 30, "Pool timeout should be 30s"
        assert call_kwargs['pool_recycle'] == 3600, "Pool recycle should be 1 hour"
        assert call_kwargs['pool_pre_ping'] is True, "Pre-ping should be enabled"
