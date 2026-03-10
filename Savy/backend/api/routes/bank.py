from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Optional
import structlog

from db.database import get_db
from services.banking_service import BankingService
from models.bank_connection import BankConnection
from models.bank_account import BankAccount
from models.transaction import Transaction
from models.user import User
from models.category import UserCategory
from schemas import BankInstitution, BankLinkResponse, StandardResponse
from api.routes.auth_controller import get_current_user
from utils.job_queue import DbJobQueue
import json

logger = structlog.get_logger()
router = APIRouter(prefix="/banks", tags=["Bank Integration"])
banking_service = BankingService()

logger = structlog.get_logger()
router = APIRouter(prefix="/banks", tags=["Bank Integration"])
banking_service = BankingService()

@router.get("/institutions", response_model=StandardResponse)
async def get_institutions(country: str = "IT", current_user: dict = Depends(get_current_user)):
    """
    Get list of supported banks/institutions for a country.
    """
    try:
        institutions = await banking_service.get_institutions(country)
        return StandardResponse(success=True, data=institutions)
    except Exception as e:
        logger.error("get_institutions_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/link/start", response_model=StandardResponse)
async def start_bank_link(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start Salt Edge Connect Session.
    1. Ensure Salt Edge Customer exists for user.
    2. Create Connect Session.
    3. Return Connect URL for WebView.
    """
    try:
        # 1. Check/Create Customer
        if not current_user.saltedge_customer_id:
            # Create remote customer
            customer_data = await banking_service.create_customer(str(current_user.id))
            logger.info("bank_link_customer_data_received", customer_data=customer_data)
            
            saltedge_id = customer_data.get("id") or customer_data.get("customer_id")
            if saltedge_id:
                current_user.saltedge_customer_id = str(saltedge_id)
                db.commit()
                db.refresh(current_user)
            else:
                logger.error("saltedge_customer_id_missing", data=customer_data)
                raise HTTPException(status_code=500, detail="Failed to create Salt Edge customer: Missing ID")
        
        # 2. Create Connect Session
        redirect_url = "savy://connect/callback" # Intercepted by App
        connect_url = await banking_service.create_connect_session(current_user.saltedge_customer_id, redirect_url)
        
        return StandardResponse(success=True, data=BankLinkResponse(link=connect_url))

    except Exception as e:
        logger.error("bank_link_start_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=StandardResponse)
async def sync_bank_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync data from Salt Edge: Connections -> Accounts -> Transactions.
    """
    if not current_user.saltedge_customer_id:
        return StandardResponse(success=False, message="User has no linked bank customer")

    try:
        # 1. Sync Connections
        connections = await banking_service.get_connections(current_user.saltedge_customer_id)
        
        # Pre-fetch user categories for mapping
        user_categories = db.query(UserCategory).filter_by(user_id=current_user.id).all()
        # Map lower case name -> id
        category_map = {c.name.lower(): c.id for c in user_categories}
        altro_id = category_map.get("altro")
        
        synced_connections = []
        
        for conn_data in connections:
            conn_id = str(conn_data["id"])
            # Upsert Connection
            connection = db.query(BankConnection).filter_by(connection_id=conn_id).first()
            if not connection:
                connection = BankConnection(
                    user_id=current_user.id,
                    connection_id=conn_id,
                    provider_code=conn_data.get("provider_code"),
                    status=conn_data.get("status", "active")
                )
                db.add(connection)
            else:
                connection.status = conn_data.get("status", "active")
                connection.updated_at = func.now()
            
            db.commit() # Commit to get ID
            synced_connections.append(connection)

            # 2. Sync Accounts for this connection
            accounts = await banking_service.get_accounts(conn_id)
            for acc_data in accounts:
                acc_provider_id = str(acc_data["id"])
                bank_account = db.query(BankAccount).filter_by(provider_account_id=acc_provider_id).first()
                
                new_acc_balance = float(acc_data.get("balance") or 0)
                
                if not bank_account:
                    bank_account = BankAccount(
                        connection_id=connection.id,
                        provider_account_id=acc_provider_id,
                        name=acc_data.get("name"),
                        currency=acc_data.get("currency_code"),
                        balance=new_acc_balance,
                        nature=acc_data.get("nature")
                    )
                    db.add(bank_account)
                    
                    # Aggiungi il nuovo saldo al bilancio totale dell'utente
                    current_user.current_balance = float(current_user.current_balance or 0) + new_acc_balance
                    
                    db.commit() # Commit to get ID
                else:
                    # Calcola la differenza e aggiorna il bilancio globale
                    old_acc_balance = float(bank_account.balance or 0)
                    balance_delta = new_acc_balance - old_acc_balance
                    
                    bank_account.balance = new_acc_balance
                    current_user.current_balance = float(current_user.current_balance or 0) + balance_delta
                    
                    db.commit()

                # 3. Sync Transactions
                transactions = await banking_service.get_transactions(conn_id, account_id=acc_provider_id)
                new_tx_count = 0
                
                for tx_data in transactions:
                    tx_provider_id = str(tx_data["id"])
                    
                    # Check duplicate
                    if db.query(Transaction).filter_by(bank_account_id=bank_account.id, provider_transaction_id=tx_provider_id).first():
                        continue
                        
                    # Prepare new transaction
                    amount = float(tx_data.get("amount", 0))
                    description = tx_data.get("description", "")
                    made_on = tx_data.get("made_on") # Date string YYYY-MM-DD
                    
                    # Simple Categorization (Placeholder for AI Agent)
                    category_name = "Altro" 
                    if "amazon" in description.lower(): category_name = "Shopping"
                    elif "uber" in description.lower(): category_name = "Trasporti"
                    elif "supermercato" in description.lower(): category_name = "Alimentari"
                    
                    category_id = category_map.get(category_name.lower(), altro_id)

                    new_tx = Transaction(
                        user_id=current_user.id,
                        bank_account_id=bank_account.id,
                        provider_transaction_id=tx_provider_id,
                        amount=amount,
                        currency=tx_data.get("currency_code", "EUR"),
                        description=description,
                        transaction_date=made_on,
                        category=category_name, # Legacy/Fallback string
                        category_id=category_id, # Link to real category
                        ai_confidence=0.5,
                        extra_data=tx_data.get("extra")
                    )
                    db.add(new_tx)
                    new_tx_count += 1
                
                db.commit()
                if new_tx_count > 0:
                     # Trigger Affiliate Worker
                     try:
                         # We queue for the user, logic will fetch recent txs or we pass IDs if needed
                         # Passing user_id is safer/simpler for now
                         queue = DbJobQueue(db)
                         queue.enqueue(
                             task_name="match_affiliate_offers", 
                             payload={"user_id": current_user.id}
                         )
                     except Exception as e:
                         logger.error("affiliate_queue_fail", error=str(e))

        
        return StandardResponse(success=True, message="Sync completed successfully")

    except Exception as e:
        logger.error("bank_sync_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
