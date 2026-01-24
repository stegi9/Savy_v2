import sys
import os
from datetime import date
from dotenv import load_dotenv

# 1. Load Environment Variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

# 2. Setup Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Redirect stdout to a file to capture logs despite truncation
class LoggerWriter:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = LoggerWriter("backend/trigger_output.txt")
sys.stderr = sys.stdout

try:
    from sqlalchemy.orm import Session
    import structlog
    from db.database import SessionLocal
    from models.user import User
    from models.transaction import Transaction
    from models.bank_account import BankAccount
    from models.bank_connection import BankConnection
    from models.category import UserCategory
    from services.affiliate_matching_service import AffiliateMatchingService
    
    logger = structlog.get_logger()
    
    def trigger_test():
        db = SessionLocal()
        try:
            print("--- STARTING AFFILIATE TRIGGER TEST ---")
            
            # 1. Get User
            # Filter for the ACTUAL frontend user
            user = db.query(User).filter(User.email == "stegi@gmail.com").first()
            if not user:
                # Fallback to first if not found (or raise error)
                print("Warning: stegi@gmail.com not found, picking first user.")
                user = db.query(User).first()
                
            print(f"User found: {user.email} (ID: {user.id})")

            import uuid

            # 2. Create Trigger Transaction
            tx = Transaction(
                id=str(uuid.uuid4()), # Generate UUID
                user_id=user.id,
                merchant="AMAZON PRIME MEMBERSHIP",
                amount=15.99,
                transaction_type="expense",
                transaction_date=date.today(),
                description="Monthly sub",
                category_id=None # Was "sub_123", but safer None if FK logic strict
            )
            db.add(tx)
            db.flush() # Get ID
            print(f"Transaction created: {tx.id} - {tx.merchant}")
            
            # 3. Running Matching Service
            print("Running AffiliateMatchingService...")
            service = AffiliateMatchingService(db)
            matches = service.process_user_transactions(user.id, [tx.id])
            
            if matches:
                 print(f"✅ SUCCESS! {len(matches)} Recommendations generated.")
                 for m in matches:
                     print(f"   - Match: Offer {m.offer_id} (Score: {m.score})")
                 print("\n>>> PLEASE REFRESH YOUR DASHBOARD NOW <<<")
            else:
                 print("⚠️ No matches found. Check if seed data exists (run seed_affiliates.py)")

            db.commit()
            
        except Exception as e:
            msg = str(e)
            print(f"❌ ERROR: {msg[:200]}...") # Print first 200 chars to stdout
            import traceback
            with open("backend/trigger_error.txt", "w") as f:
                f.write(traceback.format_exc())
                f.write("\n")
                f.write(msg)
            print("Full error written to backend/trigger_error.txt")
            db.rollback()
        finally:
            db.close()

    if __name__ == "__main__":
        trigger_test()

except Exception as import_err:
    print(f"Import Error: {import_err}")
    import traceback
    traceback.print_exc()
