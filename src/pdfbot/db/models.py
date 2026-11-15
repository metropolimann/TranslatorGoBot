# src/pdfbot/db/models.py
import uuid
from datetime import date, time
from typing import Optional
from sqlalchemy import String, Date, Time, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from pdfbot.db.base import Base

class TaskRecordModel(Base):
    """The SQLAlchemy ORM model for the task history."""
    __tablename__ = "tasks"

    # Primary key (client-generated UUID)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # Task details
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    done_by: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Date and Time
    date: Mapped[date] = mapped_column(Date, nullable=False)
    time: Mapped[time] = mapped_column(Time, nullable=False)
    
    # Sync flag for PostgreSQL
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metadata (optional JSON)
    # Note: 'metadata' is a reserved word in SQLAlchemy, so we name the Python 
    # attribute 'meta_data' but map it to a column named 'metadata'.
    meta_data: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)