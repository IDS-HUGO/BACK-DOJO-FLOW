"""
Dojo Management endpoints for dojo owners.
Only accessible to users who have purchased a plan.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.academy_profile import AcademyProfile
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.schedule import Schedule

router = APIRouter(prefix="/dojo", tags=["dojo"])


def get_dojo_owner_profile(current_user: User, db: Session) -> Optional[AcademyProfile]:
    """
    Get the academy profile for the current dojo owner.
    Verifies that user has an active paid order.
    Returns None for admins.
    """
    
    # Check if this is admin (special case)
    if current_user.email == "owner@dojoflow.com":
        return None
    
    # Check if user has an active order
    order = db.query(Order).filter(
        Order.owner_email == current_user.email,
        Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED])
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need an active subscription to access dojo management"
        )
    
    # Try to find or create academy profile
    profile = db.query(AcademyProfile).filter(
        AcademyProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create new profile from order data
        profile = AcademyProfile(
            user_id=current_user.id,
            dojo_name=order.dojo_name,
            owner_name=order.owner_name,
            contact_email=current_user.email,
            contact_phone=order.owner_phone,
            city=order.city,
            timezone=order.timezone,
            currency=order.currency,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


@router.get("/me", tags=["dojo"])
def get_my_dojo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current dojo owner's academy profile."""
    
    profile = get_dojo_owner_profile(current_user, db)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot use this endpoint"
        )
    
    # Get associated order
    order = db.query(Order).filter(
        Order.owner_email == current_user.email
    ).order_by(Order.created_at.desc()).first()
    
    return {
        "academy": {
            "id": profile.id,
            "dojo_name": profile.dojo_name,
            "owner_name": profile.owner_name,
            "contact_email": profile.contact_email,
            "contact_phone": profile.contact_phone,
            "city": profile.city,
            "timezone": profile.timezone,
        },
        "subscription": {
            "order_id": order.id if order else None,
            "plan_id": order.plan_id if order else None,
            "status": order.status if order else None,
            "amount": order.amount if order else None,
            "joined_date": order.created_at.isoformat() if order else None,
        },
        "user": {
            "email": current_user.email,
            "name": current_user.full_name,
            "active": current_user.is_active,
        }
    }


@router.get("/students", tags=["dojo"])
def get_my_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all students in dojo owner's academy."""
    
    profile = get_dojo_owner_profile(current_user, db)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot use this endpoint"
        )
    
    students = db.query(Student).filter(
        Student.academy_id == profile.id
    ).all()
    
    return [
        {
            "id": s.id,
            "name": s.full_name,
            "email": s.email,
            "phone": s.phone,
            "belt_level": s.belt_level,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in students
    ]


@router.get("/teachers", tags=["dojo"])
def get_my_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all teachers in dojo owner's academy."""
    
    profile = get_dojo_owner_profile(current_user, db)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot use this endpoint"
        )
    
    teachers = db.query(Teacher).filter(
        Teacher.academy_id == profile.id
    ).all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "email": t.email,
            "phone": t.phone,
            "specialties": t.specialties,
            "hourly_rate": t.hourly_rate,
            "active": t.active,
        }
        for t in teachers
    ]


@router.get("/schedules", tags=["dojo"])
def get_my_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all class schedules in dojo owner's academy."""
    
    profile = get_dojo_owner_profile(current_user, db)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot use this endpoint"
        )
    
    schedules = db.query(Schedule).filter(
        Schedule.academy_id == profile.id
    ).all()
    
    return [
        {
            "id": s.id,
            "class_type": s.class_type,
            "day_of_week": s.day_of_week,
            "start_time": str(s.start_time),
            "end_time": str(s.end_time),
            "max_students": s.max_students,
            "active": s.active,
            "teachers": [{"id": t.id, "name": t.name} for t in s.teachers],
        }
        for s in schedules
    ]


@router.get("/stats", tags=["dojo"])
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get statistics for dojo owner's academy."""
    
    profile = get_dojo_owner_profile(current_user, db)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot use this endpoint"
        )
    
    total_students = db.query(Student).filter(
        Student.academy_id == profile.id
    ).count()
    active_students = db.query(Student).filter(
        Student.academy_id == profile.id,
        Student.status == "active"
    ).count()
    
    total_teachers = db.query(Teacher).filter(
        Teacher.academy_id == profile.id
    ).count()
    
    total_classes = db.query(Schedule).filter(
        Schedule.academy_id == profile.id
    ).count()
    
    return {
        "academy": profile.dojo_name,
        "students": {
            "total": total_students,
            "active": active_students,
        },
        "teachers": {
            "total": total_teachers,
        },
        "classes": {
            "total": total_classes,
        }
    }


@router.patch("/profile", tags=["dojo"])
def update_my_profile(
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update dojo owner's academy profile (limited fields)."""
    
    profile = get_dojo_owner_profile(current_user, db)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot use this endpoint"
        )
    
    # Allow updating only specific fields
    allowed_fields = ["contact_phone", "city", "timezone"]
    
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(profile, field, value)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update field: {field}"
            )
    
    db.commit()
    db.refresh(profile)
    
    return {
        "message": "Profile updated successfully",
        "academy": {
            "dojo_name": profile.dojo_name,
            "contact_phone": profile.contact_phone,
            "city": profile.city,
            "timezone": profile.timezone,
        }
    }