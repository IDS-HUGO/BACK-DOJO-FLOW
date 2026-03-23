from sqlalchemy import Column, Integer, String, Boolean, Date
from app.models.base import Base, TimestampMixin


class Coupon(Base, TimestampMixin):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_percent = Column(Integer, nullable=False)  # 5, 10, 15, etc.
    max_uses = Column(Integer, default=None)  # None = unlimited
    used_count = Column(Integer, default=0)
    valid_until = Column(Date, nullable=False)
    active = Column(Boolean, default=True)
    description = Column(String(255))

    def __repr__(self):
        return f"<Coupon(id={self.id}, code={self.code}, discount={self.discount_percent}%)>"
