from datetime import datetime

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    student_id: int
    amount: float = Field(gt=0)
    method: str


class PaymentRead(BaseModel):
    id: int
    student_id: int
    amount: float
    status: str
    method: str
    payment_date: datetime

    class Config:
        from_attributes = True
