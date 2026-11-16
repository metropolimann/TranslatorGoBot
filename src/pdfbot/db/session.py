# src/pdfbot/db/session.py
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from pdfbot.config import settings
from pdfbot.db.base import Base
from pdfbot.core.exceptions import DBError
from pdfbot.logging_setup import logger

# 1. SQLite Engine (Local)
engine = create_engine(
    settings.sqlite_url, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

# 2. PostgreSQL Engine (Remote Mirror)
pg_engine = None
SessionLocalPG = None

if settings.postgres_dsn:
    try:
        pg_engine = create_engine(settings.postgres_dsn)
        SessionLocalPG = sessionmaker(
            autocommit=False, autoflush=False, bind=pg_engine, expire_on_commit=False
        )
        logger.debug("PostgreSQL engine configured.")
    except Exception as e:
        logger.error(f"Failed to configure PostgreSQL: {e}")

def init_db() -> None:
    """Create all tables in both SQLite and PostgreSQL."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.debug("SQLite tables initialized.")
        
        if pg_engine:
            Base.metadata.create_all(bind=pg_engine)
            logger.debug("PostgreSQL tables initialized.")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise DBError(f"Could not initialize database: {e}") from e

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """SQLite session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise DBError(f"SQLite operation failed: {e}") from e
    finally:
        session.close()

@contextmanager
def get_pg_session() -> Generator[Session, None, None]:
    """PostgreSQL session."""
    if not SessionLocalPG:
        raise DBError("PostgreSQL is not configured.")
    session = SessionLocalPG()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise DBError(f"PostgreSQL operation failed: {e}") from e
    finally:
        session.close()