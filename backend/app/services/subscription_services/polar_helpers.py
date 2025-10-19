from fastapi import Request, Header, APIRouter, HTTPException
import os
from dotenv import load_dotenv
from polar_sdk.webhooks import validate_event, WebhookVerificationError

router = APIRouter()

load_dotenv()

@router.post("/webhooks/polar")
async def polar_webhook(request: Request, webhook_signature: str = Header(None, alias="webhook-signature")):
    body = await request.body()
    headers = {
        "webhook-signature": webhook_signature
    }
    try:
        event = validate_event(body, headers, os.getenv("POLAR_WEBHOOK_SECRET", ""))
    except WebhookVerificationError:
        raise HTTPException(403, "Invalid webhook signature")
    
    # handle the events
    if event.type == "order.paid":
        await handle_order_paid(event.data)
    elif event.type == "subscription.created":
        await handle_subscription_created(event.data)
    elif event.type == "subscription.updated":
        await handle_subscription_updated(event.data)
    elif event.type == "subscription.canceled":
        await handle_subscription_canceled(event.data)

    return {"received": True}

