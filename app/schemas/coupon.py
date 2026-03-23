from pydantic import BaseModel
from datetime import date
from typing import Optional


class CouponBase(BaseModel):
    code: str
    discount_percent: int
    max_uses: Optional[int] = None
    valid_until: date
    active: bool = True
    description: Optional[str] = None


class CouponCreate(CouponBase):
    pass


class CouponRead(CouponBase):
    id: int
    used_count: int = 0

    class Config:
        from_attributes = True
