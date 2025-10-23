
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/assets", tags=["assets"])

@router.post("", response_model=schemas.MediaAssetOut, status_code=201)
def create_asset(payload: schemas.MediaAssetCreate, db: Session = Depends(get_db)):
    if not db.get(models.Business, payload.business_id):
        raise HTTPException(400, "Invalid business_id")
    obj = models.MediaAsset(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[schemas.MediaAssetOut])
def list_assets(db: Session = Depends(get_db)):
    return db.query(models.MediaAsset).order_by(models.MediaAsset.id.desc()).all()
