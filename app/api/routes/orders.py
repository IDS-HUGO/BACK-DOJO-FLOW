import base64
import json
from urllib.request import Request as UrllibRequest, urlopen
from urllib.error import HTTPError
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Union
import secrets
import string
import logging

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.plan import Plan
from app.models.user import User
from app.core.security import create_password_hash
from app.core.config import settings
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse, OrderCheckout
from app.core.mailer import send_dojo_credentials_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


def generate_password(length: int = 12) -> str:
    """Generate a random secure password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(chars) for _ in range(length))


# =========================
# 🔹 PAYPAL - TOKEN
# =========================
def get_paypal_token():
    credentials = f"{settings.paypal_client_id}:{settings.paypal_client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()

    try:
        req = UrllibRequest(
            f"{settings.paypal_base_url}/v1/oauth2/token",
            data=b"grant_type=client_credentials",
            method="POST",
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        with urlopen(req) as res:
                    data = json.loads(res.read().decode())
                    return data["access_token"]
    except HTTPError as e:
                error_body = e.read().decode()
                logger.error(f"PayPal token error: {e.code} - {error_body}")
                raise HTTPException(status_code=500, detail=f"PayPal token error: {error_body}")
    except Exception as e:
                logger.error(f"Unexpected error getting PayPal token: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Token error: {str(e)}")


@router.post("", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new purchase order. Public endpoint."""
    
    logger.info(f"🔹 CREATE_ORDER START - Email: {order.owner_email}, Plan: {order.plan_id}")
    
    # Verify plan exists
    plan = db.query(Plan).filter(Plan.id == order.plan_id).first()
    if not plan:
        logger.error(f"❌ Plan {order.plan_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    logger.info(f"✅ Plan found: {plan.name}, price: {plan.monthly_price}")
    
    # Check if email already has an ACTIVE order (PENDING or PAID)
    existing = db.query(Order).filter(
        Order.owner_email == order.owner_email,
        Order.status.in_([OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.COMPLETED])
    ).first()
    
    if existing:
        logger.warning(f"⚠️ Email {order.owner_email} already has active order")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This email already has an active order"
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
        status=OrderStatus.PENDING if plan.monthly_price > 0 else OrderStatus.COMPLETED,
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    logger.info(f"📋 Order created: ID={db_order.id}, Status={db_order.status}, Amount={db_order.amount}")
    
    # ✅ SI ES PLAN GRATIS, GENERAR CREDENCIALES Y ENVIAR EMAIL
    if plan.monthly_price == 0:
        logger.info(f"🎁 FREE PLAN DETECTED - Generating credentials...")
        
        generated_email = f"dojo_{db_order.id}@dojoflow.local"
        generated_password = generate_password()
        
        logger.info(f"🔐 Generated email: {generated_email}")
        logger.info(f"🔐 Generated password: {generated_password}")
        
        db_order.generated_email = generated_email
        db_order.generated_password = generated_password
        db_order.credentials_sent_at = datetime.utcnow()
        
        # Create user account
        db_user = User(
            email=generated_email,
            full_name=order.owner_name,
            hashed_password=create_password_hash(generated_password),
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_order)
        
        logger.info(f"👤 User account created: {generated_email}")
        
        # ✅ Enviar email con credenciales
        logger.info(f"📧 SENDING EMAIL to {order.owner_email}...")
        logger.info(f"   - Dojo Email: {generated_email}")
        logger.info(f"   - Dojo Name: {order.dojo_name}")
        
        try:
            result = send_dojo_credentials_email(
                to_email=order.owner_email,
                dojo_email=generated_email,
                password=generated_password,
                dojo_name=order.dojo_name
            )
            logger.info(f"✅ EMAIL SENT SUCCESSFULLY: {result}")
        except Exception as e:
            logger.error(f"❌ ERROR SENDING EMAIL: {str(e)}", exc_info=True)
    
    logger.info(f"✅ Order created successfully: {db_order.id}")
    
    return OrderResponse.from_orm(db_order)
# =========================
# 🔹 PAYPAL CHECKOUT - Solo para planes pagos
# =========================
@router.post("/{order_id}/checkout")
def checkout_order(order_id: int, db: Session = Depends(get_db)):
    """Create PayPal checkout for order. Ruta: POST /api/v1/orders/{order_id}/checkout"""
    
    try:
        logger.info(f"Starting checkout for order {order_id}")
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.warning(f"Order {order_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        logger.info(f"Order found: {order.id}, status: {order.status}, amount: {order.amount}")
        
        # ✅ BLOQUEAMOS PLANES GRATIS
        if order.amount <= 0:
            logger.error(f"Order {order_id} is free plan - cannot checkout")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Free plans do not require payment"
            )
        
        # Solo órdenes PENDING pueden hacer checkout
        if order.status != OrderStatus.PENDING:
            logger.warning(f"Order {order_id} status is {order.status}, cannot checkout")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order status is {order.status}, cannot checkout"
            )
        
        logger.info("Getting PayPal token...")
        token = get_paypal_token()
        logger.info("Token obtained successfully")

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": order.currency,
                        "value": f"{order.amount:.2f}"
                    },
                    "custom_id": str(order.id),
                    "description": f"DojoFlow Plan - {order.dojo_name}",
                }
            ],
            "application_context": {
                "return_url": f"http://localhost:5173/orders/{order_id}/success",
                "cancel_url": f"http://localhost:5173/orders/{order_id}/cancel",
                "brand_name": "DojoFlow",
                "locale": "es-MX",
                "user_action": "PAY_NOW",
            },
        }

        logger.info(f"Sending payload to PayPal: {json.dumps(payload, indent=2)}")

        req = UrllibRequest(
            f"{settings.paypal_base_url}/v2/checkout/orders",
            data=json.dumps(payload).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        with urlopen(req) as res:
            paypal_order = json.loads(res.read().decode())

        logger.info(f"PayPal response: {json.dumps(paypal_order, indent=2)}")

        approve_url = next(
            (link["href"] for link in paypal_order.get("links", []) if link.get("rel") == "approve"),
            None
        )
        
        if not approve_url:
            logger.error(f"No approve link found in PayPal response: {paypal_order}")
            raise HTTPException(status_code=500, detail="No approve link in PayPal response")

        logger.info(f"Checkout successful. PayPal Order ID: {paypal_order.get('id')}")

        return {
            "order_id": order_id,
            "paypal_order_id": paypal_order["id"],
            "checkout_url": approve_url,
            "message": "Redirecting to PayPal checkout"
        }
    except HTTPException:
        raise
    except HTTPError as e:
        error_body = e.read().decode()
        logger.error(f"PayPal HTTP Error {e.code}: {error_body}")
        raise HTTPException(status_code=500, detail=f"PayPal error: {error_body}")
    except Exception as e:
        logger.error(f"Unexpected error in checkout: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ...rest of code...

# =========================
# 🔹 PAYPAL CAPTURE
# =========================

@router.post("/{order_id}/confirm-payment")
def confirm_payment(
    order_id: int,
    paypal_order_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Capture PayPal payment and generate credentials. Ruta: POST /api/v1/orders/{order_id}/confirm-payment"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order already {order.status}"
        )
    
    token = get_paypal_token()

    try:
        req = UrllibRequest(
            f"{settings.paypal_base_url}/v2/checkout/orders/{paypal_order_id}/capture",
            data=b"",
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        with urlopen(req) as res:
            capture = json.loads(res.read().decode())

        if capture.get("status") != "COMPLETED":
            raise HTTPException(status_code=400, detail="PayPal payment not completed")

        # Mark as paid
        order.status = OrderStatus.PAID
        order.paid_at = datetime.utcnow()
        order.transaction_id = paypal_order_id

        # Generate credentials
        generated_email = f"dojo_{order.id}@dojoflow.local"
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

        # ✅ ENVIAR EMAIL CON CREDENCIALES
        email_sent = send_dojo_credentials_email(
            to_email=order.owner_email,
            dojo_email=generated_email,
            password=generated_password,
            dojo_name=order.dojo_name
        )

        return {
            "status": "success",
            "message": "Payment completed and credentials generated",
            "order": OrderResponse.from_orm(order),
            "credentials": {
                "email": generated_email,
                "password": generated_password,
            },
            "email_sent": email_sent
        }
    except HTTPError as e:
        error_body = e.read().decode()
        raise HTTPException(status_code=500, detail=f"PayPal capture error: {error_body}")

@router.get("", response_model=List[OrderListResponse])
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all orders (admin only). Ruta: GET /api/v1/orders"""
    
    if current_user.email != "owner@dojoflow.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can list orders")
    
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return [OrderListResponse.from_orm(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order status by ID (public for order tracking). Ruta: GET /api/v1/orders/{order_id}"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    return OrderResponse.from_orm(order)


@router.get("/status/{email}", response_model=Union[OrderResponse, dict])
def get_order_by_email(email: str, db: Session = Depends(get_db)):
    """Get order status by email (public for tracking). Ruta: GET /api/v1/orders/status/{email}"""
    
    order = db.query(Order).filter(Order.owner_email == email).order_by(Order.created_at.desc()).first()
    
    if not order:
        return {"message": "No order found for this email"}
    
    return OrderResponse.from_orm(order)