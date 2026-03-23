from datetime import datetime

from pydantic import BaseModel, EmailStr


class StudentBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
