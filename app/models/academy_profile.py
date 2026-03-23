from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AcademyProfile(Base):
    __tablename__ = "academy_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dojo_name: Mapped[str] = mapped_column(String(255))
    owner_name: Mapped[str] = mapped_column(String(255))
    contact_email: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(120))
    timezone: Mapped[str] = mapped_column(String(80), default="America/Mexico_City")
    currency: Mapped[str] = mapped_column(String(10), default="MXN")
