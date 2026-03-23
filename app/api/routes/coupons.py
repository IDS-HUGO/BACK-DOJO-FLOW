from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.coupon import Coupon
from app.models.user import User
from app.schemas.coupon import CouponCreate, CouponRead

router = APIRouter(prefix="/coupons", tags=["coupons"])


@router.get("/", response_model=list[CouponRead])
def get_coupons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    coupons = db.query(Coupon).filter(Coupon.active == True).all()
    return coupons


@router.post("/", response_model=CouponRead)
def create_coupon(coupon: CouponCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_coupon = Coupon(**coupon.model_dump())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


@router.get("/validate/{code}")
def validate_coupon(code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    coupon = db.query(Coupon).filter(Coupon.code == code, Coupon.active == True).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    from datetime import date
    if coupon.valid_until < date.today():
        raise HTTPException(status_code=400, detail="Coupon expired")
    
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    
    return {"discount_percent": coupon.discount_percent, "description": coupon.description}


@router.post("/use/{code}")
def use_coupon(code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    coupon = db.query(Coupon).filter(Coupon.code == code, Coupon.active == True).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    coupon.used_count += 1
    db.commit()
    db.refresh(coupon)
    return coupon


@router.put("/{coupon_id}", response_model=CouponRead)
def update_coupon(coupon_id: int, coupon: CouponCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    for key, value in coupon.model_dump().items():
        setattr(db_coupon, key, value)
    
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


@router.delete("/{coupon_id}")
def delete_coupon(coupon_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    db.delete(db_coupon)
    db.commit()
    return {"detail": "Coupon deleted"}
