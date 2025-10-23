
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

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

class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    website: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    locations = relationship("Location", back_populates="business", cascade="all, delete-orphan")
    social_profiles = relationship("SocialProfile", back_populates="business", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="business", cascade="all, delete-orphan")
    assets = relationship("MediaAsset", back_populates="business", cascade="all, delete-orphan")
    posts = relationship("ScheduledPost", back_populates="business", cascade="all, delete-orphan")

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
    __table_args__ = (UniqueConstraint("business_id", "platform", "handle", name="uq_profile_business_platform_handle"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    platform: Mapped[PlatformEnum] = mapped_column(SAEnum(PlatformEnum), nullable=False)
    handle: Mapped[str] = mapped_column(String(255), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    access_token: Mapped[str | None] = mapped_column(Text)  # TODO: store encrypted / external secret manager
    status: Mapped[str] = mapped_column(String(50), default="connected")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id", ondelete="SET NULL"))
    platform: Mapped[PlatformEnum] = mapped_column(SAEnum(PlatformEnum), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    media_asset_id: Mapped[int | None] = mapped_column(ForeignKey("media_assets.id", ondelete="SET NULL"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[PostStatus] = mapped_column(SAEnum(PostStatus), default=PostStatus.scheduled, nullable=False)
    external_post_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    business = relationship("Business", back_populates="posts")
    campaign = relationship("Campaign", back_populates="posts")
    media_asset = relationship("MediaAsset", back_populates="posts")
