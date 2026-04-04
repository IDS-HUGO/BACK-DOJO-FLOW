import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.payment import Payment
from app.models.student import Student
from app.schemas.payment import (
    PayPalCheckoutCreate,
    PayPalCheckoutResponse,
    PayPalVerifyRequest,
    PaymentCreate,
    PaymentRead,
)

router = APIRouter(prefix="/payments", tags=["payments"])


def _paypal_request(
    method: str,
    path: str,
    access_token: str,
    payload: dict | None = None,
) -> dict:
    url = f"{settings.paypal_base_url.rstrip('/')}{path}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url=url, data=body, method=method)
    request.add_header("Authorization", f"Bearer {access_token}")
    request.add_header("Content-Type", "application/json")

    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = exc.read().decode("utf-8") if exc.fp else str(exc)
        raise HTTPException(status_code=502, detail=f"PayPal error: {details}") from exc
    except URLError as exc:
        raise HTTPException(status_code=502, detail="No fue posible conectar con PayPal") from exc


def _paypal_access_token() -> str:
    if not settings.paypal_client_id or not settings.paypal_client_secret:
        raise HTTPException(status_code=503, detail="PayPal no configurado en el servidor")

    credentials = f"{settings.paypal_client_id}:{settings.paypal_client_secret}".encode("utf-8")
    encoded = base64.b64encode(credentials).decode("utf-8")
    url = f"{settings.paypal_base_url.rstrip('/')}/v1/oauth2/token"
    body = b"grant_type=client_credentials"

    request = Request(url=url, data=body, method="POST")
    request.add_header("Authorization", f"Basic {encoded}")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            token = data.get("access_token")
            if not token:
                raise HTTPException(status_code=502, detail="PayPal no devolvio access token")
            return str(token)
    except HTTPError as exc:
        details = exc.read().decode("utf-8") if exc.fp else str(exc)
        raise HTTPException(status_code=502, detail=f"PayPal auth error: {details}") from exc
    except URLError as exc:
        raise HTTPException(status_code=502, detail="No fue posible autenticar con PayPal") from exc


@router.get("", response_model=list[PaymentRead])
def list_payments(
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    student = db.query(Student).filter(Student.email == _current_user.email).first()
    query = db.query(Payment)
    if student:
        query = query.filter(Payment.student_id == student.id)
    return query.order_by(Payment.id.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=PaymentRead)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.email == current_user.email).first()
    if student and payload.student_id != student.id:
        raise HTTPException(status_code=403, detail="No puedes registrar pagos de otro alumno")

    payment = Payment(**payload.model_dump(), status="paid")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/checkout/paypal", response_model=PayPalCheckoutResponse)
def create_paypal_checkout(
    payload: PayPalCheckoutCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.email == current_user.email).first()
    if student and payload.student_id != student.id:
        raise HTTPException(status_code=403, detail="No puedes generar checkout de otro alumno")

    payment = Payment(
        student_id=payload.student_id,
        amount=payload.amount,
        method="paypal",
        status="pending",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    access_token = _paypal_access_token()
    success_url = payload.success_url or settings.paypal_success_url
    cancel_url = payload.cancel_url or settings.paypal_cancel_url

    order_payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "MXN",
                    "value": f"{payload.amount:.2f}",
                },
                "description": payload.description or f"Pago de alumno #{payload.student_id}",
                "custom_id": str(payment.id),
            }
        ],
        "application_context": {
            "return_url": success_url,
            "cancel_url": cancel_url,
            "user_action": "PAY_NOW",
        },
    }

    order = _paypal_request("POST", "/v2/checkout/orders", access_token, order_payload)
    order_id = order.get("id")
    links = order.get("links", [])
    approve_link = next((link.get("href") for link in links if link.get("rel") == "approve"), None)

    if not order_id or not approve_link:
        raise HTTPException(status_code=502, detail="PayPal no devolvio datos de checkout")

    return PayPalCheckoutResponse(payment_id=payment.id, order_id=str(order_id), checkout_url=str(approve_link))


@router.post("/checkout/paypal/me", response_model=PayPalCheckoutResponse)
def create_my_paypal_checkout(
    payload: PayPalCheckoutCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.email == current_user.email).first()
    if not student:
        raise HTTPException(status_code=403, detail="Solo alumnos pueden usar este endpoint")

    secured_payload = PayPalCheckoutCreate(
        student_id=student.id,
        amount=payload.amount,
        description=payload.description,
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
    )
    return create_paypal_checkout(secured_payload, db, current_user)


@router.post("/paypal/verify", response_model=PaymentRead)
def verify_paypal_payment(
    payload: PayPalVerifyRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    access_token = _paypal_access_token()
    order = _paypal_request("GET", f"/v2/checkout/orders/{payload.order_id}", access_token)
    order_status = str(order.get("status", "")).upper()

    if order_status == "APPROVED":
        capture = _paypal_request("POST", f"/v2/checkout/orders/{payload.order_id}/capture", access_token)
    else:
        capture = order

    purchase_units = capture.get("purchase_units", [])
    payment_reference = None
    if purchase_units:
        payment_reference = purchase_units[0].get("custom_id")

    if not payment_reference or not str(payment_reference).isdigit():
        raise HTTPException(status_code=400, detail="No se encontro referencia interna del pago")

    payment = db.query(Payment).filter(Payment.id == int(payment_reference)).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Pago interno no encontrado")

    student = db.query(Student).filter(Student.email == current_user.email).first()
    if student and payment.student_id != student.id:
        raise HTTPException(status_code=403, detail="No puedes verificar pagos de otro alumno")

    capture_status = str(capture.get("status", "")).upper()
    if capture_status == "COMPLETED":
        payment.status = "paid"
    elif capture_status in {"VOIDED", "FAILED", "DENIED"}:
        payment.status = "failed"
    else:
        payment.status = "pending"

    payment.method = "paypal"
    db.commit()
    db.refresh(payment)
    return payment
