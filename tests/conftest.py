import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport
from app.core.database import engine, Base, get_db
from app.main import app

# 1. Setup Test DB
TEST_DATABASE_URL = "postgresql+asyncpg://fridge:fridgepass@localhost:5435/fridgedb_test"

test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

# 2. DB dependency overriding (use test db instead of original db)
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# 3. Initialize Test DB automatically (execute 1 time before/after)
@pytest_asyncio.fixture(autouse=True)
async def setup_and_teardown_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 4. API test async client
@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client