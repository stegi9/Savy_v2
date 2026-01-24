import pytest
import os
from dotenv import load_dotenv

# Load env (adjust path if needed)
load_dotenv("backend/.env")
# Mock missing critical keys for test if .env is incomplete or not loaded
os.environ.setdefault("MYSQL_PASSWORD", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")
os.environ.setdefault("SALTEDGE_APP_ID", "test")
os.environ.setdefault("SALTEDGE_SECRET", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test")

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from models.user import User
from models.transaction import Transaction
from models.bank_account import BankAccount
from models.bank_connection import BankConnection
from models.category import UserCategory
from models.affiliate import (
    AffiliatePartner, AffiliateOffer, OfferTrigger, 
    MatchType, PlacementType, OfferStatus, UserRecommendation
)
from services.affiliate_matching_service import AffiliateMatchingService
from services.affiliate_redirect_service import AffiliateRedirectService

# Use in-memory DB for speed or connect to dev DB
# For this script we assume running against the dev DB or a new test DB
# Let's use a separate test engine to avoid polluting main DB if possible
# BUT for MVP manual verification script, we can run against main if careful, or use sqlite memory.
# Let's use sqlite memory for isolation.

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from contextlib import contextmanager

@contextmanager
def db_session_cm():
    # Create tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_affiliate_end_to_end(db_session):
    print("\n--- Starting Affiliate End-to-End Test ---")
    
    # 1. Setup Data
    # User
    user = User(email="test@savy.app", hashed_password="hash", full_name="Test User")
    db_session.add(user)
    db_session.flush()
    
    # Partner
    partner = AffiliatePartner(name="Amazon", base_url="https://amazon.it")
    db_session.add(partner)
    db_session.flush()
    
    # Offer
    offer = AffiliateOffer(
        partner_id=partner.id,
        title="Amazon Prime Student",
        copy_text="50% di sconto",
        target_link_template="https://amazon.it/prime?tag={sub_id}",
        status=OfferStatus.PUBLISHED
    )
    db_session.add(offer)
    db_session.flush()
    
    # Trigger
    trigger = OfferTrigger(
        offer_id=offer.id,
        match_type=MatchType.EXACT,
        pattern_text="AMAZON", # Fixed
    )
    db_session.add(trigger)
    db_session.commit()
    
    print(f"[OK] Setup Complete. User ID: {user.id}, Offer ID: {offer.id}")
    
    # 2. Simulate Transaction Sync
    # We create a transaction that should match
    tx = Transaction(
        user_id=user.id,
        amount=10.0,
        merchant="AMAZON Mktp IT", # Needs normalization
        transaction_date=datetime(2024, 1, 1).date(),
        transaction_type="expense"
    )
    db_session.add(tx)
    db_session.commit()
    print(f"[OK] Transaction Created: {tx.merchant}")
    
    # 3. Running Matching Pipeline
    # Using the Service directly (bypassing Worker/Queue delay)
    service = AffiliateMatchingService(db_session)
    # We pass the ID explicitly to simulate the worker extracting it
    service.process_user_transactions(user.id, [tx.id])
    
    # 4. Verify Recommendations
    rec = db_session.query(UserRecommendation).filter_by(user_id=user.id, offer_id=offer.id).first()
    assert rec is not None, "Recommendation was NOT created!"
    assert rec.placement == PlacementType.DASHBOARD
    print(f"[OK] Recommendation Created. Public ID: {rec.public_id}")
    
    # 5. Verify Redirect Service (Token Generation)
    assert rec.token_hash is not None
    print(f"[OK] Token Hash stored: {rec.token_hash[:10]}...")
    
    # 6. Test Token Resolution (Simulate Click)
    # 6.1 API Generation flow
    redirect_service = AffiliateRedirectService(db_session)
    raw_token, public_id = redirect_service.generate_token(
        user_id=user.id,
        offer_id=offer.id,
        placement=PlacementType.DASHBOARD # API generates fresh token
    )
    print(f"[OK] API generated raw token: {raw_token}")
    
    # 6.2 Resolve
    target_url = redirect_service.resolve_token(raw_token, user_agent="TestAgent")
    assert target_url is not None
    assert "amazon.it/prime" in target_url
    assert public_id in target_url
    assert "click_" in target_url
    print(f"[OK] Token resolved to: {target_url}")
    
    # 7. Security: Tampered Token
    tampered_token = raw_token + "FAKE"
    resolved = redirect_service.resolve_token(tampered_token)
    assert resolved is None
    print(f"[OK] Tampered token correctly rejected.")
    
    # 8. Security: Expired Token (Manually expire)
    # Find the recommendation for public_id
    rec_api = db_session.query(UserRecommendation).filter_by(public_id=public_id).first()
    rec_api.expires_at = datetime.utcnow() - timedelta(hours=1)
    db_session.commit()
    
    resolved_expired = redirect_service.resolve_token(raw_token)
    assert resolved_expired is None
    print(f"[OK] Expired token correctly rejected.")

if __name__ == "__main__":
    try:
        with db_session_cm() as sess:
            test_affiliate_end_to_end(sess)
        print("\nALL TESTS PASSED ✨")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
