from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.marketplace_item import MarketplaceItem
from app.schemas.marketplace_item import MarketplaceItemCreate, MarketplaceItemRead

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("", response_model=list[MarketplaceItemRead])
def list_items(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    return db.query(MarketplaceItem).order_by(MarketplaceItem.id.desc()).all()


@router.post("", response_model=MarketplaceItemRead)
def create_item(
    payload: MarketplaceItemCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    item = MarketplaceItem(**payload.model_dump(), active=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
