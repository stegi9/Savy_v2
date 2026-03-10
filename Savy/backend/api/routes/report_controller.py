"""
Controller (API Router) for spending reports.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
import structlog

from db.database import get_db
from repositories.report_repository import ReportRepository
from repositories.user_repository import UserRepository
from services.report_service import ReportService
from schemas import SpendingReportResponse
from api.dependencies.auth import get_current_user
from models.user import User

logger = structlog.get_logger()

router = APIRouter(prefix="/reports", tags=["reports"])


class SpendingReportRequest(BaseModel):
    """Request body for spending report."""
    period: str = Field("monthly", description="Report period: weekly, monthly, yearly, or custom")
    start_date: Optional[date] = Field(None, description="Start date for custom period")
    end_date: Optional[date] = Field(None, description="End date for custom period")
    bank_account_id: Optional[str] = Field(None, description="Filter by specific bank account ID")


@router.post("/spending", response_model=SpendingReportResponse)
async def get_spending_report(
    request: SpendingReportRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a spending report for the user.
    
    - **period**: Report period (weekly, monthly, yearly) - defaults to monthly
    """
    try:
        logger.info("get_spending_report_request", user_id=current_user.id, period=request.period)
        
        # Validate period
        # Validate period
        if request.period not in ["weekly", "monthly", "yearly", "custom"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period '{request.period}'. Must be: weekly, monthly, yearly, or custom"
            )
            
        # Parse dates if provided
        start_date = None
        end_date = None
        if request.start_date:
            start_date = datetime.combine(request.start_date, datetime.min.time())
        if request.end_date:
            end_date = datetime.combine(request.end_date, datetime.max.time())
        
        # Initialize repositories and service
        report_repository = ReportRepository(db)
        user_repository = UserRepository(db)
        report_service = ReportService(report_repository, user_repository)
        
        # Generate report
        report = report_service.generate_spending_report(
            user_id=current_user.id,
            period=request.period,
            start_date=start_date,
            end_date=end_date,
            bank_account_id=request.bank_account_id
        )
        
        logger.info(
            "get_spending_report_success",
            user_id=current_user.id,
            user_email=current_user.email,
            period=request.period,
            total_spent=report['total_spent'],
            total_income=report['total_income']
        )
        
        return {"success": True, "data": report}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_spending_report_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=500,
            detail=f"Errore nella generazione del report: {str(e)}"
        )


