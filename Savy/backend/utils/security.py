"""
Security utilities for JWT authentication, password reset, and email verification.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
import secrets
from passlib.context import CryptContext
from config import settings

# Password hashing context - using argon2 (more modern and reliable than bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token (short-lived).
    
    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        expires_delta: Token expiration time (defaults to 15 minutes)
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Access token expiration from settings
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> Tuple[str, datetime]:
    """
    Create a JWT refresh token (long-lived).
    
    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        
    Returns:
        Tuple of (encoded JWT token, expiration datetime)
    """
    to_encode = data.copy()
    
    # Long-lived refresh token (30 days)
    expire = datetime.utcnow() + timedelta(days=30)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt, expire


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        User ID from token subject, or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Verify it's an access token
        if payload.get("type") != "access":
            return None
            
        user_id: str = payload.get("sub")
        return user_id
    except jwt.PyJWTError:
        return None


def decode_refresh_token(token: str) -> Optional[str]:
    """
    Decode and verify a JWT refresh token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        User ID from token subject, or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None
            
        user_id: str = payload.get("sub")
        return user_id
    except jwt.PyJWTError:
        return None


def generate_verification_token() -> str:
    """
    Generate a secure random token for email verification or password reset.
    
    Returns:
        32-character random token
    """
    return secrets.token_urlsafe(32)


def create_password_reset_token() -> Tuple[str, datetime]:
    """
    Create a password reset token.
    
    Returns:
        Tuple of (token, expiration datetime)
    """
    token = generate_verification_token()
    expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    return token, expires


def create_email_verification_token() -> Tuple[str, datetime]:
    """
    Create an email verification token.
    
    Returns:
        Tuple of (token, expiration datetime)
    """
    token = generate_verification_token()
    expires = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    return token, expires

