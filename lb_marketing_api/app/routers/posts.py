
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("", response_model=schemas.ScheduledPostOut, status_code=201)
def schedule_post(payload: schemas.ScheduledPostCreate, db: Session = Depends(get_db)):
    if not db.get(models.Business, payload.business_id):
        raise HTTPException(400, "Invalid business_id")
    if payload.campaign_id and not db.get(models.Campaign, payload.campaign_id):
        raise HTTPException(400, "Invalid campaign_id")
    if payload.media_asset_id and not db.get(models.MediaAsset, payload.media_asset_id):
        raise HTTPException(400, "Invalid media_asset_id")
    obj = models.ScheduledPost(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[schemas.ScheduledPostOut])
def list_posts(db: Session = Depends(get_db)):
    return db.query(models.ScheduledPost).order_by(models.ScheduledPost.scheduled_at.desc()).all()
