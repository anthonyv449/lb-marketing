
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import requests
import secrets
from urllib.parse import urlencode

from ..db import get_db
from .. import models
from ..config import settings
from ..auth import get_current_user

router = APIRouter(prefix="/oauth", tags=["oauth"])

# In-memory storage for OAuth state (in production, use Redis or similar)
# Format: {state: {"user_id": int, "business_id": int}}
oauth_states = {}

def get_or_create_user_business(user: models.User, db: Session) -> models.Business:
    """Get the user's first business or create a default one."""
    business = db.query(models.Business).filter(models.Business.user_id == user.id).first()
    if not business:
        # Create a default business for the user
        business = models.Business(
            user_id=user.id,
            name=f"{user.email.split('@')[0]}'s Business",
            email=user.email
        )
        db.add(business)
        db.commit()
        db.refresh(business)
    return business

@router.get("/x/authorize")
def authorize_x(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate X (Twitter) OAuth 2.0 authorization flow.
    Redirects user to Twitter's authorization page.
    """
    if not settings.TWITTER_CLIENT_ID or not settings.TWITTER_CLIENT_SECRET:
        raise HTTPException(500, "Twitter OAuth credentials not configured")
    
    # Get or create business for user
    business = get_or_create_user_business(current_user, db)
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"user_id": current_user.id, "business_id": business.id}
    
    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": settings.TWITTER_CLIENT_ID,
        "redirect_uri": settings.TWITTER_REDIRECT_URI,
        "scope": "tweet.read tweet.write users.read offline.access",
        "state": state,
        "code_challenge": "challenge",  # Simplified - should use PKCE in production
        "code_challenge_method": "plain"
    }
    
    auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(auth_params)}"
    return RedirectResponse(url=auth_url)

@router.get("/x/callback")
def x_callback(
    code: str = Query(..., description="Authorization code from Twitter"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from Twitter.
    Exchanges authorization code for access token and stores it.
    """
    # Verify state
    if state not in oauth_states:
        raise HTTPException(400, "Invalid state parameter")
    
    state_data = oauth_states.pop(state)
    user_id = state_data["user_id"]
    business_id = state_data["business_id"]
    
    if not settings.TWITTER_CLIENT_ID or not settings.TWITTER_CLIENT_SECRET:
        raise HTTPException(500, "Twitter OAuth credentials not configured")
    
    # Exchange code for token
    token_url = "https://api.twitter.com/2/oauth2/token"
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": settings.TWITTER_CLIENT_ID,
        "redirect_uri": settings.TWITTER_REDIRECT_URI,
        "code_verifier": "challenge"  # Should match code_challenge from authorize
    }
    
    # Use Basic Auth for client credentials
    import base64
    credentials = f"{settings.TWITTER_CLIENT_ID}:{settings.TWITTER_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    try:
        response = requests.post(token_url, data=token_data, headers=headers)
        response.raise_for_status()
        token_response = response.json()
        access_token = token_response.get("access_token")
        
        if not access_token:
            raise HTTPException(400, "Failed to obtain access token")
        
        # Get user info to retrieve handle
        user_info_url = "https://api.twitter.com/2/users/me"
        user_headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(user_info_url, headers=user_headers)
        
        handle = "unknown"
        external_id = None
        if user_response.status_code == 200:
            user_data = user_response.json()
            if "data" in user_data:
                handle = user_data["data"].get("username", "unknown")
                external_id = user_data["data"].get("id")
        
        # Check if social profile already exists for this user and platform
        existing_profile = db.query(models.SocialProfile).filter(
            models.SocialProfile.user_id == user_id,
            models.SocialProfile.platform == models.PlatformEnum.x
        ).first()
        
        if existing_profile:
            # Update existing profile
            existing_profile.access_token = access_token
            existing_profile.handle = handle
            existing_profile.external_id = external_id
            existing_profile.status = "connected"
            existing_profile.business_id = business_id
        else:
            # Create new social profile
            new_profile = models.SocialProfile(
                user_id=user_id,
                business_id=business_id,
                platform=models.PlatformEnum.x,
                handle=handle,
                external_id=external_id,
                access_token=access_token,
                status="connected"
            )
            db.add(new_profile)
        
        db.commit()
        
        # Redirect to frontend with success indicator
        # In production, you'd want to use your actual frontend URL from settings
        frontend_url = "http://localhost:5173"  # Default Vite dev server
        return RedirectResponse(url=f"{frontend_url}?oauth=success")
        
    except requests.RequestException as e:
        error_msg = f"Failed to exchange token: {str(e)}"
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        db.rollback()
        error_msg = f"Error processing OAuth callback: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/x/status")
def x_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if X (Twitter) is connected for the current user.
    Returns connection status and handle if connected.
    """
    profile = db.query(models.SocialProfile).filter(
        models.SocialProfile.user_id == current_user.id,
        models.SocialProfile.platform == models.PlatformEnum.x
    ).first()
    
    if profile and profile.status == "connected" and profile.access_token:
        return {
            "connected": True,
            "handle": profile.handle
        }
    else:
        return {
            "connected": False,
            "handle": None
        }

@router.get("/status")
def get_all_platform_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get connection status for all platforms for the current user.
    Returns a dictionary mapping platform names to their connection status.
    """
    profiles = db.query(models.SocialProfile).filter(
        models.SocialProfile.user_id == current_user.id,
        models.SocialProfile.status == "connected"
    ).all()
    
    # Create a dictionary of all platforms
    status_map = {}
    for platform in models.PlatformEnum:
        status_map[platform.value] = {
            "connected": False,
            "handle": None
        }
    
    # Update with actual connected profiles
    for profile in profiles:
        if profile.access_token:
            status_map[profile.platform.value] = {
                "connected": True,
                "handle": profile.handle
            }
    
    return status_map

@router.post("/{platform}/disconnect")
def disconnect_platform(
    platform: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect a platform for the current user by setting status to 'disconnected'
    and clearing the access token.
    """
    try:
        platform_enum = models.PlatformEnum(platform)
    except ValueError as e:
        error_msg = f"Invalid platform: {platform} - {str(e)}"
        raise HTTPException(status_code=400, detail=error_msg)
    
    profile = db.query(models.SocialProfile).filter(
        models.SocialProfile.user_id == current_user.id,
        models.SocialProfile.platform == platform_enum
    ).first()
    
    if not profile:
        raise HTTPException(404, f"No profile found for platform {platform}")
    
    profile.status = "disconnected"
    profile.access_token = None
    db.commit()
    
    return {
        "success": True,
        "message": f"Disconnected from {platform}"
    }

@router.get("/{platform}/authorize")
def authorize_platform(
    platform: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generic authorize endpoint. Currently only supports 'x' platform.
    Other platforms will return a not implemented error.
    """
    if platform == "x":
        return authorize_x(current_user, db)
    else:
        raise HTTPException(501, f"OAuth for platform '{platform}' is not yet implemented")

@router.get("/{platform}/status")
def platform_status(
    platform: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check connection status for a specific platform for the current user.
    """
    try:
        platform_enum = models.PlatformEnum(platform)
    except ValueError as e:
        error_msg = f"Invalid platform: {platform} - {str(e)}"
        raise HTTPException(status_code=400, detail=error_msg)
    
    profile = db.query(models.SocialProfile).filter(
        models.SocialProfile.user_id == current_user.id,
        models.SocialProfile.platform == platform_enum
    ).first()
    
    if profile and profile.status == "connected" and profile.access_token:
        return {
            "connected": True,
            "handle": profile.handle
        }
    else:
        return {
            "connected": False,
            "handle": None
        }

