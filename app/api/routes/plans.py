import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.plan import Plan
from app.models.plan_subscription_payment import PlanSubscriptionPayment
from app.models.user import User
from app.schemas.plan import (
    PlanPayPalCheckoutCreate,
    PlanPayPalCheckoutResponse,
    PlanPayPalVerifyRequest,
    PlanRead,
    PlanSubscriptionPaymentRead,
)

router = APIRouter(prefix="/plans", tags=["plans"])


def _paypal_request(method: str, path: str, access_token: str, payload: dict | None = None) -> dict:
    url = f"{settings.paypal_base_url.rstrip('/')}{path}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url=url, data=body, method=method)
    request.add_header("Authorization", f"Bearer {access_token}")
    request.add_header("Content-Type", "application/json")

    try:
        with urlopen(request, timeout=20) as response:
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


@router.get("", response_model=list[PlanRead])
def list_plans(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    return db.query(Plan).order_by(Plan.id.asc()).all()


@router.post("/{plan_id}/checkout/paypal", response_model=PlanPayPalCheckoutResponse)
def create_plan_checkout(
    plan_id: int,
    payload: PlanPayPalCheckoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    access_token = _paypal_access_token()

    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    if plan.monthly_price <= 0:
        raise HTTPException(status_code=400, detail="Este plan no requiere pago en línea")

    subscription_payment = PlanSubscriptionPayment(
        user_id=current_user.id,
        plan_id=plan.id,
        amount=plan.monthly_price,
        status="pending",
        provider="paypal",
    )
    db.add(subscription_payment)
    db.commit()
    db.refresh(subscription_payment)

    order_payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "MXN",
                    "value": f"{plan.monthly_price:.2f}",
                },
                "description": f"Suscripcion DojoFlow - {plan.name}",
                "custom_id": str(subscription_payment.id),
            }
        ],
        "application_context": {
            "return_url": payload.success_url or settings.paypal_plan_success_url,
            "cancel_url": payload.cancel_url or settings.paypal_plan_cancel_url,
            "user_action": "PAY_NOW",
        },
    }

    order = _paypal_request("POST", "/v2/checkout/orders", access_token, order_payload)
    order_id = order.get("id")
    links = order.get("links", [])
    approve_link = next((link.get("href") for link in links if link.get("rel") == "approve"), None)

    if not order_id or not approve_link:
        raise HTTPException(status_code=502, detail="PayPal no devolvio datos de checkout")

    return PlanPayPalCheckoutResponse(
        subscription_payment_id=subscription_payment.id,
        order_id=str(order_id),
        checkout_url=str(approve_link),
    )


@router.post("/checkout/paypal/verify", response_model=PlanSubscriptionPaymentRead)
def verify_plan_checkout(
    payload: PlanPayPalVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    access_token = _paypal_access_token()
    order = _paypal_request("GET", f"/v2/checkout/orders/{payload.order_id}", access_token)
    order_status = str(order.get("status", "")).upper()

    if order_status == "APPROVED":
        capture = _paypal_request("POST", f"/v2/checkout/orders/{payload.order_id}/capture", access_token)
    else:
        capture = order

    purchase_units = capture.get("purchase_units", [])
    reference = None
    if purchase_units:
        reference = purchase_units[0].get("custom_id")

    if not reference or not str(reference).isdigit():
        raise HTTPException(status_code=400, detail="Referencia de suscripcion invalida")

    subscription_payment = (
        db.query(PlanSubscriptionPayment)
        .filter(PlanSubscriptionPayment.id == int(reference))
        .first()
    )
    if not subscription_payment:
        raise HTTPException(status_code=404, detail="Pago de suscripcion no encontrado")

    if subscription_payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes verificar pagos de otro usuario")

    capture_status = str(capture.get("status", "")).upper()
    if capture_status == "COMPLETED":
        subscription_payment.status = "paid"
    elif capture_status in {"VOIDED", "FAILED", "DENIED"}:
        subscription_payment.status = "failed"
    else:
        subscription_payment.status = "pending"

    subscription_payment.mp_payment_id = str(capture.get("id")) if capture.get("id") else None
    db.commit()
    db.refresh(subscription_payment)
    return subscription_payment
