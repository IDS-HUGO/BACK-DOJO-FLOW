from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Teacher(Base, TimestampMixin):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    specialties = Column(String(500), nullable=True)
    hourly_rate = Column(Float, default=50.0)
    active = Column(Boolean, default=True)
    academy_id = Column(Integer, ForeignKey('academy_profile.id'), nullable=False)

    # Relaciones
    academy = relationship("AcademyProfile", back_populates="teachers")
    schedules = relationship("Schedule", secondary="schedule_teacher", back_populates="teachers")