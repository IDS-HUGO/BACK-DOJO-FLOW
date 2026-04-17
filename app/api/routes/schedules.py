from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.schedule import Schedule
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.models.academy_profile import AcademyProfile
from app.models.order import Order, OrderStatus
from app.models.plan import Plan
from app.schemas.schedule import ScheduleCreate, ScheduleRead, ScheduleResponse, EnrollStudentRequest
from pydantic import BaseModel

router = APIRouter(prefix="/schedules", tags=["schedules"])

# Constantes
BASIC_PLAN_ID = 1
BASIC_PLAN_CAPACITY = 15
UNLIMITED_CAPACITY = 999
FREE_PLAN_ID = 1


def get_dojo_owner_profile(current_user: User, db: Session) -> Optional[AcademyProfile]:
    if current_user.email == "owner@dojoflow.com":
        return None

    profile = db.query(AcademyProfile).filter(
        AcademyProfile.user_id == current_user.id
    ).first()

    if profile:
        return profile

    order = db.query(Order).filter(
        Order.owner_email == current_user.email,
        Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED])
    ).first()

    if order:
        profile = AcademyProfile(
            user_id=current_user.id,
            dojo_name=order.dojo_name,
            owner_name=order.owner_name,
            contact_email=current_user.email,
            contact_phone=order.owner_phone,
            city=order.city,
            timezone=order.timezone,
            currency=order.currency,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    profile = AcademyProfile(
        user_id=current_user.id,
        dojo_name=f"Mi Dojo - {current_user.full_name}",
        owner_name=current_user.full_name,
        contact_email=current_user.email,
        contact_phone="",
        city="",
        timezone="America/Mexico_City",
        currency="USD",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_dojo_plan(db: Session, profile: AcademyProfile, current_user: User) -> Optional[Plan]:
    order = db.query(Order).filter(
        Order.owner_email == current_user.email
    ).order_by(Order.created_at.desc()).first()

    if order:
        return db.query(Plan).filter(Plan.id == order.plan_id).first()

    return db.query(Plan).filter(Plan.id == FREE_PLAN_ID).first()


def get_max_capacity(plan: Optional[Plan]) -> int:
    if not plan:
        return BASIC_PLAN_CAPACITY
    if plan.id == BASIC_PLAN_ID:
        return BASIC_PLAN_CAPACITY
    return UNLIMITED_CAPACITY


# ─── 1. RUTAS ESTÁTICAS ────────────────────────────────────────────────────────

@router.get("/", response_model=List[ScheduleResponse])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot use this endpoint")

    schedules = db.query(Schedule).filter(
        Schedule.academy_id == profile.id
    ).all()

    result = []
    for s in schedules:
        start_time_str = str(s.start_time) if s.start_time is not None else "00:00:00"
        end_time_str = str(s.end_time) if s.end_time is not None else "00:00:00"
        result.append({
            "id": s.id,
            "class_type": s.class_type,
            "day_of_week": s.day_of_week,
            "start_time": start_time_str,
            "end_time": end_time_str,
            "max_students": s.max_students,
            "active": s.active,
            "students": [{"id": st.id, "full_name": st.full_name, "email": st.email} for st in s.students],
            "teachers": [{"id": t.id, "name": t.name} for t in s.teachers],
        })
    return result


@router.post("/", response_model=ScheduleResponse)
def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot use this endpoint")

    plan = get_dojo_plan(db, profile, current_user)
    max_capacity = get_max_capacity(plan)

    db_schedule = Schedule(
        class_type=schedule_data.class_type,
        day_of_week=schedule_data.day_of_week,
        start_time=str(schedule_data.start_time),
        end_time=str(schedule_data.end_time),
        active=schedule_data.active,
        academy_id=profile.id,
        max_students=max_capacity
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    start_time_str = str(db_schedule.start_time) if db_schedule.start_time is not None else "00:00:00"
    end_time_str = str(db_schedule.end_time) if db_schedule.end_time is not None else "00:00:00"

    return {
        "id": db_schedule.id,
        "class_type": db_schedule.class_type,
        "day_of_week": db_schedule.day_of_week,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "max_students": db_schedule.max_students,
        "active": db_schedule.active,
        "students": [],
        "teachers": [],
    }


# ─── 2. RUTAS DINÁMICAS CON SUB-PATH (van ANTES que /{schedule_id} simple) ────

@router.post("/{schedule_id}/enroll-student", response_model=dict)
def enroll_student(
    schedule_id: int,
    request: EnrollStudentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot use this endpoint")

    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.academy_id == profile.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    student = db.query(Student).filter(
        Student.id == request.student_id,
        Student.academy_id == profile.id
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    already_enrolled = any(s.id == student.id for s in schedule.students)
    if already_enrolled:
        raise HTTPException(status_code=400, detail="Student already enrolled")

    current_students = len(schedule.students)
    max_cap: int = getattr(schedule, 'max_students', None) or BASIC_PLAN_CAPACITY

    if current_students >= max_cap:
        raise HTTPException(
            status_code=400,
            detail=f"Schedule is full ({current_students}/{max_cap} students)"
        )

    schedule.students.append(student)
    db.commit()
    db.refresh(schedule)

    return {
        "message": "Student enrolled successfully",
        "schedule_id": schedule.id,
        "student_id": student.id,
        "current_students": len(schedule.students),
        "max_capacity": max_cap
    }


@router.delete("/{schedule_id}/unenroll-student/{student_id}", response_model=dict)
def unenroll_student(
    schedule_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot use this endpoint")

    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.academy_id == profile.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student or student not in schedule.students:
        raise HTTPException(status_code=404, detail="Student not enrolled")

    schedule.students.remove(student)
    db.commit()
    return {"message": "Student unenrolled successfully"}


@router.post("/{schedule_id}/assign-teacher", response_model=dict)
def assign_teacher(
    schedule_id: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot use this endpoint")

    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.academy_id == profile.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    teacher = db.query(Teacher).filter(
        Teacher.id == request["teacher_id"],
        Teacher.academy_id == profile.id
    ).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher not in schedule.teachers:
        schedule.teachers.append(teacher)
        db.commit()

    return {"message": "Teacher assigned successfully"}


@router.delete("/{schedule_id}/remove-teacher/{teacher_id}", response_model=dict)
def remove_teacher(
    schedule_id: int,
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot use this endpoint")

    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.academy_id == profile.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher or teacher not in schedule.teachers:
        raise HTTPException(status_code=404, detail="Teacher not assigned")

    schedule.teachers.remove(teacher)
    db.commit()
    return {"message": "Teacher removed successfully"}


# ─── 3. RUTAS DINÁMICAS SIMPLES (siempre AL FINAL) ────────────────────────────

@router.delete("/{schedule_id}", response_model=dict)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot use this endpoint")

    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.academy_id == profile.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}