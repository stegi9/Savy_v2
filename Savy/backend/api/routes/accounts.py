from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import structlog

from db.database import get_db
from models.user import User
from models.bank_account import BankAccount
from schemas import StandardResponse, BankAccountCreate, BankAccountUpdate, BankAccountResponse
from api.routes.auth_controller import get_current_user

logger = structlog.get_logger()
router = APIRouter(prefix="/accounts", tags=["Manual Accounts"])


@router.get("/", response_model=StandardResponse)
async def get_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bank accounts for the current user (both manual and synced).
    """
    try:
        accounts = db.query(BankAccount).filter(BankAccount.user_id == current_user.id).all()
        # Convert to Pydantic models for response
        data = [BankAccountResponse.model_validate(acc).model_dump() for acc in accounts]
        import json
        logger.info("get_accounts_response", user_id=current_user.id, data=json.dumps(data, default=str))
        return StandardResponse(success=True, data=data)
    except Exception as e:
        logger.error("get_accounts_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=StandardResponse)
async def create_manual_account(
    account_in: BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new manual bank account.
    """
    try:
        new_account = BankAccount(
            user_id=current_user.id,
            is_manual=True,
            name=account_in.name,
            balance=account_in.balance,
            color=account_in.color,
            icon=account_in.icon,
            currency=account_in.currency,
            nature=account_in.nature
        )
        db.add(new_account)
        
        # Aggiorna il bilancio totale dell'utente (dashboard sum)
        user = db.query(User).filter(User.id == current_user.id).first()
        if user and account_in.balance:
            user.current_balance = float(user.current_balance or 0) + float(account_in.balance)
            
        db.commit()
        db.refresh(new_account)
        
        data = BankAccountResponse.model_validate(new_account).model_dump()
        return StandardResponse(success=True, data=data)
    except Exception as e:
        db.rollback()
        logger.error("create_account_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{account_id}", response_model=StandardResponse)
async def update_account(
    account_id: str,
    account_in: BankAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing manual bank account.
    """
    try:
        account = db.query(BankAccount).filter(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Sync update is tricky, allow manual fields to update
        update_data = account_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(account, key, value)

        db.commit()
        db.refresh(account)
        
        data = BankAccountResponse.model_validate(account).model_dump()
        return StandardResponse(success=True, data=data)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("update_account_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{account_id}", response_model=StandardResponse)
async def delete_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a bank account (both manual and synced).
    """
    try:
        account = db.query(BankAccount).filter(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Update the user's global balance by removing the deleted account's balance
        user = db.query(User).filter(User.id == current_user.id).first()
        if user and account.balance:
            user.current_balance = float(user.current_balance or 0) - float(account.balance)
            
        db.delete(account)
        db.commit()
        
        return StandardResponse(success=True, message="Account deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("delete_account_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))
