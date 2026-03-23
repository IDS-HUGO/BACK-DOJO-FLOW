from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base, TimestampMixin


class Teacher(Base, TimestampMixin):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    specialties = Column(String(255))  # JSON-like: "BJJ,MMA,Karate"
    hourly_rate = Column(Integer, default=50)  # $ por hora
    active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Teacher(id={self.id}, name={self.name}, email={self.email})>"
