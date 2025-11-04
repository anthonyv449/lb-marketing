
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas
from ..services.platform_poster import post_scheduled_post, PlatformPostError

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

@router.get("/{post_id}", response_model=schemas.ScheduledPostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.ScheduledPost, post_id)
    if not post:
        raise HTTPException(404, f"Post with id {post_id} not found")
    return post

@router.post("/{post_id}/publish", response_model=schemas.ScheduledPostOut)
def publish_post(post_id: int, db: Session = Depends(get_db)):
    """
    Publish a scheduled post to its designated platform (X or Facebook).
    Requires the post to be in 'scheduled' status and have a connected social profile.
    """
    post = db.get(models.ScheduledPost, post_id)
    if not post:
        raise HTTPException(404, f"Post with id {post_id} not found")
    
    try:
        updated_post = post_scheduled_post(post, db)
        return updated_post
    except PlatformPostError as e:
        raise HTTPException(400, str(e))
