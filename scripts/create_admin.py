import argparse
from sqlalchemy.orm import Session
from app.db import SessionLocal, Base, engine
from app.models import User
from app.security import hash_password

def main(email: str, password: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print("User already exists")
            return
        user = User(email=email, hashed_password=hash_password(password), role="ADMIN")
        db.add(user)
        db.commit()
        print("Admin created:", email)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    main(args.email, args.password)