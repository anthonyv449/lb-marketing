from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ... import models, schemas
from ...auth import get_current_user

router = APIRouter(prefix="/demo/engagements/{engagement_id}/tasks", tags=["demo"])


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


@router.get("", response_model=List[schemas.TaskStateOut])
def list_tasks(
    engagement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, current_user, db)
    return (
        db.query(models.TaskState)
        .filter(models.TaskState.engagement_id == engagement_id)
        .all()
    )


@router.put("/{task_id}", response_model=schemas.TaskStateOut)
def upsert_task(
    engagement_id: int,
    task_id: str,
    payload: schemas.TaskToggle,
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, db)

    task_state = (
        db.query(models.TaskState)
        .filter(
            models.TaskState.engagement_id == engagement_id,
            models.TaskState.task_id == task_id,
        )
        .first()
    )

    if task_state:
        task_state.completed = payload.completed
        task_state.completed_at = datetime.utcnow() if payload.completed else None
    else:
        task_state = models.TaskState(
            engagement_id=engagement_id,
            task_id=task_id,
            completed=payload.completed,
            completed_at=datetime.utcnow() if payload.completed else None,
        )
        db.add(task_state)

    db.commit()
    db.refresh(task_state)
    return task_state


@router.delete("")
def reset_tasks(
    engagement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, current_user, db)
    db.query(models.TaskState).filter(
        models.TaskState.engagement_id == engagement_id
    ).delete()
    db.commit()
    return {"reset": True, "engagement_id": engagement_id}
