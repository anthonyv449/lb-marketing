
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
import os

from ..db import get_db
from .. import models, schemas
from ..auth import get_current_user
from ..services.storage import storage_service
from ..config import settings

router = APIRouter(prefix="/assets", tags=["assets"])

# Allowed media types
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp"
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

@router.post("/upload", response_model=schemas.MediaAssetOut, status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload media file to Azure Storage and create a MediaAsset record.
    Files are stored in the user media container under folders organized by user ID.
    Format: {container_name}/{userId}/{filename}
    """
    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: JPEG, PNG, GIF, WEBP"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Get or create a business for the user
    business = db.query(models.Business).filter(
        models.Business.user_id == current_user.id
    ).first()
    
    if not business:
        # Create a default business for the user
        business = models.Business(
            user_id=current_user.id,
            name=f"{current_user.email}'s Business",
            email=current_user.email
        )
        db.add(business)
        db.commit()
        db.refresh(business)
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Generate unique filename to avoid collisions
    # Use UUID + original extension
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    # Store in folder organized by user ID: {userId}/{filename}
    blob_name = f"{current_user.id}/{unique_filename}"
    
    # Upload to Azure Storage
    if not storage_service.blob_service_client:
        raise HTTPException(
            status_code=503,
            detail="Azure Storage is not configured"
        )
    
    # Get the user media container name from config
    user_media_container = settings.AZURE_STORAGE_USER_MEDIA_CONTAINER_NAME
    
    # Upload the file to user media container (organized by user ID folders)
    upload_success = storage_service.upload_blob(
        blob_name=blob_name,
        data=file_content,
        content_type=file.content_type,
        container_name=user_media_container
    )
    
    if not upload_success:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload file to Azure Storage"
        )
    
    # Get the storage URL (construct from blob name with container prefix)
    # Store as: {container_name}/{userId}/{filename} for retrieval
    storage_url = f"{user_media_container}/{blob_name}"
    
    # Create MediaAsset record
    media_asset = models.MediaAsset(
        business_id=business.id,
        title=file.filename,
        storage_url=storage_url,
        mime_type=file.content_type
    )
    db.add(media_asset)
    db.commit()
    db.refresh(media_asset)
    
    return media_asset

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
