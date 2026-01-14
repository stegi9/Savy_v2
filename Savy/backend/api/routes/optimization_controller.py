"""
Controller (API Router) for optimization opportunities.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
import structlog

from db.database import get_db
from repositories.optimization_repository import OptimizationRepository
from services.optimization_service import OptimizationService
from api.dependencies.auth import get_current_user
from models.user import User

logger = structlog.get_logger()

router = APIRouter(prefix="/optimizations", tags=["optimizations"])


class OptimizationScanRequest(BaseModel):
    """Request body for optimization scan."""
    categories: Optional[List[str]] = Field(
        None,
        description="Categories to scan (e.g., 'energy', 'telco')"
    )


class OptimizationScanResponse(BaseModel):
    """Response with optimization scan results."""
    success: bool
    data: dict


@router.post("/scan", response_model=OptimizationScanResponse)
async def scan_optimizations(
    request: OptimizationScanRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Scan user's recurring bills for optimization opportunities.
    
    - **categories**: Optional list of categories to scan (energy, telco, gas, insurance)
    """
    try:
        logger.info(
            "optimization_scan_request",
            user_id=current_user.id,
            categories=request.categories
        )
        
        # Initialize repository and service
        optimization_repository = OptimizationRepository(db)
        optimization_service = OptimizationService(optimization_repository)
        
        # Scan for optimizations
        result = optimization_service.scan_for_optimizations(
            user_id=current_user.id,
            categories=request.categories
        )
        
        logger.info(
            "optimization_scan_success",
            user_id=current_user.id,
            opportunities_found=result.get('opportunities_found', 0),
            total_savings=result.get('total_monthly_savings', 0)
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(
            "optimization_scan_failed",
            error=str(e),
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la scansione: {str(e)}"
        )


@router.get("/leads", response_model=OptimizationScanResponse)
async def get_optimization_leads(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all optimization leads for a user.
    
    - **user_id**: The ID of the user
    """
    try:
        logger.info("get_optimization_leads_request", user_id=user_id)
        
        # Initialize repository and service
        optimization_repository = OptimizationRepository(db)
        optimization_service = OptimizationService(optimization_repository)
        
        # Get leads
        leads = optimization_service.get_user_optimization_leads(user_id)
        
        logger.info(
            "get_optimization_leads_success",
            user_id=user_id,
            leads_count=len(leads)
        )
        
        return {
            "success": True,
            "data": {
                "leads": leads,
                "count": len(leads)
            }
        }
        
    except Exception as e:
        logger.error(
            "get_optimization_leads_failed",
            error=str(e),
            user_id=user_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Errore nel recupero delle opportunità: {str(e)}"
        )

