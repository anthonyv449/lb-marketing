from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ... import models, schemas
from ...auth import get_current_user

router = APIRouter(prefix="/demo/engagements/{engagement_id}/month-end", tags=["demo"])


def _get_engagement_or_403(
    engagement_id: int,
    current_user: models.User,
    db: Session,
) -> models.ClientEngagement:
    engagement = db.get(models.ClientEngagement, engagement_id)
    if not engagement:
        raise HTTPException(404, "Engagement not found")
    if engagement.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")
    return engagement


@router.post("", response_model=schemas.MonthEndReportOut, status_code=201)
def create_month_end_report(
    engagement_id: int,
    payload: schemas.MonthEndReportCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, current_user, db)

    existing = (
        db.query(models.MonthEndReport)
        .filter(models.MonthEndReport.engagement_id == engagement_id)
        .first()
    )
    if existing:
        raise HTTPException(409, "Month-end report already exists. Use PATCH to update.")

    obj = models.MonthEndReport(**payload.model_dump(), engagement_id=engagement_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=schemas.MonthEndReportOut)
def get_month_end_report(
    engagement_id: int,
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, db)

    obj = (
        db.query(models.MonthEndReport)
        .filter(models.MonthEndReport.engagement_id == engagement_id)
        .first()
    )
    if not obj:
        raise HTTPException(404, "Month-end report not found")
    return obj


@router.patch("", response_model=schemas.MonthEndReportOut)
def update_month_end_report(
    engagement_id: int,
    payload: schemas.MonthEndReportUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, current_user, db)

    obj = (
        db.query(models.MonthEndReport)
        .filter(models.MonthEndReport.engagement_id == engagement_id)
        .first()
    )
    if not obj:
        raise HTTPException(404, "Month-end report not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(obj)
    return obj
