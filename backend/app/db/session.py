import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import structlog

logger = structlog.get_logger()

# Lazy initialization of engine and session
_engine = None
_SessionLocal = None


def _get_engine():
    """Get or create the database engine with connection pooling."""
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        _engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,          # Minimum connections
            max_overflow=15,      # Maximum additional connections
            pool_timeout=30,      # Timeout waiting for connection
            pool_recycle=3600,    # Recycle connections after 1 hour
            pool_pre_ping=True    # Test connections before use
        )
    return _engine


def _get_session_local():
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _SessionLocal


def get_db_session():
    """Get database session. Caller is responsible for closing."""
    SessionLocal = _get_session_local()
    return SessionLocal()


def get_pool_status():
    """Get connection pool health metrics."""
    engine = _get_engine()
    return {
        "pool_size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "total": engine.pool.size() + engine.pool.overflow()
    }


def get_engine():
    """
    Get the database engine.

    Returns:
        Engine: SQLAlchemy engine object
    """
    return _get_engine()
