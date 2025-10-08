from datetime import datetime
from pydantic import BaseModel, HttpUrl
from uuid import UUID


class ThumbnailResponse(BaseModel):
    id: UUID
    job_id: UUID
    storage_url: HttpUrl
    keywords: list[str]
    created_at: datetime

    class Config:
        from_attributes = True