
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/social-profiles", tags=["social-profiles"])

@router.post("", response_model=schemas.SocialProfileOut, status_code=201)
def create_social_profile(payload: schemas.SocialProfileCreate, db: Session = Depends(get_db)):
    if not db.get(models.Business, payload.business_id):
        raise HTTPException(400, "Invalid business_id")
    obj = models.SocialProfile(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        error_msg = f"Could not create social profile: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    db.refresh(obj)
    return obj

@router.get("", response_model=List[schemas.SocialProfileOut])
def list_social_profiles(db: Session = Depends(get_db)):
    return db.query(models.SocialProfile).order_by(models.SocialProfile.id.desc()).all()
