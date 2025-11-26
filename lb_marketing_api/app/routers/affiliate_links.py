from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/affiliate-links", tags=["affiliate-links"])

@router.post("", response_model=schemas.AffiliateLinkOut, status_code=201)
def create_affiliate_link(
    payload: schemas.AffiliateLinkCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new affiliate link.
    Requires authentication. The created_by field is automatically set to the current user.
    """
    # Verify user is active (already checked by get_current_user, but double-check)
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create affiliate link with current user as creator
    link_data = payload.model_dump()
    link_data["created_by"] = current_user.id
    affiliate_link = models.AffiliateLink(**link_data)
    db.add(affiliate_link)
    db.commit()
    db.refresh(affiliate_link)
    return affiliate_link

@router.get("", response_model=List[schemas.AffiliateLinkOut])
def list_affiliate_links(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    is_active: Optional[bool] = None,
    preferred: Optional[bool] = None,
    category: Optional[str] = None
):
    """
    List all affiliate links.
    Requires authentication. Can filter by is_active, preferred, and category.
    """
    query = db.query(models.AffiliateLink)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(models.AffiliateLink.is_active == is_active)
    if preferred is not None:
        query = query.filter(models.AffiliateLink.preferred == preferred)
    if category:
        query = query.filter(models.AffiliateLink.category == category)
    
    return query.order_by(models.AffiliateLink.id.desc()).all()

@router.get("/{link_id}", response_model=schemas.AffiliateLinkOut)
def get_affiliate_link(
    link_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific affiliate link by ID.
    Requires authentication.
    """
    affiliate_link = db.get(models.AffiliateLink, link_id)
    if not affiliate_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Affiliate link with id {link_id} not found"
        )
    return affiliate_link

@router.put("/{link_id}", response_model=schemas.AffiliateLinkOut)
def update_affiliate_link(
    link_id: int,
    payload: schemas.AffiliateLinkUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an affiliate link.
    Requires authentication. Only the creator can update their affiliate links.
    """
    affiliate_link = db.get(models.AffiliateLink, link_id)
    if not affiliate_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Affiliate link with id {link_id} not found"
        )
    
    # Verify user is the creator
    if affiliate_link.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this affiliate link"
        )
    
    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(affiliate_link, field, value)
    
    db.commit()
    db.refresh(affiliate_link)
    return affiliate_link

@router.patch("/{link_id}", response_model=schemas.AffiliateLinkOut)
def partial_update_affiliate_link(
    link_id: int,
    payload: schemas.AffiliateLinkUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Partially update an affiliate link (same as PUT for this implementation).
    Requires authentication. Only the creator can update their affiliate links.
    """
    return update_affiliate_link(link_id, payload, current_user, db)

@router.delete("/{link_id}", status_code=204)
def delete_affiliate_link(
    link_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an affiliate link.
    Requires authentication. Only the creator can delete their affiliate links.
    """
    affiliate_link = db.get(models.AffiliateLink, link_id)
    if not affiliate_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Affiliate link with id {link_id} not found"
        )
    
    # Verify user is the creator
    if affiliate_link.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this affiliate link"
        )
    
    db.delete(affiliate_link)
    db.commit()
    return None

