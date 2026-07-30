from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings


# PostgreSQL connection pool. ``pool_pre_ping`` replaces dead connections
# before a request uses them, while ``pool_recycle`` avoids stale connections
# in long-running API processes.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """Provide one database session per request and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
