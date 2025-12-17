


from sqlalchemy import select, func
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import math
from uuid import UUID

from app.schemas.thumbnail_schema import ThumbnailResponse, PaginatedThumbnailResponse, ThumbnailRegenerateRequest
from app.auth.validate import get_current_user_profile
from app.auth.subscription_limits import check_image_generation_limit
from app.services.subscription_services.limit_checker import LimitCheckResult, increment_image_count
from app.database.database import get_db
from app.models.images import Image
from app.models.profiles import Profile
from app.services.image_generation import regenerate_thumbnail


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

    items = []
    for image in images:
        urls = image.storage_public_url
        if isinstance(urls, str):
            urls = [urls]
        elif urls is None:
            urls = []
            
        items.append(ThumbnailResponse(
            id=image.id,
            job_id=image.job_id,
            storage_url=urls,
            video_title=image.video_title,
            keywords=image.keywords or [],
            created_at=image.created_at,
        ))

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedThumbnailResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/{image_id}/regenerate", response_model=ThumbnailResponse)
async def regenerate_thumbnail_route(
    image_id: UUID,
    request: ThumbnailRegenerateRequest,
    profile: Profile = Depends(get_current_user_profile),
    limit_check: LimitCheckResult = Depends(check_image_generation_limit),
    db: AsyncSession = Depends(get_db),
):
    image = await db.get(Image, image_id)
    print("just got image : ", image)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if not image.storage_public_url:
        raise HTTPException(status_code=400, detail="Image does not have a URL")

    try:
        current_urls = image.storage_public_url if isinstance(image.storage_public_url, list) else [image.storage_public_url]
        current_url = current_urls[-1]
        
        new_url = regenerate_thumbnail(
            job_id=str(image.job_id),
            image_url=current_url,
            prompt=request.prompt
        )
        print("new url : ", new_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    updated_urls = list(current_urls)
    updated_urls.append(new_url)
    image.storage_public_url = updated_urls
    
    await increment_image_count(profile.id, db)
    
    await db.commit()
    await db.refresh(image)

    return ThumbnailResponse(
        id=image.id,
        job_id=image.job_id,
        storage_url=image.storage_public_url,
        video_title=image.video_title,
        keywords=image.keywords or [],
        created_at=image.created_at,
    )
