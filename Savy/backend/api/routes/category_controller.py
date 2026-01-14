"""
Category controller (FastAPI router).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from services.category_service import CategoryService
from schemas import UserCategoryCreate, UserCategoryUpdate, UserCategoryResponse
from api.dependencies.auth import get_current_user
from models.user import User
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/categories", tags=["Categories"])


from fastapi import APIRouter, Depends, HTTPException, status, Query

@router.get("", response_model=List[UserCategoryResponse])
async def get_categories(
    type: Optional[str] = Query(None, description="Filter by category type (expense/income)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all categories for the current user.
    
    Returns both system categories and user-defined custom categories.
    """
    logger.info("get_categories_request", user_id=current_user.id)
    
    try:
        service = CategoryService(db)
        categories = service.get_all_categories(current_user.id, category_type=type)
        return categories
        
    except Exception as e:
        logger.error("get_categories_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nel recupero categorie: {str(e)}"
        )


@router.post("", response_model=UserCategoryResponse)
async def create_category(
    request: UserCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new custom category for the user.
    """
    logger.info("create_category_request", user_id=current_user.id, category_name=request.name)
    
    try:
        service = CategoryService(db)
        new_category = service.create_category(
            user_id=current_user.id,
            name=request.name,
            icon=request.icon,
            color=request.color,
            category_type=request.category_type,
            budget_monthly=request.budget_monthly
        )
        
        return new_category
        
    except Exception as e:
        logger.error("create_category_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nella creazione categoria: {str(e)}"
        )


@router.put("/{category_id}", response_model=UserCategoryResponse)
async def update_category(
    category_id: str,
    request: UserCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing category.
    """
    logger.info("update_category_request", user_id=current_user.id, category_id=category_id)
    
    try:
        service = CategoryService(db)
        updated_category = service.update_category(
            category_id=category_id,
            user_id=current_user.id,
            name=request.name,
            icon=request.icon,
            color=request.color,
            budget_monthly=request.budget_monthly
        )
        
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria non trovata"
            )
        
        return updated_category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_category_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nell'aggiornamento categoria: {str(e)}"
        )


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a custom category (system categories cannot be deleted).
    """
    logger.info("delete_category_request", user_id=current_user.id, category_id=category_id)
    
    try:
        service = CategoryService(db)
        success = service.delete_category(category_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria non trovata"
            )
        
        return {"success": True, "message": "Categoria eliminata con successo"}
        
    except ValueError as e:
        logger.error("delete_category_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_category_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nell'eliminazione categoria: {str(e)}"
        )


