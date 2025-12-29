import pytest
import pytest_asyncio
from bcci_tv.api.client import BCCIApiClient

@pytest_asyncio.fixture
async def api_client():
    async with BCCIApiClient() as client:
        yield client
