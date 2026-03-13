
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/businesses", tags=["businesses"])

@router.post("", response_model=schemas.BusinessOut, status_code=201)
def create_business(payload: schemas.BusinessCreate, db: Session = Depends(get_db)):
    obj = models.Business(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[schemas.BusinessOut])
def list_businesses(db: Session = Depends(get_db)):
    return db.query(models.Business).order_by(models.Business.id.desc()).all()

@router.get("/{business_id}", response_model=schemas.BusinessOut)
def get_business(business_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Business, business_id)
    if not obj:
        raise HTTPException(404, "Business not found")
    return obj


@router.patch("/{business_id}", response_model=schemas.BusinessOut)
def update_business(
    business_id: int,
    payload: schemas.BusinessUpdate,
    db: Session = Depends(get_db),
):
    obj = db.get(models.Business, business_id)
    if not obj:
        raise HTTPException(404, "Business not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return obj
