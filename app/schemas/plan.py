from datetime import datetime

from pydantic import BaseModel


class PlanRead(BaseModel):
    id: int
    name: str
    monthly_price: float
    description: str
    transaction_fee_percent: float

    class Config:
        from_attributes = True


class PlanPayPalCheckoutCreate(BaseModel):
    success_url: str | None = None
    cancel_url: str | None = None


class PlanPayPalCheckoutResponse(BaseModel):
    subscription_payment_id: int
    order_id: str
    checkout_url: str


class PlanPayPalVerifyRequest(BaseModel):
    order_id: str


class PlanSubscriptionPaymentRead(BaseModel):
    id: int
    user_id: int
    plan_id: int
    amount: float
    status: str
    provider: str
    mp_payment_id: str | None
    payment_date: datetime

    class Config:
        from_attributes = True
