from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):
    plan_id: int
    dojo_name: str
    owner_name: str
    owner_email: EmailStr
    owner_phone: str
    city: str
    timezone: str = "America/Mexico_City"
    currency: str = "MXN"


class OrderCheckout(BaseModel):
    """Request to create a checkout session."""
    order_id: int


class OrderResponse(BaseModel):
    id: int
    plan_id: int
    dojo_name: str
    owner_name: str
    owner_email: str
    amount: float
    status: str
    payment_method: str
    transaction_id: str | None
    paid_at: datetime | None
    credentials_sent_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    id: int
    dojo_name: str
    owner_email: str
    amount: float
    status: str
    paid_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
