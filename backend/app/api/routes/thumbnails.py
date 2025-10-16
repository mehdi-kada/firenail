


from sqlalchemy import select, func
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import math

from app.schemas.thumbnail_schema import ThumbnailResponse, PaginatedThumbnailResponse
from app.auth.validate import get_current_user_profile
from app.database.database import get_db
from app.models.images import Image
from app.models.profiles import Profile


router = APIRouter()


@router.get("/", response_model=PaginatedThumbnailResponse)
async def list_thumbnails(
    page: int = 1,
    page_size: int = 12,
    profile: Profile = Depends(get_current_user_profile),
    db: AsyncSession = Depends(get_db),
) -> PaginatedThumbnailResponse:
    """
    List thumbnails for the current user profile with pagination.
    """
    count_query = select(func.count()).select_from(Image).where(Image.profile_id == profile.id)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size

    q = select(Image).where(Image.profile_id == profile.id).order_by(Image.created_at.desc()).limit(page_size).offset(offset)
    result = await db.execute(q)
    images = result.scalars().all()

    items = [
        ThumbnailResponse(
            id=image.id,
            job_id=image.job_id,
            storage_url=image.storage_public_url,
            video_title=image.video_title,
            keywords=image.keywords or [],
            created_at=image.created_at,
        )
        for image in images
    ]

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedThumbnailResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
