from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.belt_progress import BeltProgress
from app.schemas.belt import BeltCreate, BeltRead

router = APIRouter(prefix="/belts", tags=["belts"])


@router.get("", response_model=list[BeltRead])
def list_belts(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    return db.query(BeltProgress).order_by(BeltProgress.id.desc()).all()


@router.post("", response_model=BeltRead)
def create_belt(
    payload: BeltCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    belt = BeltProgress(**payload.model_dump(), approved=payload.exam_score >= 70)
    db.add(belt)
    db.commit()
    db.refresh(belt)
    return belt
