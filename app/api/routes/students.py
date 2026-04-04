import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.mailer import send_student_credentials_email
from app.core.security import create_password_hash
from app.db.session import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentCreateResponse, StudentRead

router = APIRouter(prefix="/students", tags=["students"])


def _generate_temporary_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.get("", response_model=list[StudentRead])
def list_students(
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    return db.query(Student).order_by(Student.id.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=StudentCreateResponse)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    existing_student = db.query(Student).filter(Student.email == payload.email).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un alumno con ese correo",
        )

    student = Student(**payload.model_dump())
    temporary_password = _generate_temporary_password()

    existing_user = db.query(User).filter(User.email == payload.email).first()
    if not existing_user:
        db.add(
            User(
                email=payload.email,
                full_name=payload.full_name,
                hashed_password=create_password_hash(temporary_password),
                is_active=True,
            )
        )

    db.add(student)
    db.commit()
    db.refresh(student)

    credentials_email_sent = True
    try:
        send_student_credentials_email(
            to_email=payload.email,
            student_name=payload.full_name,
            login_email=payload.email,
            temporary_password=temporary_password,
        )
    except Exception:
        credentials_email_sent = False

    return StudentCreateResponse(
        **StudentRead.model_validate(student).model_dump(),
        credentials_email_sent=credentials_email_sent,
    )


@router.get("/me", response_model=StudentRead)
def get_current_student_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.email == current_user.email).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de alumno no encontrado")
    return student
