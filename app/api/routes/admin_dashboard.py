"""
Admin Dashboard endpoints for managing DojoFlow system.
Only accessible to admin users (owner@dojoflow.com).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.plan import Plan
from app.schemas.order import OrderListResponse, OrderResponse

router = APIRouter(prefix="/admin", tags=["admin"])


def verify_admin(current_user: User) -> User:
    """Verify that current user is an admin."""
    if current_user.email != "owner@dojoflow.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )
    return current_user


@router.get("/dashboard", tags=["admin"])
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get admin dashboard statistics."""
    verify_admin(current_user)
    
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    paid_orders = db.query(Order).filter(Order.status == OrderStatus.PAID).count()
    completed_orders = db.query(Order).filter(Order.status == OrderStatus.COMPLETED).count()
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Revenue calculation
    total_revenue = 0
    paid_order_list = db.query(Order).filter(Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED])).all()
    for order in paid_order_list:
        total_revenue += order.amount
    
    return {
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "paid": paid_orders,
            "completed": completed_orders,
        },
        "users": {
            "total": total_users,
            "active": active_users,
        },
        "revenue": {
            "total": total_revenue,
            "currency": "MXN"
        }
    }


@router.get("/orders", response_model=List[OrderListResponse], tags=["admin"])
def get_all_orders(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all orders with optional status filter."""
    verify_admin(current_user)
    
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return [OrderListResponse.from_orm(o) for o in orders]


@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["admin"])
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed order information."""
    verify_admin(current_user)
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    return OrderResponse.from_orm(order)


@router.patch("/orders/{order_id}/status", tags=["admin"])
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update order status manually."""
    verify_admin(current_user)
    
    # Validate status
    valid_statuses = [s.value for s in OrderStatus]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    return OrderResponse.from_orm(order)


@router.get("/users", tags=["admin"])
def list_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users in the system."""
    verify_admin(current_user)
    
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "created_at": u.created_at,
        }
        for u in users
    ]


@router.get("/users/{user_id}", tags=["admin"])
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed user information."""
    verify_admin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Get user's order if they are a dojo owner
    order = db.query(Order).filter(Order.owner_email == user.email).first()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "associated_order": OrderListResponse.from_orm(order) if order else None,
    }


@router.patch("/users/{user_id}/toggle-active", tags=["admin"])
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate or deactivate a user account."""
    verify_admin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "message": f"User {'activated' if user.is_active else 'deactivated'}"
    }


@router.get("/plans", tags=["admin"])
def list_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all available plans."""
    verify_admin(current_user)
    
    plans = db.query(Plan).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "monthly_price": p.monthly_price,
            "description": p.description,
        }
        for p in plans
    ]


@router.get("/revenue-report", tags=["admin"])
def get_revenue_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed revenue report by plan."""
    verify_admin(current_user)
    
    plans = db.query(Plan).all()
    report = {}
    
    for plan in plans:
        orders = db.query(Order).filter(
            Order.plan_id == plan.id,
            Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED])
        ).all()
        
        report[plan.name] = {
            "count": len(orders),
            "monthly_price": plan.monthly_price,
            "total_revenue": sum(o.amount for o in orders),
            "orders": [o.id for o in orders]
        }
    
    return report
