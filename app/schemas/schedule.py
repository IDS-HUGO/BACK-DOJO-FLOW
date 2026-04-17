from pydantic import BaseModel
from datetime import time
from typing import Optional, List


class TeacherInSchedule(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StudentInSchedule(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True


class ScheduleCreate(BaseModel):
    class_type: str
    day_of_week: int
    start_time: str = "18:00"
    end_time: str = "19:00"
    active: bool = True


class ScheduleRead(ScheduleCreate):
    id: int
    max_students: int
    academy_id: int
    students: List[StudentInSchedule] = []
    teachers: List[TeacherInSchedule] = []

    class Config:
        from_attributes = True


class ScheduleResponse(BaseModel):
    id: int
    class_type: str
    day_of_week: int
    start_time: str
    end_time: str
    max_students: int
    active: bool
    students: List[StudentInSchedule] = []
    teachers: List[TeacherInSchedule] = []

    class Config:
        from_attributes = True


class EnrollStudentRequest(BaseModel):
    student_id: int