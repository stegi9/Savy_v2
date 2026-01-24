"""
Smart Intent Detector - LLM-powered intent and entity extraction.
Replaces naive keyword matching with true semantic understanding.
"""
from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
import json
from config import settings
from services.affiliate.interfaces import AffiliateVertical

logger = structlog.get_logger()


def get_intent_llm() -> ChatGoogleGenerativeAI:
    """Fast LLM for intent detection."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.1,  # Low temp for consistent classification
        google_api_key=settings.gemini_api_key,
        convert_system_message_to_human=True
    )


async def detect_intent_and_entities(user_query: str) -> Dict[str, Any]:
    """
    Uses LLM to understand user intent and extract entities.
    
    Returns:
        {
            "has_purchase_intent": bool,
            "vertical": "shopping"|"travel"|"utilities"|"finance"|"general",
            "product_query": str,  # What to search for
            "budget": float | None,
            "urgency": "low"|"medium"|"high",
            "entities": ["iPhone", "hotel", "Roma", etc.]
        }
    """
    logger.info("intent_detection_started", query=user_query)
    
    try:
        llm = get_intent_llm()
        
        system_prompt = """Sei un classificatore di intenti per un'app finanziaria.
Analizza il messaggio dell'utente e determina:

1. **has_purchase_intent**: L'utente vuole comprare/prenotare/pagare qualcosa? (anche implicito)
   - "Posso permettermi un telefono?" → TRUE (vuole comprare)
   - "Mi consigli dove andare in vacanza?" → TRUE (vuole prenotare)
   - "Come risparmiare sulla bolletta?" → TRUE (vuole cambiare fornitore)
   - "Quanto ho speso questo mese?" → FALSE (solo analisi)

2. **vertical**: Categoria del potenziale acquisto
   - "shopping": prodotti, elettronica, abbigliamento, regali
   - "travel": hotel, voli, vacanze, viaggi, noleggio auto
   - "utilities": luce, gas, telefono, internet, assicurazioni
   - "finance": investimenti, risparmi, prestiti
   - "general": domande generali senza intento d'acquisto

3. **product_query**: Cosa cercare per trovare offerte affiliate
   - Estrai il prodotto/servizio specifico da cercare
   - Es: "Vorrei un nuovo telefono Samsung" → "telefono Samsung"
   - Es: "Posso andare a Milano questo weekend?" → "hotel Milano"

4. **budget**: Se l'utente menziona un budget, estrailo (null se non specificato)

5. **entities**: Lista di entità chiave (prodotti, luoghi, marchi)

RISPONDI SOLO con JSON valido, senza markdown:
{"has_purchase_intent": true, "vertical": "shopping", "product_query": "...", "budget": null, "urgency": "medium", "entities": ["..."]}
"""
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Messaggio utente: \"{user_query}\"")
        ])
        
        content = response.content.strip()
        
        # Clean markdown if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        result = json.loads(content)
        
        logger.info("intent_detection_completed", 
                    has_purchase_intent=result.get("has_purchase_intent"),
                    vertical=result.get("vertical"),
                    product_query=result.get("product_query"))
        
        return result
        
    except Exception as e:
        logger.error("intent_detection_failed", error=str(e))
        # Fallback: assume no purchase intent
        return {
            "has_purchase_intent": False,
            "vertical": "general",
            "product_query": None,
            "budget": None,
            "urgency": "low",
            "entities": []
        }


def map_vertical_to_enum(vertical_str: str) -> Optional[AffiliateVertical]:
    """Maps LLM vertical string to AffiliateVertical enum."""
    mapping = {
        "shopping": AffiliateVertical.SHOPPING,
        "travel": AffiliateVertical.TRAVEL,
        "utilities": AffiliateVertical.UTILITIES,
        "grocery": AffiliateVertical.GROCERY,
        "fuel": AffiliateVertical.FUEL_MOBILITY,
    }
    return mapping.get(vertical_str)
