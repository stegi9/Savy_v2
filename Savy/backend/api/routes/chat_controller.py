"""
Chat controller (FastAPI router).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from services.chat_service import ChatService
from schemas import ChatRequest, ChatResponse
from api.dependencies.auth import get_current_user
from models.user import User
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat endpoint for "Cocktail Check" AI coach.
    
    User asks a natural language question about spending sustainability.
    The AI agent analyzes the user's financial situation and provides advice.
    """
    logger.info(
        "chat_request_received",
        user_id=current_user.id,
        message=request.message
    )
    
    try:
        service = ChatService(db)
        result = await service.process_chat_message(current_user.id, request.message)
        
        return ChatResponse(
            decision=result["decision"],
            reasoning=result["reasoning"],
            affiliate_offers=result.get("affiliate_offers", [])
        )
        
    except Exception as e:
        logger.error("chat_request_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nell'elaborazione del messaggio: {str(e)}"
        )


