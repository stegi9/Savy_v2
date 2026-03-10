"""
Authentication controller.
Handles user registration, login, token refresh, password reset, and email verification.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from db.database import get_db
from repositories.user_repository import UserRepository
from utils.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    decode_refresh_token,
    create_password_reset_token,
    create_email_verification_token
)
from utils.exceptions import DuplicateEmailException, InvalidCredentialsException
from api.dependencies.auth import get_current_user
from schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ProfileResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    ResendVerificationRequest,
    FCMTokenUpdate
)
from models.user import User
from config import settings
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Password requirements enforced via Pydantic validation:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    
    Args:
        request: Registration data (email, password, full_name)
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        JWT access token + refresh token
        
    Raises:
        HTTPException 409: If email already exists
        HTTPException 422: If validation fails
    """
    logger.info("registration_attempt", email=request.email)
    
    user_repo = UserRepository(db)
    
    # Check if email already exists
    existing_user = user_repo.get_by_email(request.email)
    if existing_user:
        logger.warning("registration_failed_duplicate_email", email=request.email)
        raise DuplicateEmailException(request.email)
    
    # Hash password and create user
    hashed_password = hash_password(request.password)
    
    # Create email verification token
    verification_token, verification_expires = create_email_verification_token()
    
    try:
        user = user_repo.create({
            "email": request.email,
            "hashed_password": hashed_password,
            "full_name": request.full_name,
            "current_balance": 0.00,
            "monthly_budget": 2000.00,
            "currency": "EUR",
            "email_verified": False,
            "email_verification_token": verification_token,
            "email_verification_expires": verification_expires
        })
        
        # Initialize default categories
        from repositories.category_repository import CategoryRepository
        category_repo = CategoryRepository(db)
        category_repo.initialize_system_categories(user.id)
        
        logger.info("registration_successful", user_id=user.id, email=request.email)
        
        # Send verification email in background
        background_tasks.add_task(send_verification_email, request.email, verification_token)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token, refresh_expires = create_refresh_token(data={"sub": user.id})
        
        # Store refresh token
        user_repo.update(user.id, {
            "refresh_token": refresh_token,
            "refresh_token_expires": refresh_expires
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user_id=user.id
        )
    
    except Exception as e:
        logger.error("registration_failed", email=request.email, error=str(e))
        raise


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access + refresh tokens.
    
    Args:
        request: Login credentials (email, password)
        db: Database session
        
    Returns:
        JWT access token + refresh token
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    logger.info("login_attempt", email=request.email)
    
    user_repo = UserRepository(db)
    
    # Get user by email
    user = user_repo.get_by_email(request.email)
    
    if not user:
        logger.warning("login_failed_user_not_found", email=request.email)
        raise InvalidCredentialsException()
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        logger.warning("login_failed_invalid_password", email=request.email)
        raise InvalidCredentialsException()
    
    logger.info("login_successful", user_id=user.id, email=request.email)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token, refresh_expires = create_refresh_token(data={"sub": user.id})
    
    # Store refresh token in database
    user_repo.update(user.id, {
        "refresh_token": refresh_token,
        "refresh_token_expires": refresh_expires
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user.id
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        db: Database session
        
    Returns:
        New access token
        
    Raises:
        HTTPException 401: If refresh token is invalid or expired
    """
    user_id = decode_refresh_token(request.refresh_token)
    
    if not user_id:
        logger.warning("refresh_failed_invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user or user.refresh_token != request.refresh_token:
        logger.warning("refresh_failed_token_mismatch", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token is expired
    if user.refresh_token_expires and user.refresh_token_expires < datetime.utcnow():
        logger.warning("refresh_failed_token_expired", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired. Please login again."
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": user.id})
    
    logger.info("token_refreshed", user_id=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Return same refresh token
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset. Sends email with reset token.
    
    Args:
        request: Password reset request (email)
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Success message (always, even if email doesn't exist for security)
    """
    logger.info("password_reset_requested", email=request.email)
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(request.email)
    
    if user:
        # Generate reset token
        reset_token, reset_expires = create_password_reset_token()
        
        # Store token in database
        user_repo.update(user.id, {
            "password_reset_token": reset_token,
            "password_reset_expires": reset_expires
        })
        
        # Send reset email in background
        background_tasks.add_task(send_password_reset_email, request.email, reset_token)
        
        logger.info("password_reset_token_created", user_id=user.id)
    else:
        # Don't reveal if email exists
        logger.warning("password_reset_email_not_found", email=request.email)
    
    return {"message": "If the email exists, a password reset link has been sent."}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token and new password.
    
    Args:
        request: Reset token + new password
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException 400: If token is invalid or expired
    """
    logger.info("password_reset_confirmation_attempt")
    
    user_repo = UserRepository(db)
    
    # Find user by reset token
    user = db.query(User).filter(User.password_reset_token == request.token).first()
    
    if not user:
        logger.warning("password_reset_invalid_token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Check if token is expired
    if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
        logger.warning("password_reset_token_expired", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token expired. Please request a new one."
        )
    
    # Hash new password
    hashed_password = hash_password(request.new_password)
    
    # Update password and clear reset token
    user_repo.update(user.id, {
        "hashed_password": hashed_password,
        "password_reset_token": None,
        "password_reset_expires": None
    })
    
    logger.info("password_reset_successful", user_id=user.id)
    
    return {"message": "Password reset successful. Please login with your new password."}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token.
    
    Args:
        request: Email verification token
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException 400: If token is invalid or expired
    """
    logger.info("email_verification_attempt")
    
    user_repo = UserRepository(db)
    
    # Find user by verification token
    user = db.query(User).filter(User.email_verification_token == request.token).first()
    
    if not user:
        logger.warning("email_verification_invalid_token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Check if token is expired
    if user.email_verification_expires and user.email_verification_expires < datetime.utcnow():
        logger.warning("email_verification_token_expired", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token expired. Please request a new one."
        )
    
    # Mark email as verified
    user_repo.update(user.id, {
        "email_verified": True,
        "email_verification_token": None,
        "email_verification_expires": None
    })
    
    logger.info("email_verified_successful", user_id=user.id)
    
    return {"message": "Email verified successfully!"}


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Resend email verification link.
    
    Args:
        request: Resend verification request (email)
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Success message
    """
    logger.info("verification_resend_requested", email=request.email)
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(request.email)
    
    if user and not user.email_verified:
        # Generate new verification token
        verification_token, verification_expires = create_email_verification_token()
        
        # Update token in database
        user_repo.update(user.id, {
            "email_verification_token": verification_token,
            "email_verification_expires": verification_expires
        })
        
        # Send verification email in background
        background_tasks.add_task(send_verification_email, request.email, verification_token)
        
        logger.info("verification_email_resent", user_id=user.id)
    
    return {"message": "If the email exists and is unverified, a verification link has been sent."}


@router.post("/fcm-token", status_code=status.HTTP_200_OK)
async def update_fcm_token(
    request: FCMTokenUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's FCM token for push notifications.
    
    Args:
        request: FCM token
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    user_repo = UserRepository(db)
    
    user_repo.update(current_user.id, {
        "fcm_token": request.fcm_token
    })
    
    logger.info("fcm_token_updated", user_id=current_user.id)
    
    return {"message": "FCM token updated successfully"}


# ============================================================================
# EMAIL SENDING FUNCTIONS (Background Tasks)
# ============================================================================

async def send_verification_email(email: str, token: str):
    """
    Send email verification link.
    
    TODO: Implement with actual email service (SendGrid, SES, etc.)
    """
    verification_link = f"{settings.frontend_url}/verify-email?token={token}"
    
    logger.info("sending_verification_email", email=email, link=verification_link)
    
    # TODO: Integrate with email service
    # For now, just log the link
    print(f"📧 Verification Email for {email}:")
    print(f"   Link: {verification_link}")


async def send_password_reset_email(email: str, token: str):
    """
    Send password reset link.
    
    TODO: Implement with actual email service (SendGrid, SES, etc.)
    """
    reset_link = f"{settings.frontend_url}/reset-password?token={token}"
    
    logger.info("sending_password_reset_email", email=email, link=reset_link)
    
    # TODO: Integrate with email service
    # For now, just log the link
    print(f"📧 Password Reset Email for {email}:")
    print(f"   Link: {reset_link}")


