from fastapi import APIRouter, Depends, HTTPException
from app.auth.validate import get_current_user
from app.services.subscription_services.polar_sh import create_polar_checkout

router = APIRouter()

@router.post("/subscription/create-checkout")
async def create_checkout(product_id: str, user= Depends(get_current_user)):
    # check if the user is already subscribed or not ? or if the sub is active 
    existing_sub = await get_user_sub(user.id)
    if existing_sub and existing_sub.status == "active":
        raise HTTPException(400, "Already subscribed")
    
    checkout_url = await create_polar_checkout(
        product_id, user.id, user.email
    )

    return {"checkout_url": checkout_url}