
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, UniqueConstraint,
    Boolean, Numeric
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from passlib.hash import argon2

pwd_context = argon2

from .db import Base

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

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    social_profiles = relationship("SocialProfile", back_populates="user", cascade="all, delete-orphan")
    businesses = relationship("Business", back_populates="user", cascade="all, delete-orphan")
    scheduled_posts = relationship("ScheduledPost", back_populates="user", cascade="all, delete-orphan")
    engagements = relationship("ClientEngagement", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the user's password."""
        return pwd_context.verify(password, self.password_hash)

class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    website: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="businesses")
    locations = relationship("Location", back_populates="business", cascade="all, delete-orphan")
    social_profiles = relationship("SocialProfile", back_populates="business", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="business", cascade="all, delete-orphan")
    assets = relationship("MediaAsset", back_populates="business", cascade="all, delete-orphan")
    posts = relationship("ScheduledPost", back_populates="business", cascade="all, delete-orphan")
    engagements = relationship("ClientEngagement", back_populates="business", cascade="all, delete-orphan")

class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line1: Mapped[str | None] = mapped_column(String(255))
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str | None] = mapped_column(String(100), default="USA")
    timezone: Mapped[str | None] = mapped_column(String(64), default="America/Los_Angeles")

    business = relationship("Business", back_populates="locations")

class SocialProfile(Base):
    __tablename__ = "social_profiles"
    __table_args__ = (UniqueConstraint("user_id", "platform", "handle", name="uq_profile_user_platform_handle"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    platform: Mapped[PlatformEnum] = mapped_column(SAEnum(PlatformEnum), nullable=False)
    handle: Mapped[str] = mapped_column(String(255), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    access_token: Mapped[str | None] = mapped_column(Text)  # TODO: store encrypted / external secret manager
    status: Mapped[str] = mapped_column(String(50), default="connected")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="social_profiles")
    business = relationship("Business", back_populates="social_profiles")

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    goal: Mapped[str | None] = mapped_column(String(255))
    start_date: Mapped[datetime | None] = mapped_column(DateTime)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), default="active")

    business = relationship("Business", back_populates="campaigns")
    posts = relationship("ScheduledPost", back_populates="campaign")

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    title: Mapped[str | None] = mapped_column(String(255))
    storage_url: Mapped[str] = mapped_column(Text)  # could be CDN or blob key/URL
    mime_type: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    business = relationship("Business", back_populates="assets")
    posts = relationship("ScheduledPost", back_populates="media_asset")

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_id: Mapped[int | None] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id", ondelete="SET NULL"))
    platform: Mapped[PlatformEnum] = mapped_column(SAEnum(PlatformEnum), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    media_asset_id: Mapped[int | None] = mapped_column(ForeignKey("media_assets.id", ondelete="SET NULL"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[PostStatus] = mapped_column(SAEnum(PostStatus), default=PostStatus.scheduled, nullable=False)
    external_post_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="scheduled_posts")
    business = relationship("Business", back_populates="posts")
    campaign = relationship("Campaign", back_populates="posts")
    media_asset = relationship("MediaAsset", back_populates="posts")

class OAuthState(Base):
    __tablename__ = "oauth_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code_verifier: Mapped[str | None] = mapped_column(String(255))  # Required for PKCE (X/Twitter), optional for others
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # 'x', 'tiktok', etc.
    business_id: Mapped[int | None] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # Expiration time (e.g., 10 minutes)


class ClientEngagement(Base):
    __tablename__ = "client_engagements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))
    gbp_account_id: Mapped[str | None] = mapped_column(String(255))
    gbp_location_id: Mapped[str | None] = mapped_column(String(255))
    gbp_access: Mapped[str | None] = mapped_column(String(50))
    start_type: Mapped[str | None] = mapped_column(String(50))
    current_rating: Mapped[float | None] = mapped_column(Numeric(3, 1))
    review_count: Mapped[int | None] = mapped_column(Integer)
    main_goal: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="engagements")
    business = relationship("Business", back_populates="engagements")
    task_states = relationship("TaskState", back_populates="engagement", cascade="all, delete-orphan")
    audit_report = relationship("AuditReport", back_populates="engagement", uselist=False, cascade="all, delete-orphan")
    review_records = relationship("ReviewRecord", back_populates="engagement", cascade="all, delete-orphan")
    month_end_report = relationship("MonthEndReport", back_populates="engagement", uselist=False, cascade="all, delete-orphan")


class TaskState(Base):
    __tablename__ = "task_states"
    __table_args__ = (UniqueConstraint("engagement_id", "task_id", name="uq_task_state_engagement_task"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    engagement_id: Mapped[int] = mapped_column(ForeignKey("client_engagements.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[str] = mapped_column(String(50), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    engagement = relationship("ClientEngagement", back_populates="task_states")


class AuditReport(Base):
    __tablename__ = "audit_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    engagement_id: Mapped[int] = mapped_column(ForeignKey("client_engagements.id", ondelete="CASCADE"), nullable=False, unique=True)
    auditor: Mapped[str | None] = mapped_column(String(255))
    date_delivered: Mapped[str | None] = mapped_column(String(100))
    gbp_status: Mapped[str | None] = mapped_column(String(100))
    gbp_photos: Mapped[str | None] = mapped_column(String(100))
    gbp_rating: Mapped[float | None] = mapped_column(Numeric(3, 1))
    gbp_reviews: Mapped[int | None] = mapped_column(Integer)
    rank_term_1: Mapped[str | None] = mapped_column(String(255))
    rank_position_1: Mapped[int | None] = mapped_column(Integer)
    rank_term_2: Mapped[str | None] = mapped_column(String(255))
    rank_position_2: Mapped[int | None] = mapped_column(Integer)
    website_score: Mapped[str | None] = mapped_column(String(100))
    citation_notes: Mapped[str | None] = mapped_column(String(500))
    priority_issue_1: Mapped[str | None] = mapped_column(Text)
    priority_issue_2: Mapped[str | None] = mapped_column(Text)
    priority_issue_3: Mapped[str | None] = mapped_column(Text)
    quick_win_1: Mapped[str | None] = mapped_column(Text)
    quick_win_2: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("ClientEngagement", back_populates="audit_report")


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    engagement_id: Mapped[int] = mapped_column(ForeignKey("client_engagements.id", ondelete="CASCADE"), nullable=False)
    gbp_review_id: Mapped[str | None] = mapped_column(String(255))
    reviewer_name: Mapped[str | None] = mapped_column(String(255))
    review_text: Mapped[str | None] = mapped_column(Text)
    star_rating: Mapped[str | None] = mapped_column(String(10))
    review_published_at: Mapped[datetime | None] = mapped_column(DateTime)
    has_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reply_text: Mapped[str | None] = mapped_column(Text)
    reply_generated_by: Mapped[str | None] = mapped_column(String(50))
    reply_posted_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    engagement = relationship("ClientEngagement", back_populates="review_records")


class MonthEndReport(Base):
    __tablename__ = "month_end_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    engagement_id: Mapped[int] = mapped_column(ForeignKey("client_engagements.id", ondelete="CASCADE"), nullable=False, unique=True)
    period: Mapped[str | None] = mapped_column(String(100))
    rank_term_1: Mapped[str | None] = mapped_column(String(255))
    rank_before_1: Mapped[int | None] = mapped_column(Integer)
    rank_after_1: Mapped[int | None] = mapped_column(Integer)
    rank_term_2: Mapped[str | None] = mapped_column(String(255))
    rank_before_2: Mapped[int | None] = mapped_column(Integer)
    rank_after_2: Mapped[int | None] = mapped_column(Integer)
    reviews_before: Mapped[int | None] = mapped_column(Integer)
    reviews_after: Mapped[int | None] = mapped_column(Integer)
    rating_before: Mapped[float | None] = mapped_column(Numeric(3, 1))
    rating_after: Mapped[float | None] = mapped_column(Numeric(3, 1))
    profile_views_before: Mapped[int | None] = mapped_column(Integer)
    profile_views_after: Mapped[int | None] = mapped_column(Integer)
    gbp_changes: Mapped[str | None] = mapped_column(Text)
    highlights: Mapped[str | None] = mapped_column(Text)
    next_month_plan: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("ClientEngagement", back_populates="month_end_report")
