
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/locations", tags=["locations"])

@router.post("", response_model=schemas.LocationOut, status_code=201)
def create_location(payload: schemas.LocationCreate, db: Session = Depends(get_db)):
    if not db.get(models.Business, payload.business_id):
        raise HTTPException(400, "Invalid business_id")
    obj = models.Location(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[schemas.LocationOut])
def list_locations(db: Session = Depends(get_db)):
    return db.query(models.Location).order_by(models.Location.id.desc()).all()
