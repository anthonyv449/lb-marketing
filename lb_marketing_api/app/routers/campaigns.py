
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("", response_model=schemas.CampaignOut, status_code=201)
def create_campaign(payload: schemas.CampaignCreate, db: Session = Depends(get_db)):
    if not db.get(models.Business, payload.business_id):
        raise HTTPException(400, "Invalid business_id")
    obj = models.Campaign(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[schemas.CampaignOut])
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(models.Campaign).order_by(models.Campaign.id.desc()).all()
