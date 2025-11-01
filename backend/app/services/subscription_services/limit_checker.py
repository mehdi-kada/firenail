from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from uuid import UUID

from app.models.profiles import Profile
from app.models.subscriptions import Subscription
from app.constants.plan_limits import get_plan_limit


class UsageLimitExceeded(Exception):
    """Raised when user exceeds their usage limit"""
    def __init__(self, current: int, limit: int, plan_name: str):
        self.current = current
        self.limit = limit
        self.plan_name = plan_name
        super().__init__(
            f"Usage limit exceeded: {current}/{limit} images used on {plan_name} plan"
        )


class LimitCheckResult:
    def __init__(self, images_used: int, limit: int, plan_name: str, reset_at: datetime):
        self.images_used = images_used
        self.limit = limit
        self.plan_name = plan_name
        self.reset_at = reset_at
        self.remaining = max(0, limit - images_used)


async def check_and_reset_limits(
    profile: Profile,
    db: AsyncSession
) -> LimitCheckResult:
    """
    Check user's usage limits and reset if period has expired (lazy reset).
    Returns current usage information.
    Raises UsageLimitExceeded if limit is exceeded.
    """
    subscription = profile.subscription
    now = datetime.utcnow()
    
    if subscription and subscription.status in ["active", "cancelled"]:
        if subscription.status == "cancelled" and subscription.current_period_end < now:
            plan_name = "free"
            limit = get_plan_limit(plan_name)
            
            if _should_reset_period(profile.period_reset_at, now):
                profile.images_generated = 0
                profile.period_reset_at = now
                await db.commit()
            
            if profile.images_generated >= limit:
                raise UsageLimitExceeded(profile.images_generated, limit, plan_name)
            
            return LimitCheckResult(
                images_used=profile.images_generated,
                limit=limit,
                plan_name=plan_name,
                reset_at=profile.period_reset_at + timedelta(days=30)
            )
        
        plan_name = subscription.plan_name
        limit = get_plan_limit(plan_name)
        
        if subscription.current_period_start > subscription.period_reset_at:
            subscription.images_generated = 0
            subscription.period_reset_at = subscription.current_period_start
            await db.commit()
        
        if subscription.images_generated >= limit:
            raise UsageLimitExceeded(subscription.images_generated, limit, plan_name)
        
        return LimitCheckResult(
            images_used=subscription.images_generated,
            limit=limit,
            plan_name=plan_name,
            reset_at=subscription.current_period_end
        )
    else:
        plan_name = "free"
        limit = get_plan_limit(plan_name)
        
        if _should_reset_period(profile.period_reset_at, now):
            profile.images_generated = 0
            profile.period_reset_at = now
            await db.commit()
        
        if profile.images_generated >= limit:
            raise UsageLimitExceeded(profile.images_generated, limit, plan_name)
        
        return LimitCheckResult(
            images_used=profile.images_generated,
            limit=limit,
            plan_name=plan_name,
            reset_at=profile.period_reset_at + timedelta(days=30)
        )


def _should_reset_period(last_reset: datetime, now: datetime) -> bool:
    """Check if a month has passed since last reset"""
    return (now - last_reset).days >= 30


async def increment_image_count(
    user_id: UUID,
    db: AsyncSession
) -> None:
    """
    Increment the image generation count for a user.
    Should be called after successful image generation.
    """
    stmt = select(Profile).where(Profile.id == user_id).options(selectinload(Profile.subscription))
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        return
    
    subscription = profile.subscription
    
    if subscription and subscription.status in ["active", "cancelled"]:
        if subscription.status == "cancelled" and subscription.current_period_end < datetime.utcnow():
            profile.images_generated += 1
        else:
            subscription.images_generated += 1
    else:
        profile.images_generated += 1
    
    await db.commit()
