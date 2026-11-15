# src/pdfbot/logging_setup.py
import logging
import sys
from loguru import logger

from pdfbot.config import settings


class InterceptHandler(logging.Handler):
    """
    Redirect standard logging (used by SQLAlchemy, Playwright, etc.) 
    into Loguru so everything goes to the same place.
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure loguru to log to stderr and a rotating file."""
    
    # 1. Remove the default loguru handler
    logger.remove()

    # 2. Add console handler (stderr)
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # 3. Add rotating file handler
    log_file = settings.log_dir / "pdfbot.log"
    logger.add(
        log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=settings.log_rotate_bytes,
        retention=settings.log_backup_count,
        encoding="utf-8",
        enqueue=True,  # Thread-safe for QThreads
    )

    # 4. Intercept standard logging (SQLAlchemy, Alembic, Playwright)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)