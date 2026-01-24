"""
FastAPI application entry point - REFACTORED with MySQL + Repository-Service-Controller pattern.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from config import settings
from db.database import init_db, get_db
from api.routes import auth_router, category_router, chat_router, report_router, optimization_router, transaction_router, user_router, bill_router, deep_dive_router, bank_router, affiliate_controller
from schemas import HealthResponse

# Configure structured logging
from utils.logging_config import configure_logging
configure_logging()

logger = structlog.get_logger()


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
    
    # Initialize demo user and default categories
    from repositories.user_repository import UserRepository
    from repositories.category_repository import CategoryRepository
    from sqlalchemy.orm import Session
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        category_repo = CategoryRepository(db)
        
        # Create demo user
        demo_user = user_repo.create_demo_user()
        logger.info("demo_user_initialized", user_id=demo_user.id)
        
        # Initialize default categories if none exist
        existing_categories = category_repo.get_user_categories(demo_user.id)
        if not existing_categories:
            category_repo.initialize_system_categories(demo_user.id)
            logger.info("default_categories_initialized", user_id=demo_user.id)
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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

from datetime import datetime

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        version="2.0.0",
        timestamp=datetime.now().isoformat()
    )


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

