"""
Authentication utilities for JWT and OAuth.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app import models, schemas

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Email from token if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT token from request
        db: Database session
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        
    Returns:
        User model if authenticated, None otherwise
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Google OAuth2 helpers (skeleton implementation)
class GoogleOAuth:
    """Google OAuth2 helper class."""
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    def get_authorization_url(self) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Returns:
            Authorization URL string
        """
        # In production, use google-auth-oauthlib
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        # Build URL with params
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_str}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Dictionary containing token information
        """
        # In production, implement actual token exchange
        # For MVP, return mock data
        return {
            "access_token": "mock_access_token",
            "id_token": "mock_id_token",
            "email": "demo@neurohabit.com",
            "name": "Demo User"
        }
    
    async def get_user_info(self, access_token: str) -> dict:
        """
        Get user information from Google.
        
        Args:
            access_token: Google access token
            
        Returns:
            Dictionary containing user information
        """
        # In production, call Google's userinfo endpoint
        return {
            "email": "demo@neurohabit.com",
            "name": "Demo User",
            "google_id": "mock_google_id_123"
        }


google_oauth = GoogleOAuth()
