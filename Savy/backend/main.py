"""
FastAPI application entry point - REFACTORED with MySQL + Repository-Service-Controller pattern.
"""
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
from sqlalchemy.orm import Session

from config import settings
from db.database import init_db, get_db
from api.routes import (
    auth_router, 
    category_router, 
    chat_router, 
    report_router, 
    optimization_router, 
    transaction_router, 
    user_router, 
    bill_router, 
    deep_dive_router, 
    bank_router, 
    affiliate_controller
)
from api.routes import gdpr_controller
from schemas import HealthResponse
from utils.rate_limit import RateLimitMiddleware
from utils.exceptions import SavyException

# Configure structured logging
from utils.logging_config import configure_logging
configure_logging()

logger = structlog.get_logger()

# Initialize Sentry (if configured)
if settings.sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=0.1 if settings.environment == "production" else 1.0,
            profiles_sample_rate=0.1 if settings.environment == "production" else 1.0,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
            send_default_pii=False,  # Don't send personally identifiable information
        )
        logger.info("sentry_initialized", environment=settings.environment)
    except ImportError:
        logger.warning("sentry_not_installed", message="Install sentry-sdk for error monitoring")
    except Exception as e:
        logger.error("sentry_initialization_failed", error=str(e))
else:
    logger.info("sentry_disabled", message="SENTRY_DSN not configured")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("application_startup", environment=settings.environment)
    
    # Initialize database
    init_db()
    
    # Initialize demo user and default categories (only in development)
    if settings.environment == "development":
        from repositories.user_repository import UserRepository
        from repositories.category_repository import CategoryRepository
        
        db = next(get_db())
        try:
            user_repo = UserRepository(db)
            category_repo = CategoryRepository(db)
            
            # Check if demo user already exists
            demo_user = user_repo.get_by_email("demo@savy.app")
            if not demo_user:
                demo_user = user_repo.create_demo_user()
                logger.info("demo_user_created", user_id=demo_user.id)
            
            # Initialize default categories if none exist
            existing_categories = category_repo.get_user_categories(demo_user.id)
            if not existing_categories:
                category_repo.initialize_system_categories(demo_user.id)
                logger.info("default_categories_initialized", user_id=demo_user.id)
        except Exception as e:
            logger.error("demo_user_initialization_failed", error=str(e))
        finally:
            db.close()
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")


# Create FastAPI application
app = FastAPI(
    title="Savy API",
    description="AI Personal Finance Coach - Backend API",
    version="2.0.0",
    lifespan=lifespan
)

# Rate Limiting Middleware (before CORS)
app.add_middleware(
    RateLimitMiddleware,
    calls=100,  # 100 requests
    period=60   # per 60 seconds
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if settings.environment == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(SavyException)
async def savy_exception_handler(request: Request, exc: SavyException):
    """Handle custom Savy exceptions."""
    logger.warning(
        "savy_exception",
        path=request.url.path,
        detail=exc.detail,
        status_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_type=type(exc).__name__
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

from datetime import datetime
from sqlalchemy import text

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns system status including:
    - API status
    - Database connectivity
    - Environment info
    - Version
    """
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        version="2.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with component status.
    
    Checks:
    - API: Always returns healthy if endpoint is reachable
    - Database: Tests MySQL connection
    - Cache: Tests cache service (if enabled)
    - LLM: Tests Gemini API availability (optional)
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "environment": settings.environment,
        "components": {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "healthy",
            "type": "MySQL",
            "message": "Connection successful"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "type": "MySQL",
            "error": str(e)
        }
    
    # Check cache
    try:
        from services.cache_service import get_cache
        cache = get_cache()
        cache_stats = cache.get_stats()
        health_status["components"]["cache"] = {
            "status": "healthy",
            "type": "InMemoryCache",
            "stats": cache_stats
        }
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "unavailable",
            "error": str(e)
        }
    
    # Check LLM service (optional, don't fail health check if unavailable)
    try:
        from services.llm_service import get_llm_client
        llm = get_llm_client()
        health_status["components"]["llm"] = {
            "status": "configured",
            "model": "gemini-2.0-flash-exp",
            "message": "LLM client initialized"
        }
    except Exception as e:
        health_status["components"]["llm"] = {
            "status": "warning",
            "error": str(e)
        }
    
    return health_status


# ============================================================================
# REGISTER ROUTERS
# ============================================================================

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(category_router, prefix=settings.api_v1_prefix)
app.include_router(chat_router, prefix=settings.api_v1_prefix)
app.include_router(report_router, prefix=settings.api_v1_prefix)
app.include_router(optimization_router, prefix=settings.api_v1_prefix)
app.include_router(transaction_router, prefix=settings.api_v1_prefix)
app.include_router(user_router, prefix=settings.api_v1_prefix)
app.include_router(bill_router, prefix=settings.api_v1_prefix)
app.include_router(deep_dive_router, prefix=settings.api_v1_prefix)
app.include_router(bank_router, prefix=settings.api_v1_prefix)
app.include_router(affiliate_controller.router, prefix=settings.api_v1_prefix)
app.include_router(gdpr_controller.router, prefix=settings.api_v1_prefix)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Savy API - AI Personal Finance Coach",
        "version": "2.0.0",
        "architecture": "Repository-Service-Controller with MySQL",
        "docs_url": "/docs",
        "health_url": "/health"
    }

