import structlog
import httpx
from typing import List, Dict, Any, Optional
from config import settings

logger = structlog.get_logger()

class BankingService:
    """
    Service to handle interactions with the Salt Edge v5 API.
    """
    
    def __init__(self):
        self.base_url = settings.saltedge_base_url
        self.app_id = settings.saltedge_app_id
        self.secret = settings.saltedge_secret
        self.headers = {
            "App-id": self.app_id,
            "Secret": self.secret,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _request(self, method: str, endpoint: str, json_data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Internal helper to make HTTP requests to Salt Edge.
        """
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=self.headers, json=json_data, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error("saltedge_api_error", status_code=e.response.status_code, response=e.response.text, url=url)
                raise Exception(f"Salt Edge API Error: {e.response.text}")
            except Exception as e:
                logger.error("saltedge_request_failed", error=str(e), url=url)
                raise

    async def create_customer(self, identifier: str) -> Dict[str, Any]:
        """
        Create a customer in Salt Edge.
        If customer already exists (409), retrieve and return it.
        """
        payload = {
            "data": {
                "identifier": identifier
            }
        }
        logger.info("creating_saltedge_customer", identifier=identifier)
        
        try:
            response = await self._request("POST", "/customers", json_data=payload)
            data = response.get("data", {})
            logger.info("saltedge_customer_created", data=data)
            return data
        except Exception as e:
            # Check if error is due to duplicate customer
            error_str = str(e)
            if "DuplicatedCustomer" in error_str or "already exists" in error_str:
                logger.info("customer_exists_fetching", identifier=identifier)
                return await self.get_customer(identifier)
            else:
                raise e

    async def get_customer(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieve a customer by identifier.
        """
        # API v6 supports filtering by identifier in the list endpoint or specific show endpoint if we had ID.
        # But since we only have identifier, we use GET /customers with identifier param if supported,
        # OR we rely on the fact that v6 allows `GET /customers?identifier=X`
        
        response = await self._request("GET", "/customers", params={"identifier": identifier})
        
        data = response.get("data", [])
        logger.info("saltedge_get_customer_response", data=data, raw_counts=len(data) if isinstance(data, list) else "not_list")
        
        if isinstance(data, list) and len(data) > 0:
             return data[0]
        
        if not data:
             logger.warning("customer_not_found_by_identifier", identifier=identifier)
             raise Exception(f"Customer {identifier} not found despite conflict error")

        return data

    async def create_connect_session(self, customer_id: str, redirect_url: str) -> str:
        """
        Create a Connect Session and return the URL.
        """
        payload = {
            "data": {
                "customer_id": customer_id,
                "consent": {
                    "scopes": ["accounts", "transactions"],
                    "from_date": "2025-01-01"
                },
                "attempt": {
                    "return_to": redirect_url
                },
                "allowed_countries": ["XF"] # Force Fake Country for Sandbox
            }
        }
        logger.info("creating_connect_session", customer_id=customer_id)
        response = await self._request("POST", "/connections/connect", json_data=payload)
        return response["data"]["connect_url"]

    async def get_connections(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        List all connections for a customer.
        """
        response = await self._request("GET", "/connections", params={"customer_id": customer_id})
        return response.get("data", [])

    async def get_connection(self, connection_id: str) -> Dict[str, Any]:
        """
        Get a specific connection.
        """
        response = await self._request("GET", f"/connections/{connection_id}")
        return response.get("data", {})

    async def get_accounts(self, connection_id: str) -> List[Dict[str, Any]]:
        """
        Get accounts for a connection.
        """
        response = await self._request("GET", "/accounts", params={"connection_id": connection_id})
        return response.get("data", [])

    async def get_transactions(self, connection_id: str, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get transactions for a connection (and optionally specific account).
        """
        params = {"connection_id": connection_id}
        if account_id:
            params["account_id"] = account_id
            
        response = await self._request("GET", "/transactions", params=params)
        return response.get("data", [])
