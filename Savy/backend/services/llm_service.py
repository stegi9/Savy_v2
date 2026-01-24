"""
LLM service for AI-powered financial coaching using Google Gemini.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
from typing import Dict, Any, List
import json
from config import settings

from models.affiliate import OfferSearchTerm, AffiliateOffer, OfferStatus, PlacementType
from sqlalchemy import select, or_
from services.affiliate_redirect_service import AffiliateRedirectService
from db.database import SessionLocal

logger = structlog.get_logger()


def get_llm_client() -> ChatGoogleGenerativeAI:
    """
    Returns a configured LangChain LLM client using Google Gemini.
    
    Returns:
        ChatGoogleGenerativeAI instance
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",  # O usa "gemini-1.5-pro" per più potenza
        temperature=0.7,
        google_api_key=settings.gemini_api_key,
        convert_system_message_to_human=True  # Gemini non supporta system messages nativamente
    )


async def get_financial_advice(
    user_query: str,
    analysis_result: Dict[str, Any],
    affiliate_offers: List[Dict] = None # Injected from AffiliateNode
) -> Dict[str, str]:
    """
    Gets financial advice from LLM based on user query and analysis.
    """
    logger.info("llm_request_started", query=user_query)
    
    try:
        llm = get_llm_client()
        
        # 0. Format Affiliate Context (if any)
        affiliate_context = ""
        if affiliate_offers:
            offers_text = "\\n".join([f"- {o['title']} ({o['price']}) - {o['badge'] or ''}" for o in affiliate_offers])
            affiliate_context = (
                f"\\n\\n[A TUA DISPOSIZIONE NELLA UI]\\n"
                f"Ho trovato le seguenti offerte partner pertinenti che verranno mostrate come card interattive:\\n{offers_text}\\n"
                f"Nel messaggio, NON inventare link. Dì 'Ho trovato queste offerte per te:' e lascia che l'utente clicchi sulle card."
            )

        # Build system prompt - Enhanced AI Coach
        system_prompt = """Sei Savy, il tuo coach finanziario personale AI. Sei esperto, empatico e PROATTIVO nel trovare modi per risparmiare.

PERSONALITÀ:
- Parli in modo amichevole ma professionale, come un consulente finanziario di fiducia
- Sei onesto ma incoraggiante - non solo "no", ma "ecco cosa potresti fare"
- Quando l'utente vuole comprare qualcosa, lo aiuti a capire SE può permetterselo e COME risparmiare

ANALISI FINANZIARIA:
1. Estrai l'importo dalla domanda (anche se implicito: "iPhone" ≈ €800-1200)
2. Confronta con: Saldo disponibile DOPO bollette
3. Calcola quanto rimarrebbe dopo l'acquisto

DECISIONI:
- "affordable": Può permetterselo senza problemi (rimangono >€500)
- "caution": Fattibile ma richiede attenzione (rimangono €100-500)
- "not_affordable": Non consigliato (rimarrebbe <€100 o in negativo)

OFFERTE PARTNER:
- Se vedi [OFFERTE DISPONIBILI], significa che sotto appariranno card cliccabili
- Menzionale NATURALMENTE: "Ho trovato alcune opzioni per te:" o "Ecco cosa ho trovato..."
- NON inventare link, NON mettere URL nel testo

STILE RISPOSTA:
- Breve ma completo (max 3-4 frasi)
- Usa emoji con moderazione per rendere il testo più leggibile
- Mostra i calcoli chiave

Rispondi SOLO con JSON valido (no markdown):
{"decision": "...", "reasoning": "...", "suggestion": "..."}
"""
        
        # Build human prompt with context
        human_prompt = f"""Domanda utente: "{user_query}"

💰 SITUAZIONE FINANZIARIA:
- Saldo attuale: €{analysis_result.get('current_balance', 0):.2f}
- Bollette in arrivo: €{analysis_result.get('total_bills', 0):.2f}
- Disponibile dopo bollette: €{analysis_result.get('projected_balance', 0):.2f}
- Budget giornaliero: €{analysis_result.get('daily_spending_capacity', 0):.2f}/giorno
- Status: {"⚠️ ATTENZIONE - Fondi limitati" if analysis_result.get('at_risk') else "✅ Situazione gestibile"}

{affiliate_context if affiliate_context else ""}

Analizza la richiesta e rispondi con un JSON contenente decision, reasoning e suggestion."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            result = json.loads(content)
            logger.info("llm_request_completed", decision=result.get("decision"))
            return result
        except json.JSONDecodeError as je:
            logger.warning("llm_response_invalid_json", content=response.content, error=str(je))
            
            # Simple extraction if JSON parsing fails
            if "not_affordable" in content.lower() or "non puoi" in content.lower() or "impossibile" in content.lower():
                decision = "not_affordable"
            elif "caution" in content.lower() or "attenzione" in content.lower() or "cautela" in content.lower():
                decision = "caution"
            else:
                decision = "affordable"
            
            return {
                "decision": decision,
                "reasoning": content,
                "suggestion": None
            }
        
    except Exception as e:
        logger.error("llm_request_failed", error=str(e))
        return {
            "decision": "error",
            "reasoning": "Mi dispiace, ho avuto un problema nell'analizzare la tua richiesta. Riprova più tardi.",
            "suggestion": None
        }


async def categorize_with_ai(
    merchant: str,
    amount: float,
    user_categories: list[dict],
    description: str = "",
    date: str = ""
) -> Dict[str, Any]:
    """
    Categorizes a transaction using AI - CHOOSES from user's OWN categories.
    
    Args:
        merchant: Merchant/store name
        amount: Transaction amount
        user_categories: List of user's categories with id and name
        description: Optional transaction description
        date: Transaction date
        
    Returns:
        Dict with category_id, category_name, confidence, needs_review, reasoning
    """
    logger.info("ai_categorization_started", merchant=merchant, amount=amount, 
                user_categories_count=len(user_categories))
    
    # If no user categories, can't categorize
    if not user_categories:
        logger.info("no_user_categories_available", merchant=merchant)
        return {
            "category_id": None,
            "category_name": None,
            "confidence": 0.0,
            "needs_review": True,
            "reasoning": "L'utente non ha ancora configurato categorie"
        }
    
    try:
        llm = get_llm_client()
        
        # Build category list for prompt
        categories_text = "\\n".join([
            f"- ID: {cat['id']} | Nome: {cat['name']}" 
            for cat in user_categories
        ])
        category_names = [cat['name'] for cat in user_categories]
        
        system_prompt = f"""
Sei Savy, un assistente AI esperto nella categorizzazione di transazioni finanziarie.

L'utente ha definito QUESTE categorie di spesa:
{categories_text}

Il tuo compito è scegliere la categoria PIÙ APPROPRIATA dalla lista sopra.

REGOLE:
1. DEVI scegliere SOLO tra le categorie dell'utente elencate sopra
2. Se la transazione sembra "Spesa" o "Alimentari" → scegli la categoria con nome simile
3. Se "Amazon" o "Shopping" → cerca una categoria simile a Shopping/Acquisti
4. Se non trovi una categoria adatta → scegli la più generica (tipo "Altro" se esiste)
5. Restituisci l'ID esatto della categoria scelta

Rispondi SOLO con JSON:
{{
    "category_id": "ID_ESATTO_DALLA_LISTA",
    "category_name": "NOME_ESATTO_DALLA_LISTA",
    "confidence": 0.95,
    "needs_review": false,
    "reasoning": "Breve spiegazione"
}}
"""
        
        human_prompt = f"""
Categorizza questa transazione scegliendo tra le categorie dell'utente:

- Merchant: {merchant}
- Importo: €{amount:.2f}
- Descrizione: {description or "Non disponibile"}

Categorie disponibili: {', '.join(category_names)}

Rispondi con il JSON contenente l'ID e nome della categoria scelta.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        
        # Parse JSON response
        try:
            content = response.content.strip()
            
            # Remove markdown code blocks
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            result = json.loads(content)
            
            # Validate that the returned category_id exists in user's categories
            returned_id = result.get("category_id")
            returned_name = result.get("category_name")
            
            # Verify the ID is valid
            valid_ids = {cat['id'] for cat in user_categories}
            if returned_id not in valid_ids:
                # Try to match by name instead
                for cat in user_categories:
                    if cat['name'].lower() == str(returned_name).lower():
                        returned_id = cat['id']
                        returned_name = cat['name']
                        break
                else:
                    # Still no match - use first category as fallback
                    logger.warning("ai_returned_invalid_category", 
                                   returned_id=returned_id, 
                                   valid_ids=list(valid_ids))
                    returned_id = user_categories[0]['id']
                    returned_name = user_categories[0]['name']
                    result["confidence"] = 0.5
                    result["needs_review"] = True
            
            result["category_id"] = returned_id
            result["category_name"] = returned_name
            result.setdefault("confidence", 0.8)
            result.setdefault("needs_review", result.get("confidence", 0.8) < 0.7)
            result.setdefault("reasoning", "Categorizzazione AI")
            
            logger.info(
                "ai_categorization_completed",
                merchant=merchant,
                category_id=returned_id,
                category_name=returned_name,
                confidence=result["confidence"]
            )
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("ai_categorization_parse_error", error=str(e), content=response.content)
            
            # Fallback: try to match merchant to common patterns
            merchant_lower = merchant.lower()
            
            # Try to find a matching category by common patterns
            for cat in user_categories:
                cat_lower = cat['name'].lower()
                # Common grocery store names
                if any(store in merchant_lower for store in ["esselunga", "carrefour", "conad", "lidl", "aldi", "coop", "eurospin"]):
                    if any(word in cat_lower for word in ["spesa", "alimentari", "groceries", "cibo"]):
                        return {
                            "category_id": cat['id'],
                            "category_name": cat['name'],
                            "confidence": 0.85,
                            "needs_review": False,
                            "reasoning": f"Riconosciuto supermercato: {merchant}"
                        }
                # Transport
                if any(word in merchant_lower for word in ["atm", "trenord", "uber", "taxi", "metro", "autostrada"]):
                    if any(word in cat_lower for word in ["trasport", "transport", "auto", "viaggio"]):
                        return {
                            "category_id": cat['id'],
                            "category_name": cat['name'],
                            "confidence": 0.85,
                            "needs_review": False,
                            "reasoning": f"Riconosciuto trasporto: {merchant}"
                        }
            
            # No pattern match - return first category with low confidence for review
            return {
                "category_id": user_categories[0]['id'],
                "category_name": user_categories[0]['name'],
                "confidence": 0.4,
                "needs_review": True,
                "reasoning": f"Categoria non determinata per {merchant}, da rivedere"
            }
    
    except Exception as e:
        logger.error("ai_categorization_failed", error=str(e))
        return {
            "category_id": None,
            "category_name": None,
            "confidence": 0.0,
            "needs_review": True,
            "reasoning": f"Errore AI: {str(e)}"
        }
