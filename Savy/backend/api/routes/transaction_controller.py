"""
Controller (API Router) for transactions.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File, Form
import traceback
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date as DateType
import structlog

from db.database import get_db
from repositories.transaction_repository import TransactionRepository
from repositories.user_repository import UserRepository
from repositories.category_repository import CategoryRepository
from repositories.merchant_rule_repository import MerchantRuleRepository
from services.llm_service import categorize_with_ai
from services.statement_parser_service import StatementParserService
from config import settings
from schemas import StandardResponse
from api.dependencies.auth import get_current_user
from models.user import User

logger = structlog.get_logger()

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionCreateRequest(BaseModel):
    """Request to create a transaction."""
    merchant: str = Field(..., description="Merchant/store name")
    amount: float = Field(..., description="Transaction amount")
    transaction_type: str = Field("expense", description="Transaction type: 'expense' or 'income'")
    description: Optional[str] = Field(None, description="Transaction description")
    date: DateType = Field(..., description="Transaction date (YYYY-MM-DD)")
    bank_account_id: Optional[str] = Field(None, description="Bank account ID")
    auto_categorize: bool = Field(True, description="Auto-categorize with AI")


class TransactionResponse(BaseModel):
    """Transaction with category."""
    id: str
    user_id: str
    merchant: str
    amount: float
    category_id: Optional[str]
    category_name: Optional[str]
    description: Optional[str]
    date: str
    bank_account_id: Optional[str]
    ai_confidence: Optional[float]
    needs_review: bool
    created_at: str


@router.post("/", response_model=StandardResponse)
async def create_transaction(
    request: TransactionCreateRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transaction with optional AI categorization.
    
    - **merchant**: Merchant/store name
    - **amount**: Transaction amount
    - **auto_categorize**: Whether to use AI to categorize (default: true)
    """
    try:
        logger.info(
            "create_transaction_request",
            user_id=current_user.id,
            merchant=request.merchant,
            amount=request.amount
        )
        
        transaction_repo = TransactionRepository(db)
        
        # Validate transaction type FIRST
        tx_type = request.transaction_type.lower()
        if tx_type not in ["expense", "income"]:
            tx_type = "expense"
        
        # Initialize categorization variables
        category_id = None
        category_name = None
        ai_confidence = None
        needs_review = False
        
        # Get repositories
        category_repo = CategoryRepository(db)
        user_categories = category_repo.get_user_categories(current_user.id)
        merchant_rule_repo = MerchantRuleRepository(db)
        
        # ============================================================
        # Filter categories by transaction type
        # ============================================================
        filtered_categories = [
            cat for cat in user_categories
            if (cat.category_type or "expense") == tx_type
        ]
        
        logger.info(
            "categorization_start",
            user_id=current_user.id,
            tx_type=tx_type,
            total_categories=len(user_categories),
            filtered_categories=len(filtered_categories),
            all_category_types=[{"name": c.name, "type": c.category_type} for c in user_categories]
        )
        
        # ============================================================
        # NO categories of this type? Mark for review (but allow creation)
        # ============================================================
        if not filtered_categories:
            needs_review = True
            logger.info(
                "transaction_needs_review_no_matching_categories",
                merchant=request.merchant,
                tx_type=tx_type,
                user_id=current_user.id
            )
        else:
            # STEP 1: Check if we have a learned rule for this merchant
            merchant_rule = merchant_rule_repo.find_rule(current_user.id, request.merchant)
            
            if merchant_rule:
                # Verify the rule's category matches the transaction type
                rule_category = next(
                    (cat for cat in filtered_categories if cat.id == merchant_rule.category_id),
                    None
                )
                if rule_category:
                    # Use the learned rule - user taught us this before!
                    category_id = merchant_rule.category_id
                    category_name = rule_category.name
                    ai_confidence = 1.0  # User-defined = 100% confidence
                    needs_review = False
                    
                    logger.info(
                        "transaction_categorized_by_merchant_rule",
                        merchant=request.merchant,
                        category=category_name,
                        category_id=category_id
                    )
                else:
                    # Rule exists but category type doesn't match - use AI instead
                    merchant_rule = None
            
            # STEP 2: If no rule and auto_categorize enabled, use AI
            if not merchant_rule and request.auto_categorize:
                try:
                    # Pass filtered categories to AI
                    user_categories_for_ai = [
                        {"id": cat.id, "name": cat.name}
                        for cat in filtered_categories
                    ]
                    
                    ai_result = await categorize_with_ai(
                        merchant=request.merchant,
                        amount=request.amount,
                        user_categories=user_categories_for_ai,
                        description=request.description or ""
                    )
                    
                    # AI now returns category_id and category_name directly
                    category_id = ai_result.get('category_id')
                    category_name = ai_result.get('category_name')
                    ai_confidence = ai_result.get('confidence', 0.0)
                    needs_review = ai_result.get('needs_review', ai_confidence < 0.7)
                    
                    logger.info(
                        "transaction_categorized_by_ai",
                        merchant=request.merchant,
                        category_id=category_id,
                        category_name=category_name,
                        confidence=ai_confidence,
                        needs_review=needs_review
                    )
                    
                except Exception as e:
                    logger.warning(
                        "ai_categorization_failed",
                        error=str(e),
                        merchant=request.merchant
                    )
                    # Continue without categorization
                    needs_review = True
            elif not merchant_rule:
                # No rule and no auto-categorize
                needs_review = True
        
        # Create transaction
        transaction = transaction_repo.create_transaction(
            user_id=current_user.id,
            merchant=request.merchant,
            amount=request.amount,
            transaction_type=tx_type,
            category_id=category_id,
            category=category_name,
            description=request.description,
            date=request.date,
            bank_account_id=request.bank_account_id,
            ai_confidence=ai_confidence,
            needs_review=needs_review
        )
        
        # Update user balance and bank account balance
        user_repo = UserRepository(db)
        current_balance = float(current_user.current_balance or 0)
        amount_delta = request.amount if tx_type == "income" else -request.amount
        new_balance = current_balance + amount_delta
        user_repo.update_balance(current_user.id, new_balance)
        
        if request.bank_account_id:
            from models.bank_account import BankAccount
            bank_account = db.query(BankAccount).filter_by(id=request.bank_account_id).first()
            if bank_account:
                current_acc_balance = float(bank_account.balance or 0)
                bank_account.balance = current_acc_balance + amount_delta
                db.commit()
        
        logger.info(
            "transaction_created",
            transaction_id=transaction.id,
            user_id=current_user.id,
            balance_updated=True,
            new_balance=new_balance
        )
        
        return {
            "success": True,
            "data": {
                "id": transaction.id,
                "user_id": transaction.user_id,
                "merchant": transaction.merchant,
                "amount": float(transaction.amount),
                "transaction_type": transaction.transaction_type or tx_type,
                "category_id": transaction.category_id,
                "category_name": transaction.category or category_name,
                "description": transaction.description,
                "date": transaction.transaction_date.isoformat(),
                "bank_account_id": transaction.bank_account_id,
                "ai_confidence": transaction.ai_confidence,
                "needs_review": transaction.needs_review,
                "created_at": transaction.created_at.isoformat()
            },
            "message": "Transazione creata con successo"
        }
        
    except Exception as e:
        logger.error(
            "create_transaction_failed",
            error=str(e),
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Errore nella creazione della transazione: {str(e)}"
        )


@router.get("/", response_model=StandardResponse)
async def get_user_transactions(
    limit: int = 50,
    needs_review: Optional[bool] = None,
    start_date: Optional[DateType] = None,
    end_date: Optional[DateType] = None,
    bank_account_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's transactions.
    
    - **limit**: Maximum number of transactions to return
    - **needs_review**: Filter by transactions that need manual review
    - **start_date**: Filter params for date range (YYYY-MM-DD)
    - **end_date**: Filter params for date range (YYYY-MM-DD)
    """
    try:
        logger.info(
            "get_transactions_request",
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            bank_account_id=bank_account_id
        )
        
        transaction_repo = TransactionRepository(db)
        transactions = transaction_repo.get_user_transactions(
            user_id=current_user.id,
            limit=limit,
            needs_review=needs_review,
            start_date=start_date,
            end_date=end_date,
            bank_account_id=bank_account_id
        )
        
        result = []
        for t in transactions:
            result.append({
                "id": t.id,
                "user_id": t.user_id,
                "merchant": t.merchant,
                "amount": float(t.amount),
                "transaction_type": t.transaction_type or "expense",
                "category_id": t.category_id,
                "category": t.category,
                "category_name": t.category,  # Alias for Flutter compatibility
                "description": t.description,
                "date": t.transaction_date.isoformat(),
                "bank_account_id": t.bank_account_id,
                "ai_confidence": t.ai_confidence,
                "needs_review": t.needs_review,
                "created_at": t.created_at.isoformat()
            })
        
        logger.info(
            "transactions_retrieved",
            user_id=current_user.id,
            count=len(result)
        )
        
        return {
            "success": True,
            "data": {
                "transactions": result,
                "count": len(result)
            }
        }
        
    except Exception as e:
        logger.error(
            "get_transactions_failed",
            error=str(e),
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Errore nel recupero delle transazioni: {str(e)}"
        )


@router.patch("/{transaction_id}/category", response_model=StandardResponse)
async def update_transaction_category(
    transaction_id: str,
    category_id: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update transaction category (manual override after AI suggestion).
    Also saves a merchant rule so the AI learns for next time.
    
    - **transaction_id**: The transaction ID
    - **category_id**: The new category ID
    """
    try:
        logger.info(
            "update_transaction_category_request",
            transaction_id=transaction_id,
            category_id=category_id,
            user_id=current_user.id
        )
        
        transaction_repo = TransactionRepository(db)
        
        # Get transaction first to access merchant name
        existing_transaction = transaction_repo.get_by_id(transaction_id)
        if not existing_transaction:
            raise HTTPException(status_code=404, detail="Transazione non trovata")
        
        if existing_transaction.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Non autorizzato")
        
        # Update the transaction category
        transaction = transaction_repo.update_transaction_category(
            transaction_id=transaction_id,
            category_id=category_id
        )
        
        # SAVE MERCHANT RULE - AI will remember this for next time!
        if existing_transaction.merchant:
            merchant_rule_repo = MerchantRuleRepository(db)
            merchant_rule_repo.save_rule(
                user_id=current_user.id,
                merchant=existing_transaction.merchant,
                category_id=category_id
            )
            logger.info(
                "merchant_rule_saved",
                merchant=existing_transaction.merchant,
                category_id=category_id,
                user_id=current_user.id
            )
        
        logger.info(
            "transaction_category_updated",
            transaction_id=transaction_id
        )
        
        return {
            "success": True,
            "data": {
                "id": transaction.id,
                "category_id": transaction.category_id
            },
            "message": "Categoria aggiornata. L'AI ricorderà questa scelta!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "update_transaction_category_failed",
            error=str(e),
            transaction_id=transaction_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Errore nell'aggiornamento della categoria: {str(e)}"
        )


@router.delete("/{transaction_id}", response_model=StandardResponse)
async def delete_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a transaction and restore the balance.
    
    - **transaction_id**: The transaction ID to delete
    """
    try:
        logger.info(
            "delete_transaction_request",
            transaction_id=transaction_id,
            user_id=current_user.id
        )
        
        transaction_repo = TransactionRepository(db)
        
        # Get transaction to restore balance
        transaction = transaction_repo.get_by_id(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail="Transazione non trovata"
            )
        
        if transaction.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Non autorizzato a eliminare questa transazione"
            )
        
        # Restore balance based on transaction type
        user_repo = UserRepository(db)
        current_balance = float(current_user.current_balance or 0)
        
        if transaction.transaction_type == 'income':
            # Deleting income: SUBTRACT from balance (remove the income)
            amount_delta = -float(transaction.amount)
        else:
            # Deleting expense: ADD back to balance (restore the spent money)
            amount_delta = float(transaction.amount)
            
        new_balance = current_balance + amount_delta
        user_repo.update_balance(current_user.id, new_balance)
        
        # Restore bank account balance
        if transaction.bank_account_id:
            from models.bank_account import BankAccount
            bank_account = db.query(BankAccount).filter_by(id=transaction.bank_account_id).first()
            if bank_account:
                current_acc_balance = float(bank_account.balance or 0)
                bank_account.balance = current_acc_balance + amount_delta
                db.commit()
        
        # Delete transaction
        transaction_repo.delete(transaction_id)
        
        logger.info(
            "transaction_deleted",
            transaction_id=transaction_id,
            user_id=current_user.id,
            balance_restored=new_balance
        )
        
        return {
            "success": True,
            "message": "Transazione eliminata con successo"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "delete_transaction_failed",
            error=str(e),
            transaction_id=transaction_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Errore nell'eliminazione della transazione: {str(e)}"
        )


from pydantic import BaseModel
from typing import List

class BulkDeleteRequest(BaseModel):
    transaction_ids: List[str]

@router.post("/bulk-delete", response_model=StandardResponse)
async def bulk_delete_transactions(
    request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        transaction_repo = TransactionRepository(db)
        user_repo = UserRepository(db)
        
        deleted = 0
        total_user_delta = 0.0
        bank_account_deltas = {}
        
        from models.bank_account import BankAccount
        
        for tx_id in request.transaction_ids:
            transaction = transaction_repo.get_by_id(tx_id)
            if not transaction or transaction.user_id != current_user.id:
                continue
                
            amount_delta = -float(transaction.amount) if transaction.transaction_type == 'income' else float(transaction.amount)
            total_user_delta += amount_delta
            
            if transaction.bank_account_id:
                bank_account_deltas[transaction.bank_account_id] = bank_account_deltas.get(transaction.bank_account_id, 0.0) + amount_delta
                
            transaction_repo.delete(tx_id)
            deleted += 1
            
        if total_user_delta != 0:
            current_balance = float(current_user.current_balance or 0)
            user_repo.update_balance(current_user.id, current_balance + total_user_delta)
            
        for bank_id, delta in bank_account_deltas.items():
            if delta != 0:
                bank_account = db.query(BankAccount).filter_by(id=bank_id).first()
                if bank_account:
                    bank_account.balance = float(bank_account.balance or 0) + delta
                    db.commit()
                    
        return {"success": True, "message": f"{deleted} transazioni eliminate."}
    except Exception as e:
        logger.error("bulk_delete_failed", error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=StandardResponse)
async def upload_statement(
    bank_account_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an Excel or PDF bank statement.
    The AI extracts transactions, categorizes them, and performs a bulk insert.
    """
    try:
        logger.info("upload_statement_request", user_id=current_user.id, filename=file.filename)
        
        parser_service = StatementParserService(api_key=settings.gemini_api_key)
        raw_text = await parser_service.extract_text_from_file(file)
        
        category_repo = CategoryRepository(db)
        user_categories = category_repo.get_user_categories(current_user.id)
        cat_list = [{"id": c.id, "name": c.name} for c in user_categories]
        
        transactions_data = parser_service.parse_transactions(raw_text, cat_list)
        
        transaction_repo = TransactionRepository(db)
        user_repo = UserRepository(db)
        inserted_count = 0
        total_amount_delta = 0.0
        
        for tx_data in transactions_data:
            if tx_data.get("amount") is None:
                continue
                
            amount = float(tx_data.get("amount"))
            tx_type = "expense" if amount < 0 else "income"
            abs_amount = abs(amount)
            
            cat_id = tx_data.get("category_id")
            valid_cat = next((c for c in user_categories if c.id == cat_id), None) if cat_id else None
            
            # Auto-assign needs review if confidence is low
            conf = tx_data.get("ai_confidence", 0.0)
            nr = tx_data.get("needs_review", conf < 0.7)
            
            if not valid_cat:
                cat_id = None
                nr = True
                
            from datetime import datetime
            
            tx_date = tx_data.get("date")
            if not tx_date:
                tx_date = datetime.now().strftime("%Y-%m-%d")
                nr = True
                
            transaction_repo.create_transaction(
                user_id=current_user.id,
                merchant=tx_data.get("description", "Sconosciuto"),
                amount=abs_amount,
                transaction_type=tx_type,
                category_id=cat_id,
                category=valid_cat.name if valid_cat else None,
                description=tx_data.get("description", "Sconosciuto"),
                date=tx_date,
                bank_account_id=bank_account_id if bank_account_id and bank_account_id != "null" else None,
                ai_confidence=conf,
                needs_review=nr
            )
            inserted_count += 1
            total_amount_delta += amount
            
        # Update user and bank balances comprehensively
        current_balance = float(current_user.current_balance or 0)
        user_repo.update_balance(current_user.id, current_balance + total_amount_delta)
        
        if bank_account_id and bank_account_id != "null":
            from models.bank_account import BankAccount
            bank_account = db.query(BankAccount).filter_by(id=bank_account_id).first()
            if bank_account:
                current_acc_balance = float(bank_account.balance or 0)
                bank_account.balance = current_acc_balance + total_amount_delta
                db.commit()
                
        return {
            "success": True,
            "message": f"Estratto conto analizzato! {inserted_count} transazioni inserite.",
            "data": {"inserted": inserted_count}
        }
    except Exception as e:
        logger.error("upload_statement_failed", error=str(e), traceback=traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to process statement: {str(e)}")


