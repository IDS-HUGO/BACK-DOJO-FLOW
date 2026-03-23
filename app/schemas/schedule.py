from pydantic import BaseModel
from datetime import time
from typing import Optional


class ScheduleBase(BaseModel):
    class_type: str
    day_of_week: int  # 0=Lunes, ..., 6=Domingo
    start_time: time
    end_time: time
    teacher_id: Optional[int] = None
    max_students: int = 20
    active: bool = True


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleRead(ScheduleBase):
    id: int

    class Config:
        from_attributes = True
