from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PlanSubscriptionPayment(Base):
    __tablename__ = "plan_subscription_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    provider: Mapped[str] = mapped_column(String(50), default="paypal")
    mp_payment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
