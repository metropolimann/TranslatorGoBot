# src/pdfbot/services/sync.py
from sqlalchemy import select

from pdfbot.config import settings
from pdfbot.db.models import TaskRecordModel
from pdfbot.db.session import get_db_session, get_pg_session
from pdfbot.logging_setup import logger


def sync_task(task_id: str) -> bool:
    """Syncs a single task from SQLite to PostgreSQL."""
    try:
        with get_db_session() as sqlite_db:
            # 1. Fetch from SQLite
            stmt = select(TaskRecordModel).where(TaskRecordModel.id == task_id)
            task = sqlite_db.scalars(stmt).first()
            if not task:
                return True

            # 2. Push to PostgreSQL
            with get_pg_session() as pg_db:
                # Check if it already exists in PG (to prevent duplicates)
                pg_task = pg_db.get(TaskRecordModel, task.id)
                if not pg_task:
                    pg_task = TaskRecordModel(
                        id=task.id,
                        task_type=task.task_type,
                        done_by=task.done_by,
                        date=task.date,
                        time=task.time,
                        meta_data=task.meta_data,
                        is_synced=True # Always true in PG
                    )
                    pg_db.add(pg_task)
            
            # 3. Mark as synced in SQLite
            task.is_synced = True
            
        logger.info(f"Synced task {task_id} to PostgreSQL.")
        return True
    except Exception as e:
        logger.warning(f"Failed to sync task {task_id}: {e}")
        return False

def sync_all_unsynced():
    """Finds all unsynced tasks in SQLite and pushes them to PG."""
    if not settings.postgres_dsn:
        return  # PostgreSQL not configured, skip
        
    with get_db_session() as db:
        stmt = select(TaskRecordModel).where(TaskRecordModel.is_synced == False)
        unsynced_tasks = db.scalars(stmt).all()
        
        if not unsynced_tasks:
            return
            
        logger.info(f"Found {len(unsynced_tasks)} tasks to sync to PostgreSQL.")
        
    for task in unsynced_tasks:
        sync_task(str(task.id))