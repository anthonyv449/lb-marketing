"""
Platform posting service for X (Twitter), TikTok, and Facebook.
Handles posting scheduled posts to social media platforms via their APIs.
"""

import requests
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from .. import models


class PlatformPostError(Exception):
    """Custom exception for platform posting errors"""
    pass


def post_to_x(
    content: str,
    access_token: str,
    media_urls: Optional[List[str]] = None,
    social_profile: Optional[models.SocialProfile] = None
) -> Dict[str, Any]:
    """
    Post content to X (Twitter) using Twitter API v2.
    
    Args:
        content: The text content to post
        access_token: OAuth 2.0 Bearer token for Twitter API
        media_urls: Optional list of media URLs to attach
        social_profile: Optional SocialProfile object for additional context
        
    Returns:
        Dict containing the post response with 'id' and other fields
        
    Raises:
        PlatformPostError: If posting fails
    """
    try:
        # Twitter API v2 endpoint for creating tweets
        url = "https://api.twitter.com/2/tweets"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload: Dict[str, Any] = {
            "text": content
        }
        
        # If media URLs are provided, we'd need to upload them first
        # For now, we'll just post text content
        # TODO: Implement media upload for X API
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the tweet ID from the response
        if "data" in result and "id" in result["data"]:
            return {
                "external_post_id": result["data"]["id"],
                "platform_response": result
            }
        else:
            raise PlatformPostError(f"Unexpected response format: {result}")
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to post to X: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail}"
            except Exception as inner_e:
                error_msg += f" - Status: {e.response.status_code} (Error parsing response: {str(inner_e)})"
        raise PlatformPostError(error_msg) from e


def post_to_facebook(
    content: str,
    access_token: str,
    page_id: Optional[str] = None,
    media_url: Optional[str] = None,
    social_profile: Optional[models.SocialProfile] = None
) -> Dict[str, Any]:
    """
    Post content to Facebook using Facebook Graph API.
    
    Args:
        content: The text content to post
        access_token: Page access token for Facebook API
        page_id: Optional Facebook page ID (if not provided, uses profile's external_id)
        media_url: Optional media URL to attach
        social_profile: Optional SocialProfile object for additional context
        
    Returns:
        Dict containing the post response with 'id' and other fields
        
    Raises:
        PlatformPostError: If posting fails
    """
    try:
        # Use page_id from social_profile if not provided
        if not page_id and social_profile and social_profile.external_id:
            page_id = social_profile.external_id
        
        if not page_id:
            raise PlatformPostError("Facebook page_id is required for posting")
        
        # Facebook Graph API endpoint for posting to a page
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        
        params = {
            "message": content,
            "access_token": access_token
        }
        
        # If media URL is provided, use photos endpoint instead
        if media_url:
            url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
            params["url"] = media_url
            params["message"] = content
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the post ID from the response
        if "id" in result:
            return {
                "external_post_id": result["id"],
                "platform_response": result
            }
        else:
            raise PlatformPostError(f"Unexpected response format: {result}")
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to post to Facebook: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail}"
            except Exception as inner_e:
                error_msg += f" - Status: {e.response.status_code} (Error parsing response: {str(inner_e)})"
        raise PlatformPostError(error_msg) from e


def post_to_tiktok(
    content: str,
    access_token: str,
    media_urls: Optional[List[str]] = None,
    social_profile: Optional[models.SocialProfile] = None
) -> Dict[str, Any]:
    """
    Post content to TikTok using TikTok API v2.
    
    Args:
        content: The text content to post
        access_token: OAuth 2.0 Bearer token for TikTok API
        media_urls: Optional list of media URLs to attach
        social_profile: Optional SocialProfile object for additional context
        
    Returns:
        Dict containing the post response with 'id' and other fields
        
    Raises:
        PlatformPostError: If posting fails
    """
    try:
        # TikTok API v2 endpoint for creating videos/posts
        # Note: TikTok API requires video upload, text-only posts may not be supported
        # This is a simplified implementation - in production, you'd need to handle video uploads
        url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # TikTok requires video content, so we'll create a text post if no media is provided
        # In a real implementation, you'd need to upload video first
        payload: Dict[str, Any] = {
            "post_info": {
                "title": content[:100],  # TikTok title limit
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD"
            }
        }
        
        # If media URLs are provided, we'd need to upload them first
        # For now, this is a placeholder - TikTok API requires video upload workflow
        # TODO: Implement proper video upload for TikTok API
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the post ID from the response
        if "data" in result and "publish_id" in result["data"]:
            return {
                "external_post_id": result["data"]["publish_id"],
                "platform_response": result
            }
        else:
            raise PlatformPostError(f"Unexpected response format: {result}")
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to post to TikTok: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail}"
            except Exception as inner_e:
                error_msg += f" - Status: {e.response.status_code} (Error parsing response: {str(inner_e)})"
        raise PlatformPostError(error_msg) from e


def post_scheduled_post(
    scheduled_post: models.ScheduledPost,
    db: Session
) -> models.ScheduledPost:
    """
    Post a scheduled post to its designated platform.
    
    Args:
        scheduled_post: The ScheduledPost model instance to post
        db: Database session
        
    Returns:
        Updated ScheduledPost with status and external_post_id set
        
    Raises:
        PlatformPostError: If posting fails
    """
    # Validate post status
    if scheduled_post.status != models.PostStatus.scheduled:
        raise PlatformPostError(
            f"Post {scheduled_post.id} is not in scheduled status. Current status: {scheduled_post.status}"
        )
    
    # Find the social profile for this business and platform
    social_profile = db.query(models.SocialProfile).filter(
        models.SocialProfile.business_id == scheduled_post.business_id,
        models.SocialProfile.platform == scheduled_post.platform,
        models.SocialProfile.status == "connected"
    ).first()
    
    if not social_profile:
        raise PlatformPostError(
            f"No connected social profile found for business {scheduled_post.business_id} "
            f"on platform {scheduled_post.platform.value}"
        )
    
    if not social_profile.access_token:
        raise PlatformPostError(
            f"No access token found for social profile {social_profile.id}"
        )
    
    # Get media URL if media_asset_id is present
    media_url = None
    if scheduled_post.media_asset_id:
        media_asset = db.get(models.MediaAsset, scheduled_post.media_asset_id)
        if media_asset:
            media_url = media_asset.storage_url
    
    # Post to the appropriate platform
    try:
        if scheduled_post.platform == models.PlatformEnum.x:
            result = post_to_x(
                content=scheduled_post.content,
                access_token=social_profile.access_token,
                media_urls=[media_url] if media_url else None,
                social_profile=social_profile
            )
        elif scheduled_post.platform == models.PlatformEnum.tiktok:
            result = post_to_tiktok(
                content=scheduled_post.content,
                access_token=social_profile.access_token,
                media_urls=[media_url] if media_url else None,
                social_profile=social_profile
            )
        elif scheduled_post.platform == models.PlatformEnum.facebook:
            result = post_to_facebook(
                content=scheduled_post.content,
                access_token=social_profile.access_token,
                page_id=social_profile.external_id,
                media_url=media_url,
                social_profile=social_profile
            )
        else:
            raise PlatformPostError(
                f"Posting to platform {scheduled_post.platform.value} is not yet implemented"
            )
        
        # Update the scheduled post with success
        scheduled_post.external_post_id = result["external_post_id"]
        scheduled_post.status = models.PostStatus.posted
        db.commit()
        db.refresh(scheduled_post)
        
        return scheduled_post
        
    except PlatformPostError as e:
        # Update status to failed
        scheduled_post.status = models.PostStatus.failed
        db.commit()
        db.refresh(scheduled_post)
        # Re-raise with the exception message
        raise PlatformPostError(str(e)) from e

