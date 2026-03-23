from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate, AttendanceRead

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("", response_model=list[AttendanceRead])
def list_attendance(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    return db.query(Attendance).order_by(Attendance.id.desc()).all()


@router.post("", response_model=AttendanceRead)
def create_attendance(
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    attendance = Attendance(**payload.model_dump())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance
