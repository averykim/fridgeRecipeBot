import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Database URL is not defined. Please check .env file.")
# engine
engine = create_async_engine(DATABASE_URL,
                       pool_size=5,
                       max_overflow=10,
                       pool_recycle=3600,
                       pool_pre_ping=True,
                       echo=False
                       )

async_session_maker = async_sessionmaker(engine,
                                         class_=AsyncSession,
                                         expire_on_commit=False
                                         )

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session_maker() as session:
        yield session