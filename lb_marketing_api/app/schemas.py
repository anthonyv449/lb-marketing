
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer
from enum import Enum
from .models import PayoutType

def serialize_datetime_utc(dt: datetime) -> str:
    """Serialize datetime to ISO format with UTC timezone indicator ('Z' suffix)."""
    # If datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC if it has timezone info
        dt = dt.astimezone(timezone.utc)
    # Return ISO format, ensuring it ends with 'Z' for UTC
    iso_str = dt.isoformat()
    # Replace '+00:00' with 'Z' for UTC timezone
    if iso_str.endswith('+00:00'):
        return iso_str[:-6] + 'Z'
    return iso_str

class PlatformEnum(str, Enum):
    facebook = "facebook"
    instagram = "instagram"
    tiktok = "tiktok"
    x = "x"
    youtube = "youtube"
    linkedin = "linkedin"

class PostStatus(str, Enum):
    scheduled = "scheduled"
    posted = "posted"
    failed = "failed"
    canceled = "canceled"

class BusinessCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

class BusinessOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)
    
    class Config:
        from_attributes = True

class LocationCreate(BaseModel):
    business_id: int
    name: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "USA"
    timezone: Optional[str] = "America/Los_Angeles"

class LocationOut(BaseModel):
    id: int
    business_id: int
    name: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    class Config:
        from_attributes = True

class SocialProfileCreate(BaseModel):
    user_id: int
    business_id: int
    platform: PlatformEnum
    handle: str
    external_id: Optional[str] = None
    access_token: Optional[str] = None

class SocialProfileOut(BaseModel):
    id: int
    user_id: int
    business_id: int
    platform: PlatformEnum
    handle: str
    external_id: Optional[str] = None
    status: str
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)
    
    class Config:
        from_attributes = True

class CampaignCreate(BaseModel):
    business_id: int
    name: str
    goal: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignOut(BaseModel):
    id: int
    business_id: int
    name: str
    goal: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str
    
    @field_serializer('start_date', 'end_date')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        return serialize_datetime_utc(dt)
    
    class Config:
        from_attributes = True

class MediaAssetCreate(BaseModel):
    business_id: int
    title: Optional[str] = None
    storage_url: str
    mime_type: Optional[str] = None

class MediaAssetOut(BaseModel):
    id: int
    business_id: int
    title: Optional[str] = None
    storage_url: str
    mime_type: Optional[str] = None
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)
    
    class Config:
        from_attributes = True

class ScheduledPostCreate(BaseModel):
    user_id: int
    platform: PlatformEnum
    content: str = Field(..., max_length=2000)
    scheduled_at: datetime
    business_id: Optional[int] = None
    campaign_id: Optional[int] = None
    media_asset_id: Optional[int] = None

class ScheduledPostOut(BaseModel):
    id: int
    user_id: int
    business_id: Optional[int] = None
    campaign_id: Optional[int] = None
    platform: PlatformEnum
    content: str
    media_asset_id: Optional[int] = None
    scheduled_at: datetime
    status: PostStatus
    external_post_id: Optional[str] = None
    created_at: datetime
    
    @field_serializer('scheduled_at', 'created_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool
    
    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class AffiliateLinkCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    affiliate_program: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    payout_type: PayoutType
    commission_rate: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: bool = True
    seo_keywords: Optional[str] = None
    estimated_conversion_rate: Optional[float] = None
    preferred: bool = False

class AffiliateLinkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    affiliate_program: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    payout_type: Optional[PayoutType] = None
    commission_rate: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    seo_keywords: Optional[str] = None
    estimated_conversion_rate: Optional[float] = None
    preferred: Optional[bool] = None

class AffiliateLinkOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    affiliate_program: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    payout_type: PayoutType
    commission_rate: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: bool
    created_by: int
    seo_keywords: Optional[str] = None
    estimated_conversion_rate: Optional[float] = None
    preferred: bool
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)
    
    class Config:
        from_attributes = True