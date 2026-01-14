"""
LangGraph Node: Categorize Transaction with AI

This node uses Gemini to intelligently categorize transactions based on:
- Merchant name
- Amount
- Context (email, receipt data if available)
- Historical patterns
"""

import structlog
from typing import TypedDict, Optional
from services.llm_service import categorize_with_ai

logger = structlog.get_logger()


class TransactionCategorizationState(TypedDict):
    """State for transaction categorization"""
    transaction_id: str
    merchant: str
    amount: float
    description: Optional[str]
    date: str
    
    # AI outputs
    category: str
    subcategory: Optional[str]
    confidence: float
    needs_review: bool
    reasoning: str


async def categorize_transaction_node(state: TransactionCategorizationState) -> TransactionCategorizationState:
    """
    Uses Gemini AI to categorize a transaction with context awareness.
    
    Example:
    - "Amazon" + €15 + "Cuffie Bluetooth" → Electronics
    - "Amazon" + €25 + "Detersivo" → Home & Household
    - "Esselunga" → Groceries
    - "ATM Milano" → Transport
    """
    logger.info(
        "categorizing_transaction",
        transaction_id=state["transaction_id"],
        merchant=state["merchant"],
        amount=state["amount"]
    )
    
    try:
        # Call AI categorization service
        result = await categorize_with_ai(
            merchant=state["merchant"],
            amount=state["amount"],
            description=state.get("description", ""),
            date=state["date"]
        )
        
        state["category"] = result["category"]
        state["subcategory"] = result.get("subcategory")
        state["confidence"] = result["confidence"]
        state["needs_review"] = result["needs_review"]
        state["reasoning"] = result["reasoning"]
        
        logger.info(
            "categorization_completed",
            transaction_id=state["transaction_id"],
            category=state["category"],
            confidence=state["confidence"],
            needs_review=state["needs_review"]
        )
        
    except Exception as e:
        logger.error(
            "categorization_failed",
            transaction_id=state["transaction_id"],
            error=str(e)
        )
        # Fallback to "uncategorized"
        state["category"] = "uncategorized"
        state["subcategory"] = None
        state["confidence"] = 0.0
        state["needs_review"] = True
        state["reasoning"] = f"Errore durante la categorizzazione: {str(e)}"
    
    return state





