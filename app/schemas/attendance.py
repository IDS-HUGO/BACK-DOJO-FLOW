from datetime import datetime

from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    student_id: int
    class_type: str


class AttendanceRead(BaseModel):
    id: int
    student_id: int
    class_type: str
    attended_at: datetime

    class Config:
        from_attributes = True
