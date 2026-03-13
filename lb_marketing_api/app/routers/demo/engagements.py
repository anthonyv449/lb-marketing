from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ... import models, schemas
from ...auth import get_current_user

router = APIRouter(prefix="/demo/engagements", tags=["demo"])


@router.post("", response_model=schemas.ClientEngagementOut, status_code=201)
def create_engagement(
    payload: schemas.ClientEngagementCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business = db.get(models.Business, payload.business_id)
    if not business:
        raise HTTPException(400, "Invalid business_id")
    if business.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")

    obj = models.ClientEngagement(**payload.model_dump(), user_id=current_user.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=List[schemas.ClientEngagementOut])
def list_engagements(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.ClientEngagement)
        .filter(models.ClientEngagement.user_id == current_user.id)
        .order_by(models.ClientEngagement.created_at.desc())
        .all()
    )


# Must be before /{engagement_id} so "new" is not captured as engagement_id
@router.post("/new", response_model=schemas.ClientEngagementOut, status_code=201)
def create_new_engagement(
    payload: Optional[schemas.DemoEngagementQuickStart] = Body(default=None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new business and engagement in one call. Engagement ID is auto-incremented."""
    business_name = (payload and payload.business_name) or "New Client"
    business = models.Business(user_id=current_user.id, name=business_name)
    db.add(business)
    db.flush()
    engagement = models.ClientEngagement(user_id=current_user.id, business_id=business.id)
    db.add(engagement)
    db.commit()
    db.refresh(engagement)
    return engagement


@router.get("/{engagement_id}", response_model=schemas.ClientEngagementOut)
def get_engagement(
    engagement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj = db.get(models.ClientEngagement, engagement_id)
    if not obj:
        raise HTTPException(404, "Engagement not found")
    if obj.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")
    return obj


@router.patch("/{engagement_id}", response_model=schemas.ClientEngagementOut)
def update_engagement(
    engagement_id: int,
    payload: schemas.ClientEngagementUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj = db.get(models.ClientEngagement, engagement_id)
    if not obj:
        raise HTTPException(404, "Engagement not found")
    if obj.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{engagement_id}", status_code=204)
def delete_engagement(
    engagement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj = db.get(models.ClientEngagement, engagement_id)
    if not obj:
        raise HTTPException(404, "Engagement not found")
    if obj.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")

    db.delete(obj)
    db.commit()
    return None
