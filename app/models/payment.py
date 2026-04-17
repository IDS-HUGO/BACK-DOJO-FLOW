from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)

    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # 🔑 MercadoPago ID

    amount: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(String(20))  # approved, pending, rejected
    method: Mapped[str] = mapped_column(String(50))  # mercadopago

    payment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)