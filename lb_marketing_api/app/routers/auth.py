from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas
from ..auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = models.User(
        email=payload.email,
        full_name=payload.full_name
    )
    print("payload.password", payload.password)
    user.set_password(payload.password)
    print("user", user)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        error_msg = f"Could not create user: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    return user

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    # JWT 'sub' (subject) must be a string, so convert user.id to string
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=schemas.UserOut)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

