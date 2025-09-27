from typing import List, Optional
import uuid
from sqlalchemy import DateTime, Integer, String, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.database import Base


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))

    video_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    video_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    crawled_images: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True) 
    generated_image_storage_urls: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 
    
    # Relationship to profile (many-to-one)
    profile: Mapped["Profile"] = relationship("Profile", back_populates="images")

    __table_args__ = (
        Index('ix_images_profile_created', 'profile_id', 'created_at'),
    )

    
    