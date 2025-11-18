
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import requests
import secrets
import hashlib
import base64
from urllib.parse import urlencode

from ..db import get_db
from .. import models
from ..config import settings
from ..auth import get_current_user

router = APIRouter(prefix="/oauth", tags=["oauth"])

# In-memory storage for OAuth state (in production, use Redis or similar)
# Format: {state: {"user_id": int, "business_id": int, "code_verifier": str}}
oauth_states = {}

def generate_pkce_pair():
    """
    Generate PKCE code verifier and challenge pair.
    Returns tuple: (code_verifier, code_challenge)
    """
    # Generate a random code verifier (43-128 characters, URL-safe)
    code_verifier = secrets.token_urlsafe(96)[:128]
    
    # Create code challenge using SHA256 hash and base64url encoding
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.rstrip('=')
    
    return code_verifier, code_challenge

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

def _build_x_authorization_url(current_user: models.User, db: Session) -> str:
    """
    Helper function to build X authorization URL.
    Returns the authorization URL string.
    """
    if not settings.TWITTER_CLIENT_ID or not settings.TWITTER_CLIENT_SECRET:
        raise HTTPException(500, "Twitter OAuth credentials not configured")
    
    # Get or create business for user
   
    
    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "user_id": current_user.id,
        
        "code_verifier": code_verifier
    }
    
    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": settings.TWITTER_CLIENT_ID,
        "redirect_uri": settings.TWITTER_REDIRECT_URI,
        "scope": "tweet.read tweet.write users.read offline.access",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(auth_params)}"
    return auth_url

@router.get("/x/authorize")
def authorize_x(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    return_url: bool = Query(False, description="Return URL as JSON instead of redirecting")
):
    """
    Initiate X (Twitter) OAuth 2.0 authorization flow.
    By default, redirects user to Twitter's authorization page.
    If return_url=true, returns the authorization URL as JSON.
    """
    auth_url = _build_x_authorization_url(current_user, db)
    
    if return_url:
        return {"authorization_url": auth_url}
    
    return RedirectResponse(url=auth_url)

@router.get("/x/callback")
def x_callback(
    code: str = Query(None, description="Authorization code from Twitter"),
    state: str = Query(None, description="State parameter for CSRF protection"),
    error: str = Query(None, description="Error from Twitter OAuth"),
    error_description: str = Query(None, description="Error description from Twitter OAuth"),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from Twitter.
    Exchanges authorization code for access token and stores it.
    """
    # Handle OAuth errors (user denied, etc.)
    if error:
        error_msg = error_description or error
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': error_msg})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    # Validate required parameters
    if not code or not state:
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': 'Missing authorization code or state parameter'})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    # Verify state
    if state not in oauth_states:
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': 'Invalid state parameter'})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    state_data = oauth_states.pop(state)
    user_id = state_data["user_id"]
    code_verifier = state_data.get("code_verifier")
    
    if not code_verifier:
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': 'Missing code_verifier in state'})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    # Get user and business (optional)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': 'User not found'})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    # Get existing business for user (optional - business_id can be None)
    # Only use existing business, don't create one if it doesn't exist
    business = db.query(models.Business).filter(models.Business.user_id == user.id).first()
    business_id = business.id if business else None
    
    if not settings.TWITTER_CLIENT_ID or not settings.TWITTER_CLIENT_SECRET:
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': 'Twitter OAuth credentials not configured'})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    # Exchange code for token
    token_url = "https://api.twitter.com/2/oauth2/token"
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": settings.TWITTER_CLIENT_ID,
        "redirect_uri": settings.TWITTER_REDIRECT_URI,
        "code_verifier": code_verifier
    }
    
    # Use Basic Auth for client credentials
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
            frontend_url = settings.FRONTEND_URL.rstrip('/')
            error_encoded = urlencode({'error': 'Failed to obtain access token from Twitter'})
            return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
        
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
            if business_id:
                existing_profile.business_id = business_id
        else:
            # Create new social profile
            profile_data = {
                "user_id": user_id,
                "platform": models.PlatformEnum.x,
                "handle": handle,
                "external_id": external_id,
                "access_token": access_token,
                "status": "connected"
            }
            if business_id:
                profile_data["business_id"] = business_id
            new_profile = models.SocialProfile(**profile_data)
            db.add(new_profile)
        
        db.commit()
        
        # Redirect to frontend with success indicator
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        return RedirectResponse(url=f"{frontend_url}?oauth=success&platform=x")
        
    except requests.RequestException as e:
        db.rollback()
        error_msg = f"Failed to exchange token: {str(e)}"
        # Redirect to frontend with error indicator
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': error_msg})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    except Exception as e:
        db.rollback()
        error_msg = f"Error processing OAuth callback: {str(e)}"
        # Redirect to frontend with error indicator
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': error_msg})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")

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

@router.get("/tiktok/authorize")
def authorize_tiktok(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    return_url: bool = Query(False, description="Return URL as JSON instead of redirecting")
):
    """
    Initiate TikTok OAuth 2.0 authorization flow.
    By default, redirects user to TikTok's authorization page.
    If return_url=true, returns the authorization URL as JSON.
    """
    if not settings.TIKTOK_CLIENT_ID or not settings.TIKTOK_CLIENT_SECRET:
        raise HTTPException(500, "TikTok OAuth credentials not configured")
    
    # Get or create business for user
    business = get_or_create_user_business(current_user, db)
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"user_id": current_user.id, "business_id": business.id}
    
    # Build authorization URL
    # TikTok OAuth 2.0 uses similar flow to Twitter
    auth_params = {
        "client_key": settings.TIKTOK_CLIENT_ID,
        "redirect_uri": settings.TIKTOK_REDIRECT_URI,
        "scope": "user.info.basic,video.upload,video.publish",
        "response_type": "code",
        "state": state,
    }
    
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(auth_params)}"
    
    if return_url:
        return {"authorization_url": auth_url}
    
    return RedirectResponse(url=auth_url)

@router.get("/tiktok/callback")
def tiktok_callback(
    code: str = Query(None, description="Authorization code from TikTok"),
    state: str = Query(None, description="State parameter for CSRF protection"),
    error: str = Query(None, description="Error from TikTok OAuth"),
    error_description: str = Query(None, description="Error description from TikTok OAuth"),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from TikTok.
    Exchanges authorization code for access token and stores it.
    """
    # Handle OAuth errors (user denied, etc.)
    if error:
        error_msg = error_description or error
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': error_msg})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    # Validate required parameters
    if not code or not state:
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': 'Missing authorization code or state parameter'})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    # Verify state
    if state not in oauth_states:
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': 'Invalid state parameter'})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    
    state_data = oauth_states.pop(state)
    user_id = state_data["user_id"]
    business_id = state_data["business_id"]
    
    if not settings.TIKTOK_CLIENT_ID or not settings.TIKTOK_CLIENT_SECRET:
        raise HTTPException(500, "TikTok OAuth credentials not configured")
    
    # Exchange code for token
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    token_data = {
        "client_key": settings.TIKTOK_CLIENT_ID,
        "client_secret": settings.TIKTOK_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.TIKTOK_REDIRECT_URI,
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    try:
        response = requests.post(token_url, data=token_data, headers=headers)
        response.raise_for_status()
        token_response = response.json()
        access_token = token_response.get("access_token")
        
        if not access_token:
            raise HTTPException(400, "Failed to obtain access token")
        
        # Get user info to retrieve handle
        user_info_url = "https://open.tiktokapis.com/v2/user/info/"
        user_headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(user_info_url, headers=user_headers)
        
        handle = "unknown"
        external_id = None
        if user_response.status_code == 200:
            user_data = user_response.json()
            if "data" in user_data and "user" in user_data["data"]:
                handle = user_data["data"]["user"].get("display_name", "unknown")
                external_id = user_data["data"]["user"].get("open_id")
        
        # Check if social profile already exists for this user and platform
        existing_profile = db.query(models.SocialProfile).filter(
            models.SocialProfile.user_id == user_id,
            models.SocialProfile.platform == models.PlatformEnum.tiktok
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
                platform=models.PlatformEnum.tiktok,
                handle=handle,
                external_id=external_id,
                access_token=access_token,
                status="connected"
            )
            db.add(new_profile)
        
        db.commit()
        
        # Redirect to frontend with success indicator
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        return RedirectResponse(url=f"{frontend_url}?oauth=success&platform=tiktok")
        
    except requests.RequestException as e:
        db.rollback()
        error_msg = f"Failed to exchange token: {str(e)}"
        # Redirect to frontend with error indicator
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': error_msg})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")
    except Exception as e:
        db.rollback()
        error_msg = f"Error processing OAuth callback: {str(e)}"
        # Redirect to frontend with error indicator
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        error_encoded = urlencode({'error': error_msg})
        return RedirectResponse(url=f"{frontend_url}?oauth=error&{error_encoded}")

@router.get("/tiktok/status")
def tiktok_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if TikTok is connected for the current user.
    Returns connection status and handle if connected.
    """
    profile = db.query(models.SocialProfile).filter(
        models.SocialProfile.user_id == current_user.id,
        models.SocialProfile.platform == models.PlatformEnum.tiktok
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
    db: Session = Depends(get_db),
    return_url: bool = Query(False, description="Return URL as JSON instead of redirecting")
):
    """
    Generic authorize endpoint. Currently supports 'x' and 'tiktok' platforms.
    Other platforms will return a not implemented error.
    """
    if platform == "x":
        return authorize_x(current_user, db, return_url)
    elif platform == "tiktok":
        return authorize_tiktok(current_user, db, return_url)
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

