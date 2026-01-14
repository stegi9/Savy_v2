"""
User settings controller.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from db.database import get_db
from schemas import UserSettingsUpdate, UserSettingsResponse, StandardResponse
from repositories.user_repository import UserRepository
from api.dependencies.auth import get_current_user
from models.user import User

logger = structlog.get_logger()

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's settings."""
    user_repo = UserRepository(db)
    settings = user_repo.get_settings(current_user.id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return settings


@router.patch("/settings", response_model=StandardResponse)
async def update_user_settings(
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's settings."""
    user_repo = UserRepository(db)
    
    # Convert to dict and filter None values
    update_data = settings.model_dump(exclude_none=True)
    
    if not update_data:
        return StandardResponse(
            success=True,
            message="No changes provided"
        )
    
    # Convert Decimal to float for DB
    if "current_balance" in update_data:
        update_data["current_balance"] = float(update_data["current_balance"])
    if "monthly_budget" in update_data:
        update_data["monthly_budget"] = float(update_data["monthly_budget"])
    
    updated_user = user_repo.update_settings(current_user.id, update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info("User settings updated", user_id=current_user.id, updates=list(update_data.keys()))
    
    return StandardResponse(
        success=True,
        message="Settings updated successfully",
        data=user_repo.get_settings(current_user.id)
    )

