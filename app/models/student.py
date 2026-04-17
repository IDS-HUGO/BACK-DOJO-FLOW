from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base, TimestampMixin

class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    belt_level = Column(String(50), default="Cinta Blanca")
    status = Column(String(20), default="active")
    academy_id = Column(Integer, ForeignKey('academy_profile.id'), nullable=False)
    active = Column(Boolean, default=True)

    # Relaciones
    academy = relationship("AcademyProfile", back_populates="students")
    schedules = relationship("Schedule", secondary="schedule_student", back_populates="students")
    belt_progress = relationship("BeltProgress", back_populates="student")