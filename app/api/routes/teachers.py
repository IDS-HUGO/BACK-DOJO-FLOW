import logging
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes.schedules import get_dojo_owner_profile
from app.core.mailer import send_teacher_credentials_email
from app.core.security import create_password_hash
from app.db.session import get_db
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.teacher import TeacherCreate, TeacherRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/teachers", tags=["teachers"])


def _generate_temporary_password(length: int = 10) -> str:
    """Generate a temporary password for teachers."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.get("/", response_model=list[TeacherRead])
def get_teachers(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Listar instructores de la academia del usuario actual"""
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot list teachers")
    
    teachers = db.query(Teacher).filter(Teacher.academy_id == profile.id).all()
    return teachers


@router.post("/", response_model=TeacherRead)
def create_teacher(
    teacher: TeacherCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Crear un nuevo instructor asignando automáticamente academy_id"""
    # ✅ Obtener el perfil de la academia del usuario actual
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot create teachers")
    
    # ✅ Verificar que no exista un profesor con ese email
    existing_teacher = db.query(Teacher).filter(Teacher.email == teacher.email).first()
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un instructor con ese correo",
        )
    
    # ✅ Generar contraseña temporal
    temporary_password = _generate_temporary_password()
    
    # ✅ Crear profesor CON academy_id asignado
    db_teacher = Teacher(
        **teacher.model_dump(),
        academy_id=profile.id  # ← IMPORTANTE: Asignar automáticamente
    )
    
    # ✅ Crear usuario asociado (ANTES de hacer commit)
    existing_user = db.query(User).filter(User.email == teacher.email).first()
    if not existing_user:
        db.add(
            User(
                email=teacher.email,
                full_name=teacher.name,
                hashed_password=create_password_hash(temporary_password),
                is_active=True,
            )
        )
    
    # ✅ Agregar profesor
    db.add(db_teacher)
    
    # ✅ UN SOLO COMMIT para ambos
    db.commit()
    db.refresh(db_teacher)
    
    # ✅ Enviar email con credenciales
    credentials_email_sent = True
    try:
        send_teacher_credentials_email(
            to_email=teacher.email,
            teacher_name=teacher.name,
            login_email=teacher.email,
            temporary_password=temporary_password,
        )
    except Exception as e:
        logger.error(f"Error sending teacher credentials email: {str(e)}")
        credentials_email_sent = False
    
    return db_teacher


@router.put("/{teacher_id}", response_model=TeacherRead)
def update_teacher(
    teacher_id: int, 
    teacher: TeacherCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Actualizar un instructor"""
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot update teachers")
    
    db_teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.academy_id == profile.id
    ).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    for key, value in teacher.model_dump().items():
        setattr(db_teacher, key, value)
    
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.delete("/{teacher_id}")
def delete_teacher(
    teacher_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Eliminar un instructor"""
    profile = get_dojo_owner_profile(current_user, db)
    if not profile:
        raise HTTPException(status_code=403, detail="Admin cannot delete teachers")
    
    db_teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.academy_id == profile.id
    ).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # ✅ Eliminar también el usuario asociado
    db_user = db.query(User).filter(User.email == db_teacher.email).first()
    if db_user:
        db.delete(db_user)
    
    db.delete(db_teacher)
    db.commit()
    return {"detail": "Teacher deleted"}