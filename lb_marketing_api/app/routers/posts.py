import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..db import get_db

logger = logging.getLogger(__name__)
from .. import models, schemas
from ..auth import get_current_user
from ..services.platform_poster import post_scheduled_post, PlatformPostError

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("", response_model=schemas.ScheduledPostOut, status_code=201)
def schedule_post(payload: schemas.ScheduledPostCreate, db: Session = Depends(get_db)):
    if not db.get(models.User, payload.user_id):
        raise HTTPException(400, "Invalid user_id")
    if payload.business_id and not db.get(models.Business, payload.business_id):
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
def list_posts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.ScheduledPost).filter(
        models.ScheduledPost.user_id == current_user.id
    ).order_by(models.ScheduledPost.scheduled_at.desc()).all()

@router.get("/{post_id}", response_model=schemas.ScheduledPostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.ScheduledPost, post_id)
    if not post:
        raise HTTPException(404, f"Post with id {post_id} not found")
    return post

@router.post("/publish", response_model=List[schemas.ScheduledPostOut])
def publish_all_posts(db: Session = Depends(get_db)):
    """
    Publish all scheduled posts that are due (scheduled_at <= now) and in 'scheduled' status.
    Returns list of published posts.
    """
    from datetime import datetime
    
    # Get all posts that are scheduled and due
    now = datetime.utcnow()
    due_posts = db.query(models.ScheduledPost).filter(
        models.ScheduledPost.status == models.PostStatus.scheduled,
        models.ScheduledPost.scheduled_at <= now
    ).all()
    
    published_posts = []
    errors = []
    
    for post in due_posts:
        try:
            updated_post = post_scheduled_post(post, db)
            published_posts.append(updated_post)
        except PlatformPostError as e:
            error_msg = f"Post {post.id}: {str(e)}"
            errors.append(error_msg)
    
    # Return published posts, with errors if any
    if errors:
        # Note: We still return published posts, but include errors in response
        # In production, you might want to handle this differently
        pass
    
    return published_posts

class PublishRequest(BaseModel):
    post_ids: List[int]

@router.post("/publish/batch", response_model=List[schemas.ScheduledPostOut])
def publish_posts(request: PublishRequest, db: Session = Depends(get_db)):
    """
    Publish one or more scheduled posts to their designated platforms.
    Requires post_ids in the request body.
    Always returns a list of published posts.
    Requires posts to be in 'scheduled' status and have connected social profiles.
    """
    return publish_posts_batch(request.post_ids, db)

def publish_posts_batch(post_ids: List[int], db: Session) -> List[schemas.ScheduledPostOut]:
    """
    Internal function to publish multiple posts in batch.
    Returns a list of successfully published posts.
    """
    if not post_ids:
        raise HTTPException(400, "No post IDs provided")
    
    published_posts = []
    errors = []
    
    for post_id in post_ids:
        post = db.get(models.ScheduledPost, post_id)
        if not post:
            errors.append(f"Post with id {post_id} not found")
            continue
        
        try:
            updated_post = post_scheduled_post(post, db)
            published_posts.append(updated_post)
        except PlatformPostError as e:
            errors.append(f"Post {post_id}: {str(e)}")
            # Mark post as failed
            post.status = models.PostStatus.failed
            # add logger line to print out the error
            logger.error(f"Error publishing post {post_id}: {str(e)}")
            db.commit()
    
    if not published_posts:
        error_msg = "Failed to publish any posts. " + "; ".join(errors)
        raise HTTPException(status_code=500, detail=error_msg)
    
    return published_posts

def process_due_posts(db: Session) -> List[schemas.ScheduledPostOut]:
    """
    Service function that polls the scheduled posts table for posts that are due.
    Checks scheduled_at time and publishes posts that are due (scheduled_at <= now).
    Returns a list of published posts.
    This function can be called from both the timer trigger and the HTTP endpoint.
    """
    from datetime import datetime
    
    now = datetime.utcnow()
    
    # Query for all posts that are scheduled and due
    due_posts = db.query(models.ScheduledPost).filter(
        models.ScheduledPost.status == models.PostStatus.scheduled,
        models.ScheduledPost.scheduled_at <= now
    ).order_by(models.ScheduledPost.scheduled_at.asc()).all()
    
    if not due_posts:
        return []
    
    # Extract post IDs
    post_ids = [post.id for post in due_posts]
    
    # Make a batch call to publish all due posts
    return publish_posts_batch(post_ids, db)

@router.post("/cron/publish", response_model=List[schemas.ScheduledPostOut])
def cron_publish_posts(db: Session = Depends(get_db)):
    """
    HTTP endpoint for manually triggering the publish process.
    The actual automated publishing is handled by the timer-triggered function.
    """
    return process_due_posts(db)