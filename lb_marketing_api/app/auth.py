from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .db import get_db
from . import models
from .config import settings

# JWT settings
SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"verify_token: Token decoded successfully, user_id: {payload.get('sub')}")
        return payload
    except JWTError as e:
        # Log the actual error for debugging
        logger.warning(f"verify_token: JWT verification failed - {str(e)}")
        logger.debug(f"verify_token: SECRET_KEY length: {len(SECRET_KEY) if SECRET_KEY else 0}")
        return None
    except Exception as e:
        logger.error(f"verify_token: Unexpected error - {type(e).__name__}: {str(e)}")
        return None

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """Get the current authenticated user from the JWT token."""
    import logging
    logger = logging.getLogger(__name__)
    
    if credentials is None:
        logger.warning("get_current_user: No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    logger.info(f"get_current_user: Token received (length: {len(token) if token else 0})")
    logger.debug(f"get_current_user: Token preview: {token[:20] if token else 'None'}...")
    
    payload = verify_token(token)
    
    if payload is None:
        logger.error("get_current_user: Token verification failed - check logs above for details")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials - token verification failed. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # JWT 'sub' is stored as a string, so we need to convert it back to int
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        logger.warning("get_current_user: No user_id in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials - no user_id in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert string user_id back to integer
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        logger.warning(f"get_current_user: Invalid user_id format in token: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials - invalid user_id format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None or not user.is_active:
        logger.warning(f"get_current_user: User {user_id} not found or inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"get_current_user: Successfully authenticated user {user_id} ({user.email})")
    return user

