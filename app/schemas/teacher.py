from pydantic import BaseModel, EmailStr
from typing import Optional


class TeacherBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    specialties: Optional[str] = None
    hourly_rate: int = 50
    active: bool = True


class TeacherCreate(TeacherBase):
    pass


class TeacherRead(TeacherBase):
    id: int

    class Config:
        from_attributes = True

