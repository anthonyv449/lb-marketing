
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

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
    class Config:
        from_attributes = True

class ScheduledPostCreate(BaseModel):
    business_id: int
    platform: PlatformEnum
    content: str = Field(..., max_length=2000)
    scheduled_at: datetime
    campaign_id: Optional[int] = None
    media_asset_id: Optional[int] = None

class ScheduledPostOut(BaseModel):
    id: int
    business_id: int
    campaign_id: Optional[int] = None
    platform: PlatformEnum
    content: str
    media_asset_id: Optional[int] = None
    scheduled_at: datetime
    status: PostStatus
    external_post_id: Optional[str] = None
    created_at: datetime
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
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut