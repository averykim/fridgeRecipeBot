import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Database URL is not defined. Please check .env file.")
# engine
engine = create_engine(DATABASE_URL,
                       pool_size=5,
                       max_overflow=10,
                       pool_recycle=3600,
                       pool_pre_ping=True,
                       echo=False
                       )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()