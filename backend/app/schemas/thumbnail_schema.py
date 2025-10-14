from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ThumbnailResponse(BaseModel):
    id: UUID
    job_id: UUID
    storage_url: Optional[str]
    keywords: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedThumbnailResponse(BaseModel):
    items: list[ThumbnailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int