"""
Recurring Bills controller - CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import structlog

from db.database import get_db
from schemas import BillCreate, BillResponse, StandardResponse
from repositories.recurring_bill_repository import RecurringBillRepository
from api.dependencies.auth import get_current_user
from models.user import User

logger = structlog.get_logger()

router = APIRouter(prefix="/bills", tags=["Recurring Bills"])


@router.get("", response_model=List[BillResponse])
async def get_user_bills(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all recurring bills for the current user."""
    bill_repo = RecurringBillRepository(db)
    
    if active_only:
        bills = bill_repo.get_active_bills(current_user.id)
    else:
        bills = bill_repo.get_by_user(current_user.id)
    
    return [
        BillResponse(
            id=bill.id,
            user_id=bill.user_id,
            name=bill.name,
            amount=float(bill.amount),
            due_day=bill.due_day or 1,
            category=bill.category or "other",
            provider=bill.provider,
            is_active=bill.is_active,
            created_at=bill.created_at
        )
        for bill in bills
    ]


@router.post("", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_data: BillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recurring bill."""
    bill_repo = RecurringBillRepository(db)
    
    new_bill = bill_repo.create({
        "user_id": current_user.id,
        "name": bill_data.name,
        "amount": float(bill_data.amount),
        "due_day": bill_data.due_day,
        "category": bill_data.category,
        "provider": bill_data.provider,
        "is_active": bill_data.is_active
    })
    
    logger.info("Bill created", user_id=current_user.id, bill_id=new_bill.id)
    
    return BillResponse(
        id=new_bill.id,
        user_id=new_bill.user_id,
        name=new_bill.name,
        amount=float(new_bill.amount),
        due_day=new_bill.due_day or 1,
        category=new_bill.category or "other",
        provider=new_bill.provider,
        is_active=new_bill.is_active,
        created_at=new_bill.created_at
    )


@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific recurring bill."""
    bill_repo = RecurringBillRepository(db)
    bill = bill_repo.get_by_id(bill_id)
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    if bill.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this bill"
        )
    
    return BillResponse(
        id=bill.id,
        user_id=bill.user_id,
        name=bill.name,
        amount=float(bill.amount),
        due_day=bill.due_day or 1,
        category=bill.category or "other",
        provider=bill.provider,
        is_active=bill.is_active,
        created_at=bill.created_at
    )


@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: str,
    bill_data: BillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a recurring bill."""
    bill_repo = RecurringBillRepository(db)
    bill = bill_repo.get_by_id(bill_id)
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    if bill.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this bill"
        )
    
    updated_bill = bill_repo.update(bill_id, {
        "name": bill_data.name,
        "amount": float(bill_data.amount),
        "due_day": bill_data.due_day,
        "category": bill_data.category,
        "provider": bill_data.provider,
        "is_active": bill_data.is_active
    })
    
    logger.info("Bill updated", user_id=current_user.id, bill_id=bill_id)
    
    return BillResponse(
        id=updated_bill.id,
        user_id=updated_bill.user_id,
        name=updated_bill.name,
        amount=float(updated_bill.amount),
        due_day=updated_bill.due_day or 1,
        category=updated_bill.category or "other",
        provider=updated_bill.provider,
        is_active=updated_bill.is_active,
        created_at=updated_bill.created_at
    )


@router.delete("/{bill_id}", response_model=StandardResponse)
async def delete_bill(
    bill_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a recurring bill."""
    bill_repo = RecurringBillRepository(db)
    bill = bill_repo.get_by_id(bill_id)
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    if bill.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this bill"
        )
    
    bill_repo.delete(bill_id)
    logger.info("Bill deleted", user_id=current_user.id, bill_id=bill_id)
    
    return StandardResponse(
        success=True,
        message="Bill deleted successfully"
    )

