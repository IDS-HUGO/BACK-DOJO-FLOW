from datetime import datetime

from pydantic import BaseModel, Field


class BeltCreate(BaseModel):
    student_id: int
    belt_name: str
    exam_score: int = Field(ge=0, le=100)


class BeltRead(BaseModel):
    id: int
    student_id: int
    belt_name: str
    exam_score: int
    approved: bool
    evaluated_at: datetime

    class Config:
        from_attributes = True
