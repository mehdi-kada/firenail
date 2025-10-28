from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.validate import get_current_user
from app.database.database import get_db
from app.services.subscription_services.polar_sh import create_polar_portal_session
from app.services.subscription_services.polar_helpers import SubscriptionService
from app.schemas.subscriptions import CustomerPortalResponse

router = APIRouter()


@router.get("/customer-portal", response_model=CustomerPortalResponse)
async def get_customer_portal(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get Polar customer portal URL for subscription management"""
    sub = await SubscriptionService.get_user_subscription(user["user_id"], db)
    
    if not sub or not sub.polar_customer_id:
        raise HTTPException(404, "No customer portal access")
    
    portal_url = await create_polar_portal_session(sub.polar_customer_id)

    return {"portal_url": portal_url}