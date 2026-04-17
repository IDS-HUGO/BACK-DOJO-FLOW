import base64
import json
from urllib.request import Request as UrllibRequest, urlopen
from urllib.error import HTTPError

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.payment import Payment
from app.models.student import Student
from app.schemas.payment import PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])


# =========================
# 🔹 LISTAR PAGOS
# =========================
@router.get("", response_model=list[PaymentRead])
def list_payments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    student = db.query(Student).filter(Student.email == current_user.email).first()
    query = db.query(Payment)

    if student:
        query = query.filter(Payment.student_id == student.id)

    return query.order_by(Payment.id.desc()).offset(offset).limit(limit).all()


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
        raise HTTPException(status_code=500, detail=f"PayPal token error: {error_body}")


# =========================
# 🔹 CHECKOUT PAYPAL
# =========================
@router.post("/checkout")
def checkout(
    amount: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.email == current_user.email).first()
    if not student:
        raise HTTPException(status_code=403, detail="Solo alumnos pueden pagar")

    token = get_paypal_token()

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "MXN",
                    "value": f"{amount:.2f}"
                },
                "custom_id": str(student.id),
                "description": f"Pago DulceMomento - Estudiante {student.id}",
            }
        ],
        "application_context": {
            "return_url": "http://localhost:5173/app/payments",
            "cancel_url": "http://localhost:5173/app/payments",
            "brand_name": "DulceMomento",
            "locale": "es-MX",
            "user_action": "PAY_NOW",
        },
    }

    try:
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
            order = json.loads(res.read().decode())

        approve_url = next(link["href"] for link in order["links"] if link["rel"] == "approve")

        return {
            "provider": "paypal",
            "url": approve_url,
            "order_id": order["id"],
        }
    except HTTPError as e:
        error_body = e.read().decode()
        raise HTTPException(status_code=500, detail=f"PayPal checkout error: {error_body}")


# =========================
# 🔹 CAPTURAR PAGO PAYPAL
# =========================
@router.post("/paypal/capture")
def capture_paypal(
    order_id: str = Query(...),
    db: Session = Depends(get_db),
):
    token = get_paypal_token()

    try:
        req = UrllibRequest(
            f"{settings.paypal_base_url}/v2/checkout/orders/{order_id}/capture",
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
            raise HTTPException(status_code=400, detail="Pago no completado")

        purchase = capture["purchase_units"][0]["payments"]["captures"][0]

        student_id = purchase["custom_id"]
        amount = float(purchase["amount"]["value"])

        existing = db.query(Payment).filter_by(external_id=order_id).first()
        if existing:
            return {"status": "exists", "message": "Pago ya fue registrado"}

        payment = Payment(
            student_id=int(student_id),
            amount=amount,
            status="approved",
            method="paypal",
            external_id=order_id,
        )

        db.add(payment)
        db.commit()

        return {"status": "ok", "message": "Pago registrado correctamente"}
    except HTTPError as e:
        error_body = e.read().decode()
        raise HTTPException(status_code=500, detail=f"PayPal capture error: {error_body}")