from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.plan import Plan
from app.schemas.plan import PlanRead

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanRead])
def list_plans(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    return db.query(Plan).order_by(Plan.id.asc()).all()
