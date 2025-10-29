from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class SubscriptionBase(BaseModel):
    user_id: UUID
    polar_subscription_id: str
    polar_customer_id: str
    status: str
    plan_name: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    renews_at: Optional[datetime] = None


class SubscriptionCreate(SubscriptionBase):
    images_generated: int = 0
    period_reset_at: Optional[datetime] = None


class SubscriptionUpdate(BaseModel):
    status: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None
    renews_at: Optional[datetime] = None


class SubscriptionResponse(SubscriptionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CheckoutRequest(BaseModel):
    product_id: str = Field(..., description="Polar product ID")


class CheckoutResponse(BaseModel):
    checkout_url: str


class CustomerPortalResponse(BaseModel):
    portal_url: str
