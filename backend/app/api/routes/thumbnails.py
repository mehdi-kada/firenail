


from sqlalchemy import select
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.thumbnail_schema import ThumbnailResponse
from backend.app.auth.validate import get_current_user_profile
from app.database.database import get_db
from backend.app.models.images import Image
from app.models.profiles import Profile


router = APIRouter()


@router.get("/", response_model=list[ThumbnailResponse])
async def list_thumbnails(
    limit: int = 10,
    offset: int = 0,
    profile: Profile = Depends(get_current_user_profile),
    db: AsyncSession = Depends(get_db),
) -> list[ThumbnailResponse]:
    """
    List thumbnails for the current user profile.
    """
    q = select(Image).where(Image.profile_id == profile.id).limit(limit).offset(offset)
    result = await db.execute(q)
    images = result.scalars().all()
    return [
        ThumbnailResponse(
            id=image.id,
            job_id=image.job_id,
            storage_url=image.storage_public_url,
            keywords=image.keywords,
            created_at=image.created_at,
        )
        for image in images
    ]
