from pydantic import BaseModel


class PlanRead(BaseModel):
    id: int
    name: str
    monthly_price: float
    description: str
    transaction_fee_percent: float

    class Config:
        from_attributes = True
