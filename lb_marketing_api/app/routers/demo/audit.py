from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ... import models, schemas
from ...auth import get_current_user

router = APIRouter(prefix="/demo/engagements/{engagement_id}/audit", tags=["demo"])


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


@router.post("", response_model=schemas.AuditReportOut, status_code=201)
def create_audit_report(
    engagement_id: int,
    payload: schemas.AuditReportCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, current_user, db)

    existing = (
        db.query(models.AuditReport)
        .filter(models.AuditReport.engagement_id == engagement_id)
        .first()
    )
    if existing:
        raise HTTPException(409, "Audit report already exists. Use PATCH to update.")

    obj = models.AuditReport(**payload.model_dump(), engagement_id=engagement_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=schemas.AuditReportOut)
def get_audit_report(
    engagement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, current_user, db)

    obj = (
        db.query(models.AuditReport)
        .filter(models.AuditReport.engagement_id == engagement_id)
        .first()
    )
    if not obj:
        raise HTTPException(404, "Audit report not found")
    return obj


@router.patch("", response_model=schemas.AuditReportOut)
def update_audit_report(
    engagement_id: int,
    payload: schemas.AuditReportUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, current_user, db)

    obj = (
        db.query(models.AuditReport)
        .filter(models.AuditReport.engagement_id == engagement_id)
        .first()
    )
    if not obj:
        raise HTTPException(404, "Audit report not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(obj)
    return obj
