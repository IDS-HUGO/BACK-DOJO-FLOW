import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.mailer import send_password_reset_email
from app.core.security import create_access_token, create_password_hash, verify_password
from app.db.session import get_db
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
    Token,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


def _create_password_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.reset_password_expire_minutes)
    payload = {"sub": email, "exp": expire, "purpose": "password_reset"}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def _decode_password_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        if payload.get("purpose") != "password_reset":
            raise HTTPException(status_code=400, detail="Token inválido")
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=400, detail="Token inválido")
        return str(subject)
    except JWTError as exc:
        raise HTTPException(status_code=400, detail="Token inválido o expirado") from exc


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint that distinguishes between dojo owner, teacher, and student."""
    
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"❌ Login failed for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    
    # ✅ DIFERENCIAR ROLES
    # Primero verificar si es estudiante
    student = db.query(Student).filter(Student.email == user.email).first()
    if student:
        logger.info(f"✅ Login student: {user.email} (ID: {student.id})")
        return Token(
            access_token=access_token, 
            account_type="student", 
            student_id=student.id
        )
    
    # Luego verificar si es instructor/teacher
    teacher = db.query(Teacher).filter(Teacher.email == user.email).first()
    if teacher:
        logger.info(f"✅ Login teacher: {user.email} (ID: {teacher.id})")
        return Token(
            access_token=access_token, 
            account_type="teacher", 
            student_id=None
        )
    
    # Si no es ni estudiante ni instructor, es dojo owner
    logger.info(f"✅ Login dojo owner: {user.email}")
    return Token(
        access_token=access_token, 
        account_type="dojo", 
        student_id=None
    )


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        token = _create_password_reset_token(user.email)
        reset_link = f"{settings.frontend_base_url}/reset-password?token={token}"
        try:
            send_password_reset_email(
                to_email=user.email,
                user_name=user.full_name,
                reset_link=reset_link,
            )
        except Exception:
            pass

    return MessageResponse(message="Si el correo existe, enviamos instrucciones para recuperar la contraseña")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = _decode_password_reset_token(payload.token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.hashed_password = create_password_hash(payload.new_password)
    db.commit()
    return MessageResponse(message="Contraseña actualizada correctamente")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    user.hashed_password = create_password_hash(payload.new_password)
    db.commit()
    return MessageResponse(message="Contraseña cambiada correctamente")