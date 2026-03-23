from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.payment import Payment
from app.models.teacher import Teacher
from app.schemas.reports import ReportSummary, AttendanceTrend, RevenueBreakdown

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=ReportSummary)
def get_report_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Basic counts
    total_students = db.query(func.count(Student.id)).scalar() or 0
    active_students = db.query(func.count(Student.id)).filter(Student.active == True).scalar() or 0
    inactive_students = total_students - active_students
    total_teachers = db.query(func.count(Teacher.id)).scalar() or 0

    # Revenue
    total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.status == "paid").scalar() or 0
    pending_payments = db.query(func.sum(Payment.amount)).filter(Payment.status == "pending").scalar() or 0
    paid_payments = total_revenue

    # Attendance
    total_enrollments = db.query(func.count(Attendance.id)).scalar() or 0
    attendance_this_month = db.query(func.count(Attendance.id)).filter(
        Attendance.attended_at >= datetime.now().replace(day=1)
    ).scalar() or 0

    # Rate calculations
    attendance_rate = (attendance_this_month / max(total_students * 4, 1)) * 100  # 4 clases/mes promedio
    attendance_rate = min(100, attendance_rate)

    # Top class by attendance
    top_class = db.query(
        Attendance.class_type,
        func.count(Attendance.id).label("count")
    ).group_by(Attendance.class_type).order_by(func.count(Attendance.id).desc()).first()
    top_class_label = top_class[0] if top_class else "N/A"

    # Average per class
    avg_attendance = (total_enrollments / max(4 * total_students, 1)) * 100  # simplified

    return ReportSummary(
        total_revenue=float(total_revenue),
        total_students=total_students,
        active_students=active_students,
        inactive_students=inactive_students,
        total_enrollments=total_enrollments,
        attendance_rate=float(min(100, attendance_rate)),
        pending_payments=float(pending_payments),
        paid_payments=float(paid_payments),
        total_teachers=total_teachers,
        average_attendance_per_class=float(min(100, (attendance_this_month / max(1, total_students)))),
        top_class_by_attendance=top_class_label,
        top_teacher_by_rating=None,
    )


@router.get("/attendance-trend", response_model=list[AttendanceTrend])
def get_attendance_trend(days: int = 30, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    start_date = datetime.now() - timedelta(days=days)
    
    trends = db.query(
        func.date(Attendance.attended_at).label("date"),
        func.count(Attendance.id).label("count")
    ).filter(
        Attendance.attended_at >= start_date
    ).group_by(func.date(Attendance.attended_at)).order_by("date").all()

    return [
        AttendanceTrend(date=str(date), count=count)
        for date, count in trends
    ]


@router.get("/revenue-breakdown", response_model=list[RevenueBreakdown])
def get_revenue_breakdown(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Payment method breakdown
    breakdown = db.query(
        Payment.method,
        func.sum(Payment.amount).label("total")
    ).filter(Payment.status == "paid").group_by(Payment.method).all()

    return [
        RevenueBreakdown(label=method, value=float(total or 0))
        for method, total in breakdown
    ]


@router.get("/top-students")
def get_top_students(limit: int = 5, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    top = db.query(
        Student.id,
        Student.full_name,
        func.count(Attendance.id).label("attendance_count")
    ).outerjoin(Attendance).group_by(Student.id).order_by(
        func.count(Attendance.id).desc()
    ).limit(limit).all()

    return [
        {"id": id, "name": name, "attendance": count}
        for id, name, count in top
    ]
