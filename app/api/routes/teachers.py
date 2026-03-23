from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.teacher import TeacherCreate, TeacherRead

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.get("/", response_model=list[TeacherRead])
def get_teachers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    teachers = db.query(Teacher).all()
    return teachers


@router.post("/", response_model=TeacherRead)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_teacher = Teacher(**teacher.model_dump())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.put("/{teacher_id}", response_model=TeacherRead)
def update_teacher(teacher_id: int, teacher: TeacherCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    for key, value in teacher.model_dump().items():
        setattr(db_teacher, key, value)
    
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    db.delete(db_teacher)
    db.commit()
    return {"detail": "Teacher deleted"}
