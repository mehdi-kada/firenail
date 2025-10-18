import os
from dotenv import load_dotenv
from polar_sdk import Polar

load_dotenv()

POLAR_ACCESS_TOKEN = os.getenv("POLAR_ACCESS_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

polar = Polar(access_token=POLAR_ACCESS_TOKEN)

async def create_polar_checkout(product_id: str, user_id: str, user_email: str):
    checkout = await polar.checkouts.create(request={
        "products": [product_id],
        "success_url": f"{BACKEND_URL}/thmbnails/success?checkout_id={{CHECKOUT_ID}}",
        "customer_email": user_email,
        "metadata": {"user_id": user_id},
        "allow_discount_codes": True,
    })

    return checkout.url


async def create_polar_portal_session(customer_id: str):
    session = await polar.portal_sessions.create(request={
        "customer": customer_id,
    })
    return session.url