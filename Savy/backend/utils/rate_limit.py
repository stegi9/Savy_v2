"""
Rate limiting middleware for API protection.
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    For production, use Redis-based rate limiting (e.g., slowapi).
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            app: FastAPI application
            calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, Tuple[int, datetime]] = {}
    
    async def dispatch(self, request: Request, call_next):
        """Process each request with rate limiting."""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Get client identifier (IP address or user ID if authenticated)
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        now = datetime.now()
        
        if client_id in self.clients:
            count, window_start = self.clients[client_id]
            
            # Reset window if period has passed
            if now - window_start > timedelta(seconds=self.period):
                self.clients[client_id] = (1, now)
            else:
                # Check if limit exceeded
                if count >= self.calls:
                    logger.warning(
                        "rate_limit_exceeded",
                        client_id=client_id,
                        path=request.url.path,
                        count=count
                    )
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {self.period} seconds.",
                        headers={"Retry-After": str(self.period)}
                    )
                
                # Increment counter
                self.clients[client_id] = (count + 1, window_start)
        else:
            # First request from this client
            self.clients[client_id] = (1, now)
        
        # Clean up old entries periodically
        if len(self.clients) > 10000:
            self._cleanup_old_entries(now)
        
        response = await call_next(request)
        
        # Add rate limit headers
        if client_id in self.clients:
            count, _ = self.clients[client_id]
            response.headers["X-RateLimit-Limit"] = str(self.calls)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.calls - count))
            response.headers["X-RateLimit-Reset"] = str(self.period)
        
        return response
    
    def _cleanup_old_entries(self, now: datetime):
        """Remove entries older than the rate limit period."""
        expired_clients = [
            client_id for client_id, (_, window_start) in self.clients.items()
            if now - window_start > timedelta(seconds=self.period * 2)
        ]
        for client_id in expired_clients:
            del self.clients[client_id]
        
        logger.info("rate_limiter_cleanup", removed=len(expired_clients))
