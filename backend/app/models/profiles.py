from __future__ import annotations

import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.database.database import Base

if TYPE_CHECKING:
    from .images import Image
    from .jobs import Job


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True
    )
    
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    images: Mapped[List["Image"]] = relationship(
        "Image", 
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    
    jobs: Mapped[List["Job"]] = relationship(
        "Job", 
        back_populates="profile",
        cascade="all, delete-orphan"
    )
