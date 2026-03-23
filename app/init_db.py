from sqlalchemy.orm import Session
from datetime import date, time

from app.core.security import create_password_hash
from app.db.session import SessionLocal, engine
from app.models.academy_profile import AcademyProfile
from app.models.base import Base
from app.models.coupon import Coupon
from app.models.marketplace_item import MarketplaceItem
from app.models.plan import Plan
from app.models.schedule import Schedule
from app.models.teacher import Teacher
from app.models.user import User


def seed_data(db: Session) -> None:
    existing_user = db.query(User).filter(User.email == "owner@dojoflow.com").first()
    if not existing_user:
        db.add(
            User(
                email="owner@dojoflow.com",
                full_name="Dojo Owner",
                hashed_password=create_password_hash("admin123"),
                is_active=True,
            )
        )

    existing_plans = db.query(Plan).count()
    if existing_plans == 0:
        db.add_all(
            [
                Plan(
                    name="Plan Blanco",
                    monthly_price=0,
                    description="Hasta 10 alumnos para validación",
                    transaction_fee_percent=2.0,
                ),
                Plan(
                    name="Plan Negro",
                    monthly_price=520,
                    description="Alumnos ilimitados y módulo de exámenes",
                    transaction_fee_percent=1.5,
                ),
                Plan(
                    name="Plan Maestro",
                    monthly_price=870,
                    description="Marketing automatizado y éxito del cliente",
                    transaction_fee_percent=1.0,
                ),
            ]
        )

    existing_profile = db.query(AcademyProfile).count()
    if existing_profile == 0:
        db.add(
            AcademyProfile(
                dojo_name="DojoFlow Central",
                owner_name="Dojo Owner",
                contact_email="owner@dojoflow.com",
                contact_phone="+52 555 000 0000",
                city="Ciudad de México",
                timezone="America/Mexico_City",
                currency="MXN",
            )
        )

    existing_marketplace_items = db.query(MarketplaceItem).count()
    if existing_marketplace_items == 0:
        db.add_all(
            [
                MarketplaceItem(name="Gi BJJ Oficial", category="Uniformes", price=1499, stock=20, active=True),
                MarketplaceItem(name="Guantes MMA Pro", category="Protección", price=899, stock=35, active=True),
                MarketplaceItem(name="Espinilleras TKD", category="Protección", price=749, stock=28, active=True),
            ]
        )

    existing_teachers = db.query(Teacher).count()
    if existing_teachers == 0:
        db.add_all(
            [
                Teacher(
                    name="Sensei Karate Master",
                    email="sensei.karate@dojoflow.com",
                    phone="+52 555 111 1111",
                    specialties="Karate,TKD",
                    hourly_rate=75,
                    active=True,
                ),
                Teacher(
                    name="Mestre BJJ Pro",
                    email="mestre.bjj@dojoflow.com",
                    phone="+52 555 222 2222",
                    specialties="BJJ",
                    hourly_rate=85,
                    active=True,
                ),
                Teacher(
                    name="Coach MMA Elite",
                    email="coach.mma@dojoflow.com",
                    phone="+52 555 333 3333",
                    specialties="MMA,Boxing",
                    hourly_rate=90,
                    active=True,
                ),
            ]
        )

    existing_schedules = db.query(Schedule).count()
    if existing_schedules == 0:
        # Need teacher IDs
        db.flush()  # commit to get IDs
        teachers = db.query(Teacher).all()
        if teachers:
            db.add_all(
                [
                    Schedule(
                        class_type="BJJ",
                        day_of_week=0,  # Lunes
                        start_time=time(18, 0),
                        end_time=time(19, 30),
                        teacher_id=teachers[1].id,
                        max_students=15,
                        active=True,
                    ),
                    Schedule(
                        class_type="BJJ",
                        day_of_week=2,  # Miércoles
                        start_time=time(18, 0),
                        end_time=time(19, 30),
                        teacher_id=teachers[1].id,
                        max_students=15,
                        active=True,
                    ),
                    Schedule(
                        class_type="Karate",
                        day_of_week=1,  # Martes
                        start_time=time(17, 0),
                        end_time=time(18, 0),
                        teacher_id=teachers[0].id,
                        max_students=20,
                        active=True,
                    ),
                    Schedule(
                        class_type="Karate",
                        day_of_week=4,  # Viernes
                        start_time=time(17, 0),
                        end_time=time(18, 0),
                        teacher_id=teachers[0].id,
                        max_students=20,
                        active=True,
                    ),
                    Schedule(
                        class_type="MMA",
                        day_of_week=3,  # Jueves
                        start_time=time(19, 0),
                        end_time=time(20, 30),
                        teacher_id=teachers[2].id,
                        max_students=12,
                        active=True,
                    ),
                    Schedule(
                        class_type="MMA",
                        day_of_week=5,  # Sábado
                        start_time=time(10, 0),
                        end_time=time(11, 30),
                        teacher_id=teachers[2].id,
                        max_students=12,
                        active=True,
                    ),
                ]
            )

    existing_coupons = db.query(Coupon).count()
    if existing_coupons == 0:
        db.add_all(
            [
                Coupon(
                    code="WELCOME10",
                    discount_percent=10,
                    max_uses=50,
                    valid_until=date(2026, 12, 31),
                    active=True,
                    description="10% descuento para nuevos alumnos",
                ),
                Coupon(
                    code="SUMMER20",
                    discount_percent=20,
                    max_uses=30,
                    valid_until=date(2026, 8, 31),
                    active=True,
                    description="20% descuento en agosto",
                ),
                Coupon(
                    code="LOYALTY5",
                    discount_percent=5,
                    max_uses=None,  # unlimited
                    valid_until=date(2027, 12, 31),
                    active=True,
                    description="5% para clientes recurrentes",
                ),
            ]
        )

    db.commit()


def init() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    init()
