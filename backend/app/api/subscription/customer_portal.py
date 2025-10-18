from fastapi import Depends, APIRouter, HTTPException
from app.auth.validate import get_current_user
from app.services.subscription_services.polar_sh import create_polar_portal_session


router = APIRouter()

@router.post("/customer-portal")
async def get_customer_portal(user= Depends(get_current_user)):
    sub = await  get_user_sub(user.id)
    if not sub or not sub.polar_customer_id:
        raise HTTPException(404, "No customer portal access")
    
    portal_url = await create_polar_portal_session(sub.polar_customer_id)

    return {"portal_url": portal_url}