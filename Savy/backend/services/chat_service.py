"""
Chat service for AI coach functionality.
"""
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from graph import invoke_agent
import structlog
import re
import json

logger = structlog.get_logger()


class ChatService:
    """Service for chat/AI coach functionality."""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
    
    async def process_chat_message(self, user_id: str, message: str) -> dict:
        """Process a chat message through the AI agent."""
        logger.info("processing_chat_message", user_id=user_id)
        
        try:
            # Invoke the LangGraph agent
            result = await invoke_agent(
                user_id=user_id,
                user_query=message
            )
            
            # Parse reasoning if it's in JSON format
            reasoning_text = result.get("reasoning", "")
            
            # Try to parse JSON from reasoning
            try:
                # Check if reasoning contains JSON (might be wrapped in markdown)
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', reasoning_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(1))
                    reasoning_text = parsed.get("reasoning", reasoning_text)
                elif reasoning_text.strip().startswith('{'):
                    parsed = json.loads(reasoning_text)
                    reasoning_text = parsed.get("reasoning", reasoning_text)
            except (json.JSONDecodeError, AttributeError):
                # If parsing fails, use the text as-is
                pass
            
            return {
                "decision": result.get("decision", "unknown"),
                "reasoning": reasoning_text,
                "balance": result.get("balance", 0.0),
                "upcoming_bills": result.get("upcoming_bills", [])
            }
            
        except Exception as e:
            logger.error("chat_processing_failed", error=str(e))
            raise






