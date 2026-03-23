from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    monthly_price: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String(255))
    transaction_fee_percent: Mapped[float] = mapped_column(Float)
