from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.validate import get_current_user
from app.database.database import get_db
from app.services.subscription_services.polar_sh import create_polar_checkout
from app.services.subscription_services.polar_helpers import SubscriptionService
from app.schemas.subscriptions import CheckoutRequest, CheckoutResponse

router = APIRouter()


@router.post("/subscription/create-checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a Polar checkout session for subscription"""
    existing_sub = await SubscriptionService.get_user_subscription(user["user_id"], db)
    if existing_sub and existing_sub.status == "active":
        raise HTTPException(400, "Already subscribed")
    
    checkout_url = await create_polar_checkout(
        request.product_id, 
        user["user_id"], 
        user["email"]
    )
    
    if not checkout_url:
        raise HTTPException(500, "Failed to create checkout session")

    return {"checkout_url": checkout_url}