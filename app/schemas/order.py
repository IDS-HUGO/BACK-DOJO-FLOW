from datetime import datetime
from enum import Enum
from typing import Optional

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
    owner_phone: str
    city: str
    timezone: str
    currency: str
    amount: float
    status: str
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    generated_email: Optional[str] = None
    generated_password: Optional[str] = None
    credentials_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    id: int
    dojo_name: str
    owner_email: str
    amount: float
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True