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
    body = await request.body()
    headers = dict(request.headers)
    
    try:
        event = validate_event(body, headers, os.getenv("POLAR_WEBHOOK_SECRET", ""))
        print("Webhook verified successfully, here is the event: ", event)
    except WebhookVerificationError as e:
        print(f"Webhook verification failed: {e}")
        raise HTTPException(403, "Invalid webhook signature")
    

    event_type = event.TYPE
    print(f"Received webhook event: {event_type}")
    
    # Check event type and handle accordingly
    if event_type == 'order.paid':
        await handle_order_paid(event, db)
    elif event_type == 'subscription.created':
        await handle_subscription_created(event, db)
    elif event_type == 'subscription.updated':
        await handle_subscription_updated(event, db)
    elif event_type == 'subscription.canceled':
        await handle_subscription_canceled(event, db)
    elif event_type == 'subscription.revoked':
        await handle_subscription_revoked(event, db)
    else:
        print(f"Unhandled event type: {event_type}")

    return {"received": True}


async def handle_order_paid(event, db: AsyncSession):
    """Handle order.paid event - creates/updates subscription"""
    try:
        order_data = event.data
        
        user_id = order_data.metadata.get('user_id') if hasattr(order_data.metadata, 'get') else order_data.metadata.get('user_id', None)
        print("user id is :", user_id)
        if not user_id:
            print("No user_id in order metadata")
            return
        
        subscription_data = order_data.subscription if hasattr(order_data, "subscription") else None
        if not subscription_data:
            print("Order doesn't contain subscription data, skipping")
            return
        
        subscription_create = SubscriptionCreate(
            user_id=UUID(user_id),
            polar_subscription_id=subscription_data.id,
            polar_customer_id=subscription_data.customer_id,
            status=subscription_data.status,
            plan_name=subscription_data.product.name if hasattr(subscription_data, "product") else "Polar Subscription",
            current_period_start=subscription_data.current_period_start,
            current_period_end=subscription_data.current_period_end,
            cancel_at_period_end=subscription_data.cancel_at_period_end,
            renews_at=subscription_data.current_period_end,
            images_generated=0,
            period_reset_at=subscription_data.current_period_start
        )
        
        await SubscriptionService.upsert_subscription(subscription_create, db)
        print(f"Successfully created subscription from paid order for user {user_id}")
    except Exception as e:
        print(f"Error handling order paid: {e}")
        import traceback
        traceback.print_exc()


async def handle_subscription_created(event, db: AsyncSession):
    """Handle subscription.created event"""
    try:
        subscription_data = event.data
        
        user_id = subscription_data.metadata.get('user_id') if hasattr(subscription_data.metadata, 'get') else None
        if not user_id:
            print("No user_id in subscription metadata")
            return
        
        subscription_create = SubscriptionCreate(
            user_id=UUID(user_id),
            polar_subscription_id=subscription_data.id,
            polar_customer_id=subscription_data.customer_id,
            status=subscription_data.status,
            plan_name=subscription_data.product.name if hasattr(subscription_data, "product") else "Polar Subscription",
            current_period_start=subscription_data.current_period_start,
            current_period_end=subscription_data.current_period_end,
            cancel_at_period_end=subscription_data.cancel_at_period_end,
            renews_at=subscription_data.current_period_end,
            images_generated=0,
            period_reset_at=subscription_data.current_period_start
        )
        
        await SubscriptionService.upsert_subscription(subscription_create, db)
        print(f"Updated database with subscription data for user {user_id}")
    except Exception as e:
        print(f"Error handling subscription creation: {e}")
        import traceback
        traceback.print_exc()


async def handle_subscription_updated(event, db: AsyncSession):
    """Handle subscription.updated event"""
    try:
        subscription_data = event.data
        
        user_id = subscription_data.metadata.get('user_id') if hasattr(subscription_data.metadata, 'get') else None
        if not user_id:
            print("No user_id in subscription metadata")
            return
        
        subscription_create = SubscriptionCreate(
            user_id=UUID(user_id),
            polar_subscription_id=subscription_data.id,
            polar_customer_id=subscription_data.customer_id,
            status=subscription_data.status,
            plan_name=subscription_data.product.name if hasattr(subscription_data, "product") else "Polar Subscription",
            current_period_start=subscription_data.current_period_start,
            current_period_end=subscription_data.current_period_end,
            cancel_at_period_end=subscription_data.cancel_at_period_end,
            renews_at=subscription_data.current_period_end,
            images_generated=0,
            period_reset_at=subscription_data.current_period_start
        )
        
        await SubscriptionService.upsert_subscription(subscription_create, db)
        print(f"Updated subscription for user {user_id}")
    except Exception as e:
        print(f"Error handling subscription update: {e}")
        import traceback
        traceback.print_exc()


async def handle_subscription_canceled(event, db: AsyncSession):
    """Handle subscription.canceled event - mark as cancelled but keep premium until period ends"""
    try:
        subscription_data = event.data
        subscription_id = subscription_data.id
        
        print(f"Handling subscription cancellation: {subscription_id}")
        
        success = await SubscriptionService.cancel_subscription(subscription_id, db)
        
        if success:
            print("Subscription marked as cancelled, user retains access until period ends")
        else:
            print("Failed to cancel subscription in database")
    except Exception as e:
        print(f"Error handling subscription cancellation: {e}")
        import traceback
        traceback.print_exc()


async def handle_subscription_revoked(event, db: AsyncSession):
    """Handle subscription.revoked event - immediate cancellation/revocation of access"""
    try:
        subscription_data = event.data
        subscription_id = subscription_data.id
        
        print(f"Handling subscription revocation: {subscription_id}")
        
        success = await SubscriptionService.revoke_subscription(subscription_id, db)
        
        if success:
            print("Subscription revoked, user access removed immediately")
        else:
            print("Failed to revoke subscription in database")
    except Exception as e:
        print(f"Error handling subscription revocation: {e}")
        import traceback
        traceback.print_exc()
