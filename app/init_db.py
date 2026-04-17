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
    # 1. Crear Users primero
    existing_user = db.query(User).filter(User.email == "owner@dojoflow.com").first()
    if not existing_user:
        owner = User(
            email="owner@dojoflow.com",
            full_name="Dojo Owner",
            hashed_password=create_password_hash("admin123"),
            is_active=True,
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
    else:
        owner = existing_user

    existing_dojo_user = db.query(User).filter(User.email == "dojo_1@dojoflow.local").first()
    if not existing_dojo_user:
        dojo_user = User(
            email="dojo_1@dojoflow.local",
            full_name="Dojo Demo",
            hashed_password=create_password_hash("dojo1234"),
            is_active=True,
        )
        db.add(dojo_user)
        db.commit()
        db.refresh(dojo_user)
    else:
        dojo_user = existing_dojo_user

    # 2. Crear Plans
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
        db.commit()

    # 3. Crear AcademyProfile con user_id válido
    existing_profile = db.query(AcademyProfile).filter(AcademyProfile.user_id == owner.id).first()
    if not existing_profile:
        academy = AcademyProfile(
            user_id=owner.id,
            dojo_name="Dojo Flow Principal",
            owner_name="Dojo Owner",
            contact_email="owner@dojoflow.com",
            contact_phone="+52 555 000 0000",
            city="Ciudad de México",
            timezone="America/Mexico_City",
            currency="MXN",
        )
        db.add(academy)
        db.commit()
        db.refresh(academy)
    else:
        academy = existing_profile

    # Valida que academy no sea None antes de continuar
    if academy is None:
        raise ValueError("AcademyProfile no pudo ser creado")

    # 4. Crear MarketplaceItems
    existing_marketplace_items = db.query(MarketplaceItem).count()
    if existing_marketplace_items == 0:
        db.add_all(
            [
                MarketplaceItem(name="Gi BJJ Oficial", category="Uniformes", price=1499, stock=20, active=True),
                MarketplaceItem(name="Guantes MMA Pro", category="Protección", price=899, stock=35, active=True),
                MarketplaceItem(name="Espinilleras TKD", category="Protección", price=749, stock=28, active=True),
            ]
        )
        db.commit()

    # 5. Crear Teachers CON academy_id
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
                    academy_id=academy.id,
                    active=True,
                ),
                Teacher(
                    name="Mestre BJJ Pro",
                    email="mestre.bjj@dojoflow.com",
                    phone="+52 555 222 2222",
                    specialties="BJJ",
                    hourly_rate=85,
                    academy_id=academy.id,
                    active=True,
                ),
                Teacher(
                    name="Coach MMA Elite",
                    email="coach.mma@dojoflow.com",
                    phone="+52 555 333 3333",
                    specialties="MMA,Boxing",
                    hourly_rate=90,
                    academy_id=academy.id,
                    active=True,
                ),
            ]
        )
        db.commit()

    # 6. Crear Schedules CON academy_id
# ...existing code...

    # 6. Crear Schedules CON academy_id (solo si la columna existe)
    try:
        existing_schedules = db.query(Schedule).count()
        if existing_schedules == 0:
            teachers = db.query(Teacher).all()
            if teachers:
                db.add_all(
                    [
                        Schedule(
                            class_type="BJJ",
                            day_of_week=0,
                            start_time="18:00",
                            end_time="19:30",
                            academy_id=academy.id,
                            max_students=15,
                            active=True,
                        ),
                        Schedule(
                            class_type="BJJ",
                            day_of_week=2,
                            start_time="18:00",
                            end_time="19:30",
                            academy_id=academy.id,
                            max_students=15,
                            active=True,
                        ),
                        Schedule(
                            class_type="Karate",
                            day_of_week=1,
                            start_time="17:00",
                            end_time="18:00",
                            academy_id=academy.id,
                            max_students=20,
                            active=True,
                        ),
                        Schedule(
                            class_type="Karate",
                            day_of_week=4,
                            start_time="17:00",
                            end_time="18:00",
                            academy_id=academy.id,
                            max_students=20,
                            active=True,
                        ),
                        Schedule(
                            class_type="MMA",
                            day_of_week=3,
                            start_time="19:00",
                            end_time="20:30",
                            academy_id=academy.id,
                            max_students=12,
                            active=True,
                        ),
                        Schedule(
                            class_type="MMA",
                            day_of_week=5,
                            start_time="10:00",
                            end_time="11:30",
                            academy_id=academy.id,
                            max_students=12,
                            active=True,
                        ),
                    ]
                )
                db.commit()
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudieron crear schedules. Asegúrate de ejecutar la migración SQL:")
        print(f"ALTER TABLE schedules ADD COLUMN academy_id INT NOT NULL;")
        print(f"ALTER TABLE schedules ADD FOREIGN KEY (academy_id) REFERENCES academy_profile(id);")
        print(f"Error: {e}")
        db.rollback()

# ...existing code...

    # 7. Crear Coupons
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
                    max_uses=None,
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