from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone
from uuid import UUID

from app.schemas.subscriptions import SubscriptionCreate
from app.models.subscriptions import Subscription
from app.models.profiles import Profile


class SubscriptionService:

    @staticmethod
    async def get_user_subscription(
        user_id: UUID,
        db: AsyncSession
    ) -> Optional[Subscription]:
        """Get the latest subscription for a user from db"""
        query = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_subscription_by_polar_id(
        polar_subscription_id: str,
        db: AsyncSession
    ) -> Optional[Subscription]:
        """Get subscription by Polar subscription ID"""
        query = select(Subscription).where(
            Subscription.polar_subscription_id == polar_subscription_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_subscription(
        subscription_data: SubscriptionCreate,
        db: AsyncSession
    ) -> Subscription:
        """Create or update subscription"""
        existing = await SubscriptionService.get_subscription_by_polar_id(
            subscription_data.polar_subscription_id,
            db
        )
        
        if existing:
            period_changed = existing.current_period_start != subscription_data.current_period_start
            
            for field, value in subscription_data.model_dump().items():
                if field == "images_generated" and not period_changed:
                    continue
                if field == "period_reset_at" and not period_changed:
                    continue
                setattr(existing, field, value)
            
            if period_changed:
                existing.images_generated = 0
                existing.period_reset_at = subscription_data.current_period_start
            
            existing.updated_at = datetime.now(timezone.utc)
            subscription = existing
        else:
            subscription_dict = subscription_data.model_dump()
            if subscription_dict.get("period_reset_at") is None:
                subscription_dict["period_reset_at"] = subscription_data.current_period_start
            subscription = Subscription(**subscription_dict)
            db.add(subscription)
        
        await db.commit()
        await db.refresh(subscription)
        
        premium_status = subscription_data.status in ["active", "cancelled"]
        await SubscriptionService.update_user_premium_status(
            subscription_data.user_id,
            premium_status,
            db
        )
        
        return subscription

    @staticmethod
    async def update_user_premium_status(
        user_id: UUID,
        is_premium: bool,
        db: AsyncSession
    ) -> bool:
        """Update user's premium status"""
        profile = await db.get(Profile, user_id)
        
        if profile:
            profile.is_premium = is_premium
            await db.commit()
            return True
        return False

    @staticmethod
    async def cancel_subscription(
        polar_subscription_id: str,
        db: AsyncSession
    ) -> bool:
        """Mark subscription as cancelled in DB"""
        subscription = await SubscriptionService.get_subscription_by_polar_id(
            polar_subscription_id,
            db
        )
        
        if not subscription:
            return False
        
        subscription.status = "cancelled"
        subscription.cancel_at_period_end = True
        subscription.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        return True

    @staticmethod
    async def check_user_premium_status(
        user_id: UUID,
        db: AsyncSession
    ) -> bool:
        """
        Check if user has active premium access
        Includes grace period for cancelled subscriptions
        """
        profile = await db.get(Profile, user_id)
        
        if not profile:
            return False
        
        if profile.is_premium:
            return True
        
        query = (
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == "cancelled",
                    Subscription.current_period_end > datetime.now(timezone.utc)
                )
            )
        )
        result = await db.execute(query)
        cancelled_sub = result.scalar_one_or_none()
        
        return cancelled_sub is not None