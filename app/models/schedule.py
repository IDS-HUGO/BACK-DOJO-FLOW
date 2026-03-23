from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Schedule(Base, TimestampMixin):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    class_type = Column(String(50), nullable=False)  # BJJ, MMA, Karate, TKD
    day_of_week = Column(Integer, nullable=False)  # 0=Lunes, 1=Martes, ..., 6=Domingo
    start_time = Column(Time, nullable=False)  # HH:MM
    end_time = Column(Time, nullable=False)  # HH:MM
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    max_students = Column(Integer, default=20)
    active = Column(Boolean, default=True)

    teacher = relationship("Teacher", foreign_keys=[teacher_id])

    def __repr__(self):
        return f"<Schedule(id={self.id}, class_type={self.class_type}, day={self.day_of_week})>"
