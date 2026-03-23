from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from sqlalchemy.orm import DeclarativeBase

# engine

Base = DeclarativeBase()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()