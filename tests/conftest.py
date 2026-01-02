import pytest
import pytest_asyncio
from pathlib import Path
from bcci_tv.api.client import BCCIApiClient

@pytest.fixture(autouse=True)
def mock_cache_dir(monkeypatch, tmp_path):
    """Ensure tests use a temporary cache directory."""
    monkeypatch.setattr(BCCIApiClient, "_get_cache_dir", lambda self: tmp_path)
    return tmp_path

@pytest_asyncio.fixture
async def api_client():
    async with BCCIApiClient() as client:
        yield client
