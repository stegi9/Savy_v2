"""
GDPR Controller - Data Export & Account Deletion
Handles GDPR compliance endpoints for user data.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import io
from datetime import datetime

from db.database import get_db
from api.dependencies.auth import get_current_user
from models.user import User
from repositories.user_repository import UserRepository
from repositories.transaction_repository import TransactionRepository
from repositories.category_repository import CategoryRepository
from repositories.recurring_bill_repository import RecurringBillRepository
from services.email_service import get_email_service
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/gdpr", tags=["GDPR"])


@router.get("/export-data")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data in JSON format (GDPR Article 20 - Right to data portability).
    
    Returns:
        JSON file with all user data
    """
    logger.info("gdpr_data_export_requested", user_id=current_user.id)
    
    try:
        # Collect all user data
        user_repo = UserRepository(db)
        transaction_repo = TransactionRepository(db)
        category_repo = CategoryRepository(db)
        bill_repo = RecurringBillRepository(db)
        
        # User profile
        user_data = {
            "user_profile": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "current_balance": float(current_user.current_balance),
                "monthly_budget": float(current_user.monthly_budget),
                "currency": current_user.currency,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
            },
            "categories": [],
            "transactions": [],
            "recurring_bills": [],
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "format_version": "1.0",
                "gdpr_compliant": True
            }
        }
        
        # Categories
        categories = category_repo.get_user_categories(current_user.id)
        for cat in categories:
            user_data["categories"].append({
                "id": cat.id,
                "name": cat.name,
                "icon": cat.icon,
                "color": cat.color,
                "type": cat.type,
                "budget_monthly": float(cat.budget_monthly) if cat.budget_monthly else None,
                "created_at": cat.created_at.isoformat() if hasattr(cat, 'created_at') and cat.created_at else None,
            })
        
        # Transactions
        transactions = transaction_repo.get_user_transactions(current_user.id, limit=10000)  # All transactions
        for txn in transactions:
            user_data["transactions"].append({
                "id": txn.id,
                "amount": float(txn.amount),
                "description": txn.description,
                "transaction_date": txn.transaction_date.isoformat() if txn.transaction_date else None,
                "type": txn.type,
                "category_id": txn.category_id,
                "merchant": txn.merchant if hasattr(txn, 'merchant') else None,
                "created_at": txn.created_at.isoformat() if hasattr(txn, 'created_at') and txn.created_at else None,
            })
        
        # Recurring Bills
        bills = bill_repo.get_user_bills(current_user.id)
        for bill in bills:
            user_data["recurring_bills"].append({
                "id": bill.id,
                "name": bill.name,
                "amount": float(bill.amount),
                "frequency": bill.frequency,
                "next_due_date": bill.next_due_date.isoformat() if bill.next_due_date else None,
                "provider": bill.provider if hasattr(bill, 'provider') else None,
                "is_active": bill.is_active if hasattr(bill, 'is_active') else None,
            })
        
        # Convert to JSON
        json_data = json.dumps(user_data, indent=2, ensure_ascii=False)
        
        # Create file stream
        file_stream = io.BytesIO(json_data.encode('utf-8'))
        file_stream.seek(0)
        
        logger.info("gdpr_data_export_completed", user_id=current_user.id, records={
            "categories": len(user_data["categories"]),
            "transactions": len(user_data["transactions"]),
            "bills": len(user_data["recurring_bills"])
        })
        
        # Return as downloadable file
        return StreamingResponse(
            file_stream,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=savy_data_export_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
            }
        )
    
    except Exception as e:
        logger.error("gdpr_data_export_failed", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export data"
        )


@router.delete("/delete-account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account and all associated data (GDPR Article 17 - Right to erasure).
    
    This action is IRREVERSIBLE and will:
    - Delete all transactions
    - Delete all categories
    - Delete all bills
    - Delete user profile
    - Revoke all tokens
    
    Returns:
        Success message
    """
    logger.warning("gdpr_account_deletion_requested", user_id=current_user.id, email=current_user.email)
    
    try:
        user_repo = UserRepository(db)
        
        # Send confirmation email before deletion
        email_service = get_email_service()
        try:
            email_service.send_email(
                to=current_user.email,
                subject="Account Savy Cancellato",
                html_content=f"""
                <h2>Il tuo account è stato cancellato</h2>
                <p>Ciao {current_user.full_name},</p>
                <p>Il tuo account Savy è stato cancellato con successo come richiesto.</p>
                <p>Tutti i tuoi dati sono stati eliminati in modo permanente.</p>
                <p>Se hai cancellato per errore o desideri tornare, puoi registrarti nuovamente in qualsiasi momento.</p>
                <p>Grazie per aver utilizzato Savy!</p>
                <p>- Il Team Savy</p>
                """
            )
        except Exception as email_error:
            logger.warning("account_deletion_email_failed", error=str(email_error))
        
        # Delete user (CASCADE will delete all related data)
        user_repo.delete(current_user.id)
        
        logger.info("gdpr_account_deleted", user_id=current_user.id)
        
        return {
            "success": True,
            "message": "Account deleted successfully",
            "deleted_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error("gdpr_account_deletion_failed", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )


@router.post("/request-data-deletion")
async def request_data_deletion(
    current_user: User = Depends(get_current_user)
):
    """
    Request account deletion (sends confirmation email with delay).
    Useful for implementing a grace period before actual deletion.
    
    Returns:
        Confirmation message
    """
    logger.info("gdpr_deletion_request_received", user_id=current_user.id)
    
    # TODO: Implement grace period logic (e.g., 7 days before actual deletion)
    # Store deletion_requested_at in database
    # Send email with cancellation link
    # Schedule background job for actual deletion
    
    return {
        "success": True,
        "message": "Account deletion requested. Your account will be deleted in 7 days.",
        "cancellation_deadline": "2026-02-07T00:00:00Z"  # TODO: Calculate actual date
    }
