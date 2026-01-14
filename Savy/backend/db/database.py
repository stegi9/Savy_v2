"""
MySQL database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from urllib.parse import quote_plus
import structlog

from config import settings

logger = structlog.get_logger()

# MySQL connection URL (with URL encoding for special characters in password)
mysql_user_encoded = quote_plus(settings.mysql_user)
mysql_password_encoded = quote_plus(settings.mysql_password)
DATABASE_URL = f"mysql+pymysql://{mysql_user_encoded}:{mysql_password_encoded}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"

# Debug: Print connection URL (hide password)
import re
safe_url = re.sub(r':([^@]+)@', ':****@', DATABASE_URL)
logger.info("database_url_configured", url=safe_url)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database (create all tables).
    Call this on application startup.
    """
    logger.info("database_initializing")
    Base.metadata.create_all(bind=engine)
    logger.info("database_initialized")

