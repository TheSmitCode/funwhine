# verify_admin.py
"""
Simple verification script: prints admin users from the DB.
Run: python verify_admin.py
"""

from sqlalchemy.orm import sessionmaker
from app.db.session import SessionLocal, get_sync_engine_for_admin
from app.models.user import User

def main():
    # Prefer the provided sync SessionLocal; if not available, derive a sync engine.
    if SessionLocal is not None:
        SessionFactory = SessionLocal
    else:
        engine = get_sync_engine_for_admin()
        SessionFactory = sessionmaker(bind=engine)

    db = SessionFactory()
    try:
        admins = db.query(User).filter(getattr(User, "is_admin", False) == True).all()
        if not admins:
            print("No admin users found.")
        else:
            for a in admins:
                print("Admin:", getattr(a, "id", None), getattr(a, "email", getattr(a, "username", None)))
    finally:
        db.close()

if __name__ == "__main__":
    main()
