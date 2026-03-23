from pydantic import BaseModel


class DashboardKpi(BaseModel):
    mrr: float
    churn_rate: float
    take_rate_volume: float
    nps: float
    active_students: int
    attendance_this_month: int


class MrrTrendPoint(BaseModel):
    label: str
    mrr: float
