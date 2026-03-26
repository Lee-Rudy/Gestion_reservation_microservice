import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import bcrypt
from sqlalchemy.orm import Session

from auth_service.infrastructure.database.database import Base, SessionLocal, engine
from auth_service.infrastructure.database.models import UserModel

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

db: Session = SessionLocal()

existing_user = db.query(UserModel).filter(UserModel.email == "user@example.com").first()
existing_admin = db.query(UserModel).filter(UserModel.email == "admin@example.com").first()

if not existing_user:
    user_password = bcrypt.hashpw("User@123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = UserModel(
        name="Test User",
        email="user@example.com",
        password_hash=user_password,
        role="USER",
    )
    db.add(user)
    print("[OK] User created: user@example.com / User@123")
else:
    print("[INFO] User already exists")

if not existing_admin:
    admin_password = bcrypt.hashpw("Admin@123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    admin = UserModel(
        name="Admin User",
        email="admin@example.com",
        password_hash=admin_password,
        role="ADMIN",
    )
    db.add(admin)
    print("[OK] Admin created: admin@example.com / Admin@123")
else:
    print("[INFO] Admin already exists")

db.commit()
db.close()

print("\n[SUCCESS] Database initialized!")
