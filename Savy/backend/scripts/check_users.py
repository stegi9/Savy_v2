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
    
    db = SessionLocal()
    users = db.query(User).all()
    print("--- USERS FOUND ---")
    for u in users:
        print(f"Email: {u.email} | ID: {u.id}")
    print("-------------------")
    db.close()
except Exception as e:
    print(f"Error: {e}")
