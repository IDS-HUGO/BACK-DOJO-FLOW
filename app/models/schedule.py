from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

# Tabla de unión: Schedule <-> Student
schedule_student = Table(
    'schedule_student',
    Base.metadata,
    Column('schedule_id', Integer, ForeignKey('schedules.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
)

# Tabla de unión: Schedule <-> Teacher
schedule_teacher = Table(
    'schedule_teacher',
    Base.metadata,
    Column('schedule_id', Integer, ForeignKey('schedules.id'), primary_key=True),
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True),
)

class Schedule(Base, TimestampMixin):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    class_type = Column(String(50), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(String(5), nullable=False)  # Cambiar a String para simplificar
    end_time = Column(String(5), nullable=False)    # Cambiar a String para simplificar
    max_students = Column(Integer, default=20)
    active = Column(Boolean, default=True, index=True)
    academy_id = Column(Integer, ForeignKey('academy_profile.id'), nullable=False, index=True)

    # Relaciones
    academy = relationship("AcademyProfile", back_populates="schedules")
    students = relationship("Student", secondary=schedule_student, back_populates="schedules")
    teachers = relationship("Teacher", secondary=schedule_teacher, back_populates="schedules")