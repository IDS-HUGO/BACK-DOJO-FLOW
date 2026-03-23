from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.attendance import Attendance
from app.models.payment import Payment
from app.models.student import Student
from app.schemas.dashboard import DashboardKpi, MrrTrendPoint

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=DashboardKpi)
def get_kpis(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    active_students = db.query(func.count(Student.id)).filter(Student.active.is_(True)).scalar() or 0
    mrr = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0
    take_rate_volume = float(mrr)

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    attendance_month = (
        db.query(func.count(Attendance.id)).filter(Attendance.attended_at >= month_start).scalar() or 0
    )

    churn_rate = 4.2
    nps = 76

    return DashboardKpi(
        mrr=float(mrr),
        churn_rate=churn_rate,
        take_rate_volume=take_rate_volume,
        nps=nps,
        active_students=active_students,
        attendance_this_month=attendance_month,
    )


@router.get("/mrr-trend", response_model=list[MrrTrendPoint])
def mrr_trend(_current_user=Depends(get_current_user)):
    sample = [
        MrrTrendPoint(label="Oct", mrr=9800),
        MrrTrendPoint(label="Nov", mrr=11400),
        MrrTrendPoint(label="Dic", mrr=13800),
        MrrTrendPoint(label="Ene", mrr=16400),
        MrrTrendPoint(label="Feb", mrr=18500),
        MrrTrendPoint(label="Mar", mrr=21300),
    ]
    return sample
