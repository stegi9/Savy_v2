"""
Authentication controller.
Handles user registration, login, and profile retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.user_repository import UserRepository
from utils.security import hash_password, verify_password, create_access_token
from api.dependencies.auth import get_current_user
from schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ProfileResponse
)
from models.user import User
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Args:
        request: Registration data (email, password, full_name)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException 400: If email already exists
    """
    user_repo = UserRepository(db)
    
    # Check if email already exists
    existing_user = user_repo.get_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = hash_password(request.password)
    
    user = user_repo.create({
        "email": request.email,
        "hashed_password": hashed_password,
        "full_name": request.full_name,
        "current_balance": 0.00,
        "monthly_budget": 2000.00,
        "currency": "EUR"
    })
    
    # Initialize default categories
    from repositories.category_repository import CategoryRepository
    category_repo = CategoryRepository(db)
    category_repo.initialize_system_categories(user.id)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 24 * 60 * 60  # 30 days in seconds
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token.
    
    Args:
        request: Login credentials (email, password)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    user_repo = UserRepository(db)
    
    # Get user by email
    user = user_repo.get_by_email(request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 24 * 60 * 60  # 30 days in seconds
    )


@router.get("/me", response_model=ProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current authenticated user's profile.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        User profile information
    """
    return ProfileResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        current_balance=float(current_user.current_balance),
        currency=current_user.currency,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

