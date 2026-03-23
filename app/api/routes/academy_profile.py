from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.academy_profile import AcademyProfile
from app.schemas.academy_profile import AcademyProfileRead, AcademyProfileUpdate

router = APIRouter(prefix="/academy-profile", tags=["academy-profile"])


@router.get("", response_model=AcademyProfileRead)
def get_profile(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    profile = db.query(AcademyProfile).first()
    if not profile:
        profile = AcademyProfile(
            dojo_name="DojoFlow Central",
            owner_name="Dojo Owner",
            contact_email="owner@dojoflow.com",
            contact_phone="+52 555 000 0000",
            city="Ciudad de México",
            timezone="America/Mexico_City",
            currency="MXN",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("", response_model=AcademyProfileRead)
def update_profile(
    payload: AcademyProfileUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    profile = db.query(AcademyProfile).first()
    if not profile:
        profile = AcademyProfile(**payload.model_dump())
        db.add(profile)
    else:
        for key, value in payload.model_dump().items():
            setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile
