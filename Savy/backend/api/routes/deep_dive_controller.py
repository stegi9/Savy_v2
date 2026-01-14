"""
Deep Dive Analytics Controller.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import structlog

from db.database import get_db
from api.dependencies.auth import get_current_user
from models.user import User
from schemas import DeepDiveRequest, DeepDiveResponse
from services.deep_dive_service import DeepDiveService
from repositories.report_repository import ReportRepository
from repositories.category_repository import CategoryRepository

logger = structlog.get_logger()

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/deep-dive", response_model=DeepDiveResponse)
async def get_deep_dive_analytics(
    request: DeepDiveRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get deep dive analytics with AI insights.
    
    Provides advanced analytics including:
    - Category comparisons with previous period
    - Spending velocity and projections
    - Trend data for visualizations
    - AI-generated insights
    """
    logger.info(
        "deep_dive_request",
        user_id=current_user.id,
        period=request.period
    )
    
    try:
        # Initialize repositories and service
        report_repo = ReportRepository(db)
        category_repo = CategoryRepository(db)
        service = DeepDiveService(report_repo, category_repo)
        
        # Generate analytics
        analytics = service.generate_deep_dive(
            user_id=current_user.id,
            period=request.period
        )
        
        logger.info(
            "deep_dive_generated",
            user_id=current_user.id,
            period=request.period,
            total_spent=analytics['total_spent'],
            insights_count=len(analytics['ai_insights'])
        )
        
        return {
            "success": True,
            "data": analytics
        }
        
    except Exception as e:
        logger.error(
            "deep_dive_failed",
            error=str(e),
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la generazione dell'analisi: {str(e)}"
        )


