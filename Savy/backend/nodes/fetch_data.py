"""
Node: Fetch User Data
Retrieves user financial data from MySQL database (balance, bills, transactions).
"""
from typing import Dict, Any
import structlog
from db.database import SessionLocal
from repositories.user_repository import UserRepository
from repositories.recurring_bill_repository import RecurringBillRepository

logger = structlog.get_logger()


async def fetch_user_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetches user financial data from MySQL database.
    
    Retrieves:
    - Current balance from profiles table
    - Active recurring bills
    - Recent transactions (last 30 days)
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with balance and upcoming_bills
    """
    user_id = state["user_id"]
    
    logger.info("fetch_data_started", user_id=user_id)
    
    db = SessionLocal()
    try:
        # Initialize repositories
        user_repo = UserRepository(db)
        bill_repo = RecurringBillRepository(db)
        
        # Fetch user data
        user = user_repo.get_by_id(user_id)
        if not user:
            logger.warning("user_not_found", user_id=user_id)
            state["balance"] = 0.0
            state["upcoming_bills"] = []
            return state
        
        # Get current balance
        state["balance"] = float(user.current_balance)
        
        # Get active recurring bills
        bills = bill_repo.get_active_bills(user_id)
        state["upcoming_bills"] = [
            {
                "id": bill.id,
                "name": bill.name,
                "amount": float(bill.amount),
                "due_day": bill.due_day,
                "category": bill.category,
                "provider": bill.provider
            }
            for bill in bills
        ]
        
        logger.info(
            "fetch_data_completed",
            user_id=user_id,
            balance=state["balance"],
            bills_count=len(state["upcoming_bills"])
        )
        
        return state
        
    except Exception as e:
        logger.error("fetch_data_failed", user_id=user_id, error=str(e))
        # Return state with default values on error
        state["balance"] = 0.0
        state["upcoming_bills"] = []
        return state
    finally:
        db.close()






