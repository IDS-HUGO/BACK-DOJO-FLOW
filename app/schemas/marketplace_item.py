from datetime import datetime

from pydantic import BaseModel, Field


class MarketplaceItemCreate(BaseModel):
    name: str
    category: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class MarketplaceItemRead(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
