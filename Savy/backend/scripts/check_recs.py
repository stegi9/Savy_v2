import sys
import os
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

try:
    from db.database import SessionLocal
    from models.user import User
    from models.affiliate import UserRecommendation, AffiliateOffer
    
    db = SessionLocal()
    user = db.query(User).filter(User.email == "stegi@gmail.com").first()
    
    if not user:
        print("User stegi@gmail.com not found.")
    else:
        recs = db.query(UserRecommendation).filter(UserRecommendation.user_id == user.id).all()
        print(f"--- RECS FOR {user.email} ---")
        for r in recs:
            offer = db.get(AffiliateOffer, r.offer_id)
            print(f"Rec ID: {r.id} | Offer: {offer.title if offer else 'Unknown'} | Expires: {r.expires_at}")
        print("-----------------------------")
        
    db.close()
except Exception as e:
    print(f"Error: {e}")
