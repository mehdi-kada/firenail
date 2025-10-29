from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.validate import get_current_user_profile
from app.database.database import get_db
from app.models.profiles import Profile
from app.services.subscription_services.limit_checker import (
    check_and_reset_limits,
    UsageLimitExceeded,
    LimitCheckResult
)


async def check_image_generation_limit(
    profile: Profile = Depends(get_current_user_profile),
    db: AsyncSession = Depends(get_db)
) -> LimitCheckResult:
    """
    Dependency that checks if user has remaining image generation quota.
    Automatically resets limits if billing period has changed (lazy reset).
    Raises HTTP 429 if limit is exceeded.
    """
    try:
        result = await check_and_reset_limits(profile, db)
        return result
    except UsageLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Usage limit exceeded",
                "message": str(e),
                "current": e.current,
                "limit": e.limit,
                "plan": e.plan_name
            }
        )
