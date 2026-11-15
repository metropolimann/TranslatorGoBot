# src/pdfbot/services/history.py
from datetime import datetime
from getpass import getuser
from typing import Optional
from sqlalchemy import select

from pdfbot.config import settings
from pdfbot.core.constants import TaskType
from pdfbot.core.exceptions import DBError
from pdfbot.db.models import TaskRecordModel
from pdfbot.db.session import get_db_session
from pdfbot.logging_setup import logger


class HistoryService:
    """Service to log tasks to the SQLite database."""

    @staticmethod
    def log_task(task_type: TaskType, meta_data: Optional[dict] = None, done_by: Optional[str] = None) -> None:
        """
        Record a completed task in the database.
        Defaults to the OS username or OPERATOR_NAME from .env.
        """
        # 1. Figure out who ran it
        if not done_by:
            done_by = settings.operator_name or getuser()

        # 2. Get current date and time
        now = datetime.now()

        # 3. Save to database
        try:
            with get_db_session() as db:
                task = TaskRecordModel(
                    task_type=task_type.value,
                    done_by=done_by,
                    date=now.date(),
                    time=now.time(),
                    is_synced=False,
                    meta_data=meta_data
                )
                db.add(task)
            logger.debug(f"Logged task: {task_type.value} by {done_by}")
            
        except DBError as e:
            # We don't want a failed history log to crash the main app
            logger.error(f"Failed to log task to history: {e}")

    @staticmethod
    def list_tasks(limit: int = 20) -> list[TaskRecordModel]:
        """Fetch the most recent tasks for the CLI or GUI."""
        try:
            with get_db_session() as db:
                # SQLAlchemy 2.0 syntax to select the newest tasks first
                stmt = (
                    select(TaskRecordModel)
                    .order_by(TaskRecordModel.date.desc(), TaskRecordModel.time.desc())
                    .limit(limit)
                )
                return list(db.scalars(stmt).all())
        except DBError as e:
            logger.error(f"Failed to fetch tasks: {e}")
            return []