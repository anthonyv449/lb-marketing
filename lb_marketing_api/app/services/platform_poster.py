"""
Platform posting service for X (Twitter).
Handles posting scheduled posts to X via their API.
"""

import requests
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
import io

from .. import models
from ..services.storage import logger, storage_service
from ..config import settings


class PlatformPostError(Exception):
    """Custom exception for platform posting errors"""
    pass


def validate_x_token(access_token: str) -> Tuple[bool, Optional[str]]:
    """
    Validate X (Twitter) access token by making a test API call.
    
    Args:
        access_token: OAuth 2.0 Bearer token for Twitter API
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if token is valid, False otherwise
        - error_message: Error message if token is invalid, None if valid
    """
    try:
        # Use Twitter API v2 endpoint to get user info (lightweight validation)
        url = "https://api.twitter.com/2/users/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Token is valid if we get a 200 response
        if response.status_code == 200:
            return True, None
        
        # Token is invalid if we get 401 (Unauthorized)
        if response.status_code == 401:
            try:
                error_data = response.json()
                error_msg = "Invalid or expired access token"
                if "errors" in error_data:
                    error_messages = [err.get("message", str(err)) for err in error_data["errors"]]
                    error_msg = ", ".join(error_messages)
                return False, error_msg
            except Exception:
                return False, "Invalid or expired access token"
        
        # Other status codes might indicate temporary issues
        # For now, we'll consider them as potentially valid to avoid false disconnections
        # But log the issue
        return True, None
        
    except requests.exceptions.RequestException as e:
        # Network errors shouldn't cause disconnection
        # Return True but with a warning message
        return True, f"Unable to validate token due to network error: {str(e)}"
    except Exception as e:
        # Unexpected errors shouldn't cause disconnection
        return True, f"Unable to validate token: {str(e)}"


def upload_media_to_x(media_data: bytes, media_type: str, access_token: str) -> str:
    """
    Upload media to X (Twitter) using API v1.1 upload endpoint.
    Note: X API v2 doesn't have a media upload endpoint, so we use v1.1 for uploads
    but the media_id can be used with v2 tweet creation.
    
    Args:
        media_data: The media file as bytes
        media_type: MIME type of the media (e.g., 'image/jpeg', 'image/png', 'image/gif')
        access_token: OAuth 2.0 Bearer token for Twitter API
        
    Returns:
        media_id string to use when creating the tweet
        
    Raises:
        PlatformPostError: If upload fails
    """
    try:
        # X (Twitter) API v1.1 media upload endpoint
        # Note: Media uploads use v1.1 API, but media_id works with v2 tweets
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        # X requires multipart/form-data for media upload
        files = {
            "media": ("media", io.BytesIO(media_data), media_type)
        }
        
        response = requests.post(upload_url, headers=headers, files=files)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for errors in the response
        if "errors" in result:
            error_details = result.get("errors", [])
            error_messages = [str(err) for err in error_details]
            raise PlatformPostError(f"X API returned errors: {', '.join(error_messages)}")
        
        # Extract media_id from response (v1.1 API returns media_id_string or media_id)
        if "media_id_string" in result:
            return result["media_id_string"]
        elif "media_id" in result:
            return str(result["media_id"])
        else:
            raise PlatformPostError(f"Unexpected media upload response format: {result}")
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to upload media to X: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            error_msg += f" (HTTP {status_code})"
            try:
                error_detail = e.response.json()
                if isinstance(error_detail, dict):
                    if "errors" in error_detail:
                        error_messages = [err.get("message", str(err)) for err in error_detail["errors"]]
                        error_msg += f" - {', '.join(error_messages)}"
                    else:
                        error_msg += f" - {error_detail}"
                else:
                    error_msg += f" - {error_detail}"
            except Exception:
                error_msg += f" - Status: {e.response.status_code}"
        raise PlatformPostError(error_msg) from e


def post_to_x(
    content: str,
    access_token: str,
    media_urls: Optional[List[str]] = None,
    media_data: Optional[bytes] = None,
    media_type: Optional[str] = None,
    social_profile: Optional[models.SocialProfile] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Post content to X (Twitter) using Twitter API v2.
    
    Args:
        content: The text content to post
        access_token: OAuth 2.0 Bearer token for Twitter API
        media_urls: Optional list of media URLs (deprecated, use media_data instead)
        media_data: Optional media file as bytes to upload
        media_type: Optional MIME type of the media (required if media_data is provided)
        social_profile: Optional SocialProfile object for additional context
        db: Optional database session for disconnecting user if token is invalid
        
    Returns:
        Dict containing the post response with 'id' and other fields
        
    Raises:
        PlatformPostError: If posting fails
    """
    # Validate token before posting
    is_valid, error_msg = validate_x_token(access_token)
    if not is_valid:
        # Disconnect user if we have the social profile and database session
        if social_profile and db:
            social_profile.status = "disconnected"
            social_profile.access_token = None
            db.commit()
        raise PlatformPostError(f"X token validation failed: {error_msg}")
    
    try:
        # Upload media if provided
        media_ids = []
        if media_data and media_type:
            media_id = upload_media_to_x(media_data, media_type, access_token)
            media_ids.append(media_id)
        
        # Twitter API v2 endpoint for creating tweets
        url = "https://api.twitter.com/2/tweets"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload: Dict[str, Any] = {
            "text": content
        }
        
        # Add media if we have media_ids
        if media_ids:
            payload["media"] = {
                "media_ids": media_ids
            }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for errors in the response body (Twitter API can return errors even with 200 status)
        if "errors" in result:
            error_details = result.get("errors", [])
            error_messages = [str(err) for err in error_details]
            raise PlatformPostError(f"Twitter API returned errors: {', '.join(error_messages)}")
        
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
            status_code = e.response.status_code
            error_msg += f" (HTTP {status_code})"
            
            # Provide specific message for authentication errors
            if status_code == 401:
                error_msg = f"Authentication failed: Invalid or expired access token for X (Twitter) API"
                # Disconnect user if we have the social profile and database session
                if social_profile and db:
                    social_profile.status = "disconnected"
                    social_profile.access_token = None
                    db.commit()
            
            # Try to extract detailed error from response body
            try:
                error_detail = e.response.json()
                if isinstance(error_detail, dict):
                    # Twitter API v2 error format
                    if "errors" in error_detail:
                        error_messages = [err.get("message", str(err)) for err in error_detail["errors"]]
                        error_msg += f" - {', '.join(error_messages)}"
                    elif "detail" in error_detail:
                        error_msg += f" - {error_detail['detail']}"
                    else:
                        error_msg += f" - {error_detail}"
                else:
                    error_msg += f" - {error_detail}"
            except Exception:
                # If we can't parse JSON, include the raw response text if available
                try:
                    response_text = e.response.text[:200]  # Limit length
                    if response_text:
                        error_msg += f" - Response: {response_text}"
                except Exception:
                    pass
        
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
    
    # Find the social profile for this user and platform
    # If business_id is provided, prefer profiles associated with that business
    # Otherwise, use any profile for the user on this platform
    query = db.query(models.SocialProfile).filter(
        models.SocialProfile.user_id == scheduled_post.user_id,
        models.SocialProfile.platform == scheduled_post.platform,
        models.SocialProfile.status == "connected"
    )
    
    # If business_id is provided, prefer profiles for that business
    if scheduled_post.business_id:
        query = query.filter(models.SocialProfile.business_id == scheduled_post.business_id)
    
    social_profile = query.first()
    
    if not social_profile:
        business_msg = f" for business {scheduled_post.business_id}" if scheduled_post.business_id else ""
        raise PlatformPostError(
            f"No connected social profile found for user {scheduled_post.user_id}{business_msg} "
            f"on platform {scheduled_post.platform.value}"
        )
    
    if not social_profile.access_token:
        raise PlatformPostError(
            f"No access token found for social profile {social_profile.id}"
        )
    
    # Get media data from Azure Storage if media_asset_id is present
    media_data = None
    media_type = None
    if scheduled_post.media_asset_id:
        media_asset = db.get(models.MediaAsset, scheduled_post.media_asset_id)
        if media_asset:
            # Extract container and blob name from storage_url
            # Format: "{container_name}/{userId}/{filename}"
            # Container name comes from AZURE_STORAGE_USER_MEDIA_CONTAINER_NAME config
            storage_url_parts = media_asset.storage_url.split("/", 1)
            if len(storage_url_parts) == 2:
                container_name = storage_url_parts[0]
                blob_name = storage_url_parts[1]  # This is {userId}/{filename}
            else:
                # Fallback: assume it's in the default container
                container_name = None
                blob_name = media_asset.storage_url
            
            # Fetch media from Azure Storage
            media_data = storage_service.get_blob(blob_name, container_name=container_name)
            # add logger line to print out media_data
            logger.info(f"Media data: {media_data}")
            if media_data:
                media_type = media_asset.mime_type
            else:
                raise PlatformPostError(
                    f"Failed to retrieve media from storage: {media_asset.storage_url}"
                )
    
    # Post to X platform
    try:
        if scheduled_post.platform != models.PlatformEnum.x:
            raise PlatformPostError(
                f"Only X (Twitter) platform is supported. Platform {scheduled_post.platform.value} is not supported."
            )
        
        result = post_to_x(
            content=scheduled_post.content,
            access_token=social_profile.access_token,
            media_data=media_data,
            media_type=media_type,
            social_profile=social_profile,
            db=db
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
        # add logger line to print out the error
        logger.error(f"Error posting scheduled post {scheduled_post.id}: {str(e)}")
        raise PlatformPostError(str(e)) from e

