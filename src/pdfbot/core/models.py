# src/pdfbot/core/models.py
from datetime import date, time
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

from pdfbot.core.constants import TaskType, LanguageCode


class SplitRequest(BaseModel):
    """Input data for the PDF splitter."""
    pdf_path: Path
    n1: int = Field(gt=0, description="Starting page (1-indexed)")
    n2: int = Field(gt=0, description="Ending page (inclusive)")
    m: int = Field(gt=0, description="Number of pages per pack")
    identifier: str = Field(min_length=1, description="Project or task ID")

    @field_validator("n2")
    @classmethod
    def validate_page_range(cls, v: int, info) -> int:
        n1 = info.data.get("n1")
        if n1 is not None and v < n1:
            raise ValueError(f"n2 ({v}) cannot be less than n1 ({n1})")
        return v


class SplitResult(BaseModel):
    """Output data returned after a successful split."""
    identifier: str
    output_dir: Path
    created_files: list[Path]
    total_packs: int


class TranslateRequest(BaseModel):
    """Input data for the translator."""
    pack_path: Path
    src_lang: LanguageCode
    tgt_lang: LanguageCode
    identifier: str = Field(min_length=1)


class TranslateResult(BaseModel):
    """Output data returned after a successful translation."""
    identifier: str
    output_pdf: Path
    src_lang: LanguageCode
    tgt_lang: LanguageCode
    characters_translated: int


class TaskRecord(BaseModel):
    """The unified schema for SQLite and PostgreSQL history."""
    id: UUID = Field(default_factory=uuid4)
    task_type: TaskType
    done_by: str
    date: date
    time: time
    
    # SQLite-specific offline queue flag (ignored by PostgreSQL)
    is_synced: bool = False
    
    # Optional JSON metadata (e.g., file paths, page ranges)
    metadata: Optional[dict] = None