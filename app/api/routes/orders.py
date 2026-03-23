from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import string

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.plan import Plan
from app.models.user import User
from app.core.security import create_password_hash
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse, OrderCheckout

router = APIRouter(prefix="/orders", tags=["orders"])


def generate_password(length: int = 12) -> str:
    """Generate a random secure password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(chars) for _ in range(length))


@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new purchase order. Public endpoint."""
    
    # Verify plan exists
    plan = db.query(Plan).filter(Plan.id == order.plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    # Check if email already has an order
    existing = db.query(Order).filter(Order.owner_email == order.owner_email).first()
    if existing and existing.status in [OrderStatus.PAID, OrderStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email already has an active order"
        )
    
    # Create order
    db_order = Order(
        plan_id=order.plan_id,
        dojo_name=order.dojo_name,
        owner_name=order.owner_name,
        owner_email=order.owner_email,
        owner_phone=order.owner_phone,
        city=order.city,
        timezone=order.timezone,
        currency=order.currency,
        amount=plan.monthly_price,
        status=OrderStatus.PENDING,
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return OrderResponse.from_orm(db_order)


@router.post("/{order_id}/checkout", response_model=dict)
def checkout_order(order_id: int, db: Session = Depends(get_db)):
    """
    Simulate a Stripe checkout session creation.
    In production, this would integrate with Stripe SDK.
    """
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order status is {order.status}, cannot checkout"
        )
    
    # Mock Stripe session (in production, call Stripe API)
    # For demo: return a mock checkout URL
    checkout_url = f"https://stripe-mock.example.com/checkout/{order_id}?session_id=cs_mock_{order_id}"
    
    return {
        "order_id": order_id,
        "checkout_url": checkout_url,
        "message": "To complete payment in production, use Stripe checkout. For testing, call /orders/{order_id}/confirm-payment",
    }


@router.post("/{order_id}/confirm-payment", response_model=OrderResponse)
def confirm_payment(order_id: int, db: Session = Depends(get_db)):
    """
    Confirm payment and generate credentials.
    In production, this would be triggered by Stripe webhook.
    For testing/demo, this endpoint simulates successful payment.
    """
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_found, detail="Order not found")
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order already {order.status}"
        )
    
    # Mark as paid
    order.status = OrderStatus.PAID
    order.paid_at = datetime.utcnow()
    order.transaction_id = f"txn_mock_{order_id}_{int(datetime.utcnow().timestamp())}"
    
    # Generate credentials
    generated_email = f"dojo_{order_id}@dojoflow.local"
    generated_password = generate_password()
    
    order.generated_email = generated_email
    order.generated_password = generated_password
    order.credentials_sent_at = datetime.utcnow()
    
    # Create user account
    existing_user = db.query(User).filter(User.email == generated_email).first()
    if not existing_user:
        db_user = User(
            email=generated_email,
            full_name=order.owner_name,
            hashed_password=create_password_hash(generated_password),
            is_active=True,
        )
        db.add(db_user)
    
    db.commit()
    db.refresh(order)
    
    return OrderResponse.from_orm(order)


@router.get("/", response_model=list[OrderListResponse])
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all orders (admin only - user must be owner@dojoflow.com)."""
    
    if current_user.email != "owner@dojoflow.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can list orders")
    
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return [OrderListResponse.from_orm(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order status by ID (public for order tracking)."""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    return OrderResponse.from_orm(order)


@router.get("/status/{email}", response_model=OrderResponse | dict)
def get_order_by_email(email: str, db: Session = Depends(get_db)):
    """Get order status by email (public for tracking)."""
    
    order = db.query(Order).filter(Order.owner_email == email).order_by(Order.created_at.desc()).first()
    
    if not order:
        return {"message": "No order found for this email"}
    
    return OrderResponse.from_orm(order)
