import sys
import os
from dotenv import load_dotenv

# 1. Load Environment Variables from backend/.env
# This must be done BEFORE importing config/db
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

# 2. Add backend directory to python path
# Assuming script is inside backend/ folder, we add this folder to sys.path
# 2. Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def seed_affiliates():
    try:
        from sqlalchemy.orm import Session
        import structlog
        from db.database import SessionLocal
        from models.affiliate import AffiliatePartner, AffiliateOffer, OfferTrigger, MatchType

        logger = structlog.get_logger()
        db = SessionLocal()
        
        logger.info("checking_existing_data")
        # ... logic ...
        
        # 1. Partner
        partner = db.query(AffiliatePartner).filter_by(name="Amazon DE").first()
        if not partner:
            partner = AffiliatePartner(
                name="Amazon DE",
                base_url="https://amazon.de",
                is_active=True
            )
            db.add(partner)
            db.flush()
        else:
            logger.info("partner_exists", id=partner.id)

        # 2. Offer
        offer = db.query(AffiliateOffer).filter_by(
            partner_id=partner.id, 
            title="Sconti Tech Week"
        ).first()
        
        if not offer:
            offer = AffiliateOffer(
                partner_id=partner.id,
                title="Sconti Tech Week",
                copy_text="Fino al 40% su elettronica e informatica. Approfittane subito!",
                target_link_template="https://amazon.de/deals?tag=savy-abc-21", 
                status="PUBLISHED",
                published_at=None,
            )
            db.add(offer)
            db.flush()
        else:
            logger.info("offer_exists", id=offer.id)

        # 3. Trigger
        trigger = db.query(OfferTrigger).filter_by(offer_id=offer.id, pattern_text="AMAZON").first()
        if not trigger:
            trigger = OfferTrigger(
                offer_id=offer.id,
                match_type=MatchType.PREFIX,
                pattern_text="AMAZON",
                priority=10
            )
            db.add(trigger)
        else:
            logger.info("trigger_exists", id=trigger.id)
            if trigger.match_type != MatchType.PREFIX:
                trigger.match_type = MatchType.PREFIX
                logger.info("trigger_updated_to_prefix")

        db.commit()
        logger.info("seed_completed", partner="Amazon DE", trigger="AMAZON")
        db.close()

    except Exception as e:
        import traceback
        with open("backend/seed_error.txt", "w") as f:
            f.write("Environment keys: " + str(list(os.environ.keys())) + "\n")
            f.write(traceback.format_exc())
            f.write("\n")
            f.write(str(e))
        print("SEED FAILED. Check backend/seed_error.txt")

if __name__ == "__main__":
    seed_affiliates()
