from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReportSummary(BaseModel):
    total_revenue: float
    total_students: int
    active_students: int
    inactive_students: int
    total_enrollments: int
    attendance_rate: float
    pending_payments: float
    paid_payments: float
    total_teachers: int
    average_attendance_per_class: float
    top_class_by_attendance: str
    top_teacher_by_rating: Optional[str]


class AttendanceTrend(BaseModel):
    date: str
    count: int


class RevenueBreakdown(BaseModel):
    label: str
    value: float
