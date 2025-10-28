from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.validate import get_current_user
from app.database.database import get_db
from app.services.subscription_services.polar_helpers import SubscriptionService
from app.schemas.subscriptions import SubscriptionResponse

router = APIRouter()


@router.get("/subscription/status", response_model=SubscriptionResponse)
async def get_subscription_status(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's subscription status"""
    subscription = await SubscriptionService.get_user_subscription(
        user["user_id"], 
        db
    )
    
    if not subscription:
        raise HTTPException(404, "No subscription found")
    
    return subscription
