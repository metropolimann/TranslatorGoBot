# src/pdfbot/db/session.py
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from pdfbot.config import settings
from pdfbot.db.base import Base
from pdfbot.core.exceptions import DBError
from pdfbot.logging_setup import logger

# 1. Create the engine
# connect_args={"check_same_thread": False} is required for SQLite 
# when used with multi-threaded apps (like our future GUI).
engine = create_engine(
    settings.sqlite_url, 
    connect_args={"check_same_thread": False}
)

# 2. Create a session factory
# expire_on_commit=False prevents the DetachedInstanceError when we 
# try to read data from objects after the session is closed.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    expire_on_commit=False
)

def init_db() -> None:
    """Create all tables in the SQLite database."""
    try:
        # This looks at all classes inheriting from Base (like TaskRecordModel)
        # and creates the tables if they don't exist.
        Base.metadata.create_all(bind=engine)
        logger.debug("Database tables initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise DBError(f"Could not initialize database: {e}") from e

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager that yields a database session.
    Automatically commits on success, rolls back on error, and closes.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise DBError(f"Database operation failed: {e}") from e
    finally:
        session.close()