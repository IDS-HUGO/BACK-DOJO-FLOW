from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=list[PaymentRead])
def list_payments(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    return db.query(Payment).order_by(Payment.id.desc()).all()


@router.post("", response_model=PaymentRead)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    payment = Payment(**payload.model_dump(), status="paid")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
