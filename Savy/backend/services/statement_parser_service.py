import os
import json
import pandas as pd
import PyPDF2
from typing import List, Dict, Any, Tuple
from fastapi import UploadFile
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
from db.database import SessionLocal

logger = structlog.get_logger()

class StatementParserService:
    def __init__(self, api_key: str):
        if not api_key:
            logger.error("statement_parser_missing_api_key")
            raise ValueError("GOOGLE_API_KEY is required for statement parsing")
        # Ensure we use native Langchain integration to match Savy's stack
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            google_api_key=api_key,
            convert_system_message_to_human=True
        )

    async def extract_text_from_file(self, file: UploadFile) -> str:
        """Extracts text from PDF, CSV, or EXCEL file."""
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Save temp file
        temp_path = f"/tmp/upload_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(content)
            
        text_content = ""
        try:
            if file_ext == 'pdf':
                reader = PyPDF2.PdfReader(temp_path)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted + "\n"
            elif file_ext in ['csv']:
                df = pd.read_csv(temp_path)
                text_content = df.to_csv(index=False)
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(temp_path)
                text_content = df.to_csv(index=False)
            else:
                raise ValueError(f"Formato file non supportato: {file_ext}")
                
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        return text_content

    def parse_transactions(self, raw_text: str, user_categories: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Sends raw text to Gemini to neatly extract transactions 
        matching existing categories.
        """
        prompt = f"""
Sei un esperto contabile AI. Il tuo obiettivo è analizzare il seguente estratto conto bancario (PDF grezzo o CSV) ed estrarre tutte le transazioni vere e proprie.

REGOLE FONDAMENTALI:
1. IGNORA i saldi totali, le intestazioni, le pubblicità della banca e i messaggi informativi.
2. IGNORA categorizzazioni o 'settori' nativi proposti dalla banca nel file. 
3. Per ogni transazione, DEVI cercare la categoria più appropriata dalla seguente lista di Categorie dell'Utente:
{json.dumps(user_categories, indent=2)}

4. Se sei almeno mediamente sicuro (confidence >= 0.6) che una transazione appartenga a una di queste categorie (es. 'Supermercato', 'Amazon' in 'Shopping', ecc.), assegna il suo `id`. Altrimenti assegna null.
5. DEVI restituire i dati ESATTAMENTE nel seguente formato JSON strutturato, senza markup Markdown o spiegazioni aggiuntive. Un array di oggetti:

[
  {{
    "date": "YYYY-MM-DD",
    "amount": -10.50,  // Negativo per le uscite (spese), positivo per le entrate (stipendi/ricariche)
    "description": "Nome pulito del commerciante o causale",
    "category_id": "uuid-se-trovata-corrispondenza-altrimenti-null",
    "ai_confidence": 0.95, // Da 0.0 a 1.0 sulla sicurezza della categorizzazione
    "needs_review": false // true SOLO se sei in forte dubbio sulla categoria o il merchant
  }}
]

Ecco il testo grezzo estratto dal file bancario:
================
{raw_text[:25000]} 
================
"""

        try:
            logger.info("gemini_statement_parsing_started", text_length=len(raw_text))
            
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content="Analizza l'estratto conto sovrastante.")
            ]
            response = self.llm.invoke(messages)
            
            raw_json = response.content.strip()
            
            if raw_json.startswith("```json"):
                raw_json = raw_json.replace("```json", "").replace("```", "").strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json.replace("```", "").strip()
                
            transactions = json.loads(raw_json)
            logger.info("gemini_statement_parsing_success", count=len(transactions))
            return transactions
            
        except json.JSONDecodeError as e:
            logger.error("gemini_json_parse_error", error=str(e), response=response.content)
            raise ValueError("Impossibile decodificare l'output dell'IA")
        except Exception as e:
            logger.error("gemini_api_error", error=str(e))
            raise ValueError(f"Errore di comunicazione con Gemini: {str(e)}")
