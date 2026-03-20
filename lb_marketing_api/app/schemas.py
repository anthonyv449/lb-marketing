
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer
from enum import Enum

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

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
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


# ---------------------------------------------------------------------------
# Demo module schemas
# ---------------------------------------------------------------------------

class DemoEngagementQuickStart(BaseModel):
    """Optional body for POST /demo/engagements/new. Creates Business + Engagement in one call."""
    business_name: Optional[str] = "New Client"


class ClientEngagementCreate(BaseModel):
    business_id: int
    contact_name: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    gbp_account_id: Optional[str] = None
    gbp_location_id: Optional[str] = None
    gbp_access: Optional[str] = None
    start_type: Optional[str] = None
    current_rating: Optional[float] = None
    review_count: Optional[int] = None
    main_goal: Optional[str] = None
    notes: Optional[str] = None


class ClientEngagementUpdate(BaseModel):
    contact_name: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    gbp_account_id: Optional[str] = None
    gbp_location_id: Optional[str] = None
    gbp_access: Optional[str] = None
    start_type: Optional[str] = None
    current_rating: Optional[float] = None
    review_count: Optional[int] = None
    main_goal: Optional[str] = None
    notes: Optional[str] = None


class ClientEngagementOut(BaseModel):
    id: int
    user_id: int
    business_id: int
    business_name: Optional[str] = None
    contact_name: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    gbp_account_id: Optional[str] = None
    gbp_location_id: Optional[str] = None
    gbp_access: Optional[str] = None
    start_type: Optional[str] = None
    current_rating: Optional[float] = None
    review_count: Optional[int] = None
    main_goal: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)

    class Config:
        from_attributes = True


class TaskStateOut(BaseModel):
    id: int
    engagement_id: int
    task_id: str
    completed: bool
    completed_at: Optional[datetime] = None

    @field_serializer('completed_at')
    def serialize_completed_at(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        return serialize_datetime_utc(dt)

    class Config:
        from_attributes = True


class TaskToggle(BaseModel):
    completed: bool


class TaskBatchDelete(BaseModel):
    task_ids: List[str] = Field(..., min_length=1, description="Task IDs to delete")


class AuditReportCreate(BaseModel):
    auditor: Optional[str] = None
    date_delivered: Optional[str] = None
    gbp_status: Optional[str] = None
    gbp_photos: Optional[str] = None
    gbp_rating: Optional[float] = None
    gbp_reviews: Optional[int] = None
    yelp_status: Optional[str] = None
    yelp_rating: Optional[float] = None
    yelp_reviews: Optional[int] = None
    rank_term_1: Optional[str] = None
    rank_position_1: Optional[int] = None
    rank_term_2: Optional[str] = None
    rank_position_2: Optional[int] = None
    website_score: Optional[str] = None
    citation_notes: Optional[str] = None
    priority_issue_1: Optional[str] = None
    priority_issue_2: Optional[str] = None
    priority_issue_3: Optional[str] = None
    quick_win_1: Optional[str] = None
    quick_win_2: Optional[str] = None
    notes: Optional[str] = None


class AuditReportUpdate(BaseModel):
    auditor: Optional[str] = None
    date_delivered: Optional[str] = None
    gbp_status: Optional[str] = None
    gbp_photos: Optional[str] = None
    gbp_rating: Optional[float] = None
    gbp_reviews: Optional[int] = None
    yelp_status: Optional[str] = None
    yelp_rating: Optional[float] = None
    yelp_reviews: Optional[int] = None
    rank_term_1: Optional[str] = None
    rank_position_1: Optional[int] = None
    rank_term_2: Optional[str] = None
    rank_position_2: Optional[int] = None
    website_score: Optional[str] = None
    citation_notes: Optional[str] = None
    priority_issue_1: Optional[str] = None
    priority_issue_2: Optional[str] = None
    priority_issue_3: Optional[str] = None
    quick_win_1: Optional[str] = None
    quick_win_2: Optional[str] = None
    notes: Optional[str] = None


class AuditReportOut(BaseModel):
    id: int
    engagement_id: int
    auditor: Optional[str] = None
    date_delivered: Optional[str] = None
    gbp_status: Optional[str] = None
    gbp_photos: Optional[str] = None
    gbp_rating: Optional[float] = None
    gbp_reviews: Optional[int] = None
    yelp_status: Optional[str] = None
    yelp_rating: Optional[float] = None
    yelp_reviews: Optional[int] = None
    rank_term_1: Optional[str] = None
    rank_position_1: Optional[int] = None
    rank_term_2: Optional[str] = None
    rank_position_2: Optional[int] = None
    website_score: Optional[str] = None
    citation_notes: Optional[str] = None
    priority_issue_1: Optional[str] = None
    priority_issue_2: Optional[str] = None
    priority_issue_3: Optional[str] = None
    quick_win_1: Optional[str] = None
    quick_win_2: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)

    class Config:
        from_attributes = True


class ReviewRecordOut(BaseModel):
    id: int
    engagement_id: int
    gbp_review_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_text: Optional[str] = None
    star_rating: Optional[str] = None
    review_published_at: Optional[datetime] = None
    has_reply: bool
    reply_text: Optional[str] = None
    reply_generated_by: Optional[str] = None
    reply_posted_at: Optional[datetime] = None
    created_at: datetime

    @field_serializer('review_published_at', 'reply_posted_at')
    def serialize_optional_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        return serialize_datetime_utc(dt)

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)

    class Config:
        from_attributes = True


class AutoReplyRequest(BaseModel):
    tone: str = "warm"
    dry_run: bool = False


class AutoReplyResultItem(BaseModel):
    review_id: int
    gbp_review_id: Optional[str] = None
    reviewer: str
    review_snippet: str
    generated_reply: Optional[str] = None
    posted: bool
    saved: bool
    error: Optional[str] = None


class AutoReplyResult(BaseModel):
    processed: int
    succeeded: int
    failed: int
    dry_run: bool
    results: list[AutoReplyResultItem]


class MonthEndReportCreate(BaseModel):
    period: Optional[str] = None
    rank_term_1: Optional[str] = None
    rank_before_1: Optional[int] = None
    rank_after_1: Optional[int] = None
    rank_term_2: Optional[str] = None
    rank_before_2: Optional[int] = None
    rank_after_2: Optional[int] = None
    reviews_before: Optional[int] = None
    reviews_after: Optional[int] = None
    rating_before: Optional[float] = None
    rating_after: Optional[float] = None
    profile_views_before: Optional[int] = None
    profile_views_after: Optional[int] = None
    gbp_changes: Optional[str] = None
    highlights: Optional[str] = None
    next_month_plan: Optional[str] = None


class MonthEndReportUpdate(BaseModel):
    period: Optional[str] = None
    rank_term_1: Optional[str] = None
    rank_before_1: Optional[int] = None
    rank_after_1: Optional[int] = None
    rank_term_2: Optional[str] = None
    rank_before_2: Optional[int] = None
    rank_after_2: Optional[int] = None
    reviews_before: Optional[int] = None
    reviews_after: Optional[int] = None
    rating_before: Optional[float] = None
    rating_after: Optional[float] = None
    profile_views_before: Optional[int] = None
    profile_views_after: Optional[int] = None
    gbp_changes: Optional[str] = None
    highlights: Optional[str] = None
    next_month_plan: Optional[str] = None


class MonthEndReportOut(BaseModel):
    id: int
    engagement_id: int
    period: Optional[str] = None
    rank_term_1: Optional[str] = None
    rank_before_1: Optional[int] = None
    rank_after_1: Optional[int] = None
    rank_term_2: Optional[str] = None
    rank_before_2: Optional[int] = None
    rank_after_2: Optional[int] = None
    reviews_before: Optional[int] = None
    reviews_after: Optional[int] = None
    rating_before: Optional[float] = None
    rating_after: Optional[float] = None
    profile_views_before: Optional[int] = None
    profile_views_after: Optional[int] = None
    gbp_changes: Optional[str] = None
    highlights: Optional[str] = None
    next_month_plan: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        return serialize_datetime_utc(dt)

    class Config:
        from_attributes = True