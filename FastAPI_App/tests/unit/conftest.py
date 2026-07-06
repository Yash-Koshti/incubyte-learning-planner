import pytest_asyncio


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    yield


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    yield
