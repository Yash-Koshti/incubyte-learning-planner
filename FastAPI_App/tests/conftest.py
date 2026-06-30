from unittest.mock import AsyncMock, MagicMock

import app.dependencies.temporal as temporal_module
import pytest
import pytest_asyncio
from app.core.config import settings
from app.core.database import Base
from app.dependencies.db import get_db
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = settings.database_url.replace("/docprocessor", "/docprocessor_test")

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionFactory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(db_session: AsyncSession):
    yield
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(table.delete())
    await db_session.commit()


@pytest.fixture(autouse=True)
def mock_temporal_client(monkeypatch):
    mock_client = MagicMock()
    mock_client.start_workflow = AsyncMock()
    monkeypatch.setattr(temporal_module, "_temporal_client", mock_client)
    return mock_client


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
