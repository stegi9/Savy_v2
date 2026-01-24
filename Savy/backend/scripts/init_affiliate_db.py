from db.database import engine, Base
from models.tracking import AffiliateClickToken, AffiliateClickEvent, AffiliateConversion
import structlog

logger = structlog.get_logger()

def init_tables():
    logger.info("Initializing Affiliate Tracking Tables...")
    try:
        # Create all tables defined in models.tracking
        # SQLAlchemy's create_all will skip existing tables
        AffiliateClickToken.__table__.create(bind=engine, checkfirst=True)
        AffiliateClickEvent.__table__.create(bind=engine, checkfirst=True)
        AffiliateConversion.__table__.create(bind=engine, checkfirst=True)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error("Failed to create tables", error=str(e))

if __name__ == "__main__":
    init_tables()
