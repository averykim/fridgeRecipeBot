import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:1234@localhost:5432/naengpa_db"
)

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("Database URL is not defined. Please check .env file.")
# engine
engine = create_engine(SQLALCHEMY_DATABASE_URL,
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