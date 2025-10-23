import os
from typing import Optional
from dotenv import load_dotenv
from polar_sdk import Polar

load_dotenv()

POLAR_ACCESS_TOKEN = os.getenv("POLAR_ACCESS_TOKEN")
APP_URL = os.getenv("APP_URL", "http://localhost:3000")

polar = Polar(  server="sandbox",
              access_token=POLAR_ACCESS_TOKEN)


async def create_polar_checkout(
    product_id: str, 
    user_id: str, 
    user_email: str,
    success_url: Optional[str] = None
) -> Optional[str]:
    """Create Polar checkout session"""
    try:
        checkout = polar.checkouts.create(request={
            "products": [product_id],
            "success_url": success_url or f"{APP_URL}/thumbnails?success=true",
            "customer_email": user_email,
            "metadata": {"user_id": user_id},
            "allow_discount_codes": True,
            "require_billing_address": False,
        })
        return checkout.url
    except Exception as e:
        print(f"Error creating Polar checkout: {e}")
        return None


async def create_polar_portal_session(customer_id: str) -> str:
    """Create customer portal session"""
    try:
        session = polar.customer_sessions.create(request={
            "customer_id": customer_id,
        })
        return session.customer_portal_url
    except Exception as e:
        print(f"Error creating customer portal session: {e}")
        raise Exception("Failed to create customer portal session")


async def get_polar_subscription(subscription_id: str):
    """Get subscription from Polar"""
    try:
        return  polar.subscriptions.get(id=subscription_id)
    except Exception as e:
        print(f"Error getting Polar subscription: {e}")
        return None