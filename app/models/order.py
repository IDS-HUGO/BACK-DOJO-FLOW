from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base, TimestampMixin):
    """Represents a purchase order for a dojo plan."""
    
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id"), index=True)
    dojo_name: Mapped[str] = mapped_column(String(255), index=True)
    owner_name: Mapped[str] = mapped_column(String(255))
    owner_email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    owner_phone: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(120))
    timezone: Mapped[str] = mapped_column(String(80), default="America/Mexico_City")
    currency: Mapped[str] = mapped_column(String(10), default="MXN")
    
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True)
    payment_method: Mapped[str] = mapped_column(String(50), default="paypal")
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Credentials generated after payment
    generated_email: Mapped[str] = mapped_column(String(255), nullable=True)
    generated_password: Mapped[str] = mapped_column(String(255), nullable=True)
    credentials_sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
