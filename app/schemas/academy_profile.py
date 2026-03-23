from pydantic import BaseModel, EmailStr


class AcademyProfileBase(BaseModel):
    dojo_name: str
    owner_name: str
    contact_email: EmailStr
    contact_phone: str
    city: str
    timezone: str
    currency: str


class AcademyProfileUpdate(AcademyProfileBase):
    pass


class AcademyProfileRead(AcademyProfileBase):
    id: int

    class Config:
        from_attributes = True
