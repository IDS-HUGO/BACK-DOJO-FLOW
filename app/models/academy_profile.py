from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base, TimestampMixin

class AcademyProfile(Base, TimestampMixin):
    __tablename__ = "academy_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # ← AGREGADO
    dojo_name = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), default="America/Mexico_City")
    currency = Column(String(3), default="MXN")

    # Relaciones
    user = relationship("User", back_populates="academy_profile")
    students = relationship("Student", back_populates="academy")
    teachers = relationship("Teacher", back_populates="academy")
    schedules = relationship("Schedule", back_populates="academy")