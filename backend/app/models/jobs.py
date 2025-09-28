from __future__ import annotations

import uuid
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from app.models.profiles import Profile

if TYPE_CHECKING:
    from .videos import Video
    from .job_events import JobEvent


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(SAEnum(JobStatus), nullable=False, default=JobStatus.queued)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="jobs")

    videos: Mapped[List["Video"]] = relationship("Video", back_populates="job", cascade="all, delete-orphan")
    job_events: Mapped[List["JobEvent"]] = relationship("JobEvent", back_populates="job", cascade="all, delete-orphan")