from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class DocumentStatus(StrEnum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    created_at: datetime


class DocumentDetail(DocumentResponse):
    page_count: int | None = None
    chunk_count: int | None = None
    error: str | None = None
