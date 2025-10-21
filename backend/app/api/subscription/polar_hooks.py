from fastapi import Request, Header, APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import os
from dotenv import load_dotenv
from polar_sdk.webhooks import validate_event, WebhookVerificationError
from datetime import datetime
from uuid import UUID

from app.database.database import get_db
from app.services.subscription_services.polar_helpers import SubscriptionService
from app.schemas.subscriptions import SubscriptionCreate

router = APIRouter()
load_dotenv()


@router.post("/webhooks/polar")
async def polar_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    webhook_signature: str = Header(None, alias="webhook-signature")
):
    """Handle Polar webhook events"""
    body = await request.body()
    headers = dict(request.headers)
    
    try:
        event = validate_event(body, headers, os.getenv("POLAR_WEBHOOK_SECRET", ""))
    except WebhookVerificationError as e:
        print(f"Webhook verification failed: {e}")
        raise HTTPException(403, "Invalid webhook signature")
    
    event_type = event.type
    event_data = event.data
    
    if event_type == "order.paid":
        await handle_order_paid(event_data, db)
    elif event_type == "subscription.created":
        await handle_subscription_created(event_data, db)
    elif event_type == "subscription.updated":
        await handle_subscription_updated(event_data, db)
    elif event_type == "subscription.canceled":
        await handle_subscription_canceled(event_data, db)
    else:
        print(f"Unhandled event type: {event_type}")

    return {"received": True}


async def handle_order_paid(order_data: dict, db: AsyncSession):
    """Handle order.paid event - creates/updates subscription"""
    try:
        user_id = order_data.get("metadata", {}).get("user_id")
        if not user_id:
            print("No user_id in order metadata")
            return
        
        subscription_data = order_data.get("subscription")
        if not subscription_data:
            print("Order doesn't contain subscription data, skipping")
            return
        
        subscription_create = SubscriptionCreate(
            user_id=UUID(user_id),
            polar_subscription_id=subscription_data["id"],
            polar_customer_id=subscription_data["customer_id"],
            status=subscription_data["status"],
            plan_name=subscription_data.get("product", {}).get("name", "Polar Subscription"),
            current_period_start=datetime.fromisoformat(subscription_data["current_period_start"]),
            current_period_end=datetime.fromisoformat(subscription_data["current_period_end"]),
            cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
            renews_at=datetime.fromisoformat(subscription_data["current_period_end"])
        )
        
        await SubscriptionService.upsert_subscription(subscription_create, db)
        print(f"Successfully created subscription from paid order for user {user_id}")
    except Exception as e:
        print(f"Error handling order paid: {e}")


async def handle_subscription_created(subscription_data: dict, db: AsyncSession):
    """Handle subscription.created event"""
    try:
        user_id = subscription_data.get("metadata", {}).get("user_id")
        if not user_id:
            print("No user_id in subscription metadata")
            return
        
        subscription_create = SubscriptionCreate(
            user_id=UUID(user_id),
            polar_subscription_id=subscription_data["id"],
            polar_customer_id=subscription_data["customer_id"],
            status=subscription_data["status"],
            plan_name=subscription_data.get("product", {}).get("name", "Polar Subscription"),
            current_period_start=datetime.fromisoformat(subscription_data["current_period_start"]),
            current_period_end=datetime.fromisoformat(subscription_data["current_period_end"]),
            cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
            renews_at=datetime.fromisoformat(subscription_data["current_period_end"])
        )
        
        await SubscriptionService.upsert_subscription(subscription_create, db)
        print(f"Updated database with subscription data for user {user_id}")
    except Exception as e:
        print(f"Error handling subscription creation: {e}")


async def handle_subscription_updated(subscription_data: dict, db: AsyncSession):
    """Handle subscription.updated event"""
    try:
        user_id = subscription_data.get("metadata", {}).get("user_id")
        if not user_id:
            print("No user_id in subscription metadata")
            return
        
        subscription_create = SubscriptionCreate(
            user_id=UUID(user_id),
            polar_subscription_id=subscription_data["id"],
            polar_customer_id=subscription_data["customer_id"],
            status=subscription_data["status"],
            plan_name=subscription_data.get("product", {}).get("name", "Polar Subscription"),
            current_period_start=datetime.fromisoformat(subscription_data["current_period_start"]),
            current_period_end=datetime.fromisoformat(subscription_data["current_period_end"]),
            cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
            renews_at=datetime.fromisoformat(subscription_data.get("current_period_end"))
        )
        
        await SubscriptionService.upsert_subscription(subscription_create, db)
        print(f"Updated subscription for user {user_id}")
    except Exception as e:
        print(f"Error handling subscription update: {e}")


async def handle_subscription_canceled(subscription_data: dict, db: AsyncSession):
    """Handle subscription.canceled event - mark as cancelled but keep premium until period ends"""
    try:
        subscription_id = subscription_data["id"]
        print(f"Handling subscription cancellation: {subscription_id}")
        
        success = await SubscriptionService.cancel_subscription(subscription_id, db)
        
        if success:
            print("Subscription marked as cancelled, user retains access until period ends")
        else:
            print("Failed to cancel subscription in database")
    except Exception as e:
        print(f"Error handling subscription cancellation: {e}")
