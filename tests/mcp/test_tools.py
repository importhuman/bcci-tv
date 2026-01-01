import pytest
import json
from bcci_tv.mcp.server import get_live_tournaments
from bcci_tv.api.client import BCCIApiClient

@pytest.mark.asyncio
async def test_get_live_tournaments_tool(httpx_mock):
    # Read raw JS fixture for the API mock
    with open("tests/fixtures/competitions.js", "r") as f:
        mock_raw_response = f.read()

    # Read expected output from the new JSON fixture
    with open("tests/fixtures/live_tournaments.json", "r") as f:
        expected_output = json.load(f)

    mock_url = BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.COMPETITIONS)

    httpx_mock.add_response(
        url=mock_url,
        text=mock_raw_response,
        status_code=200
    )

    # Call the underlying function directly (FastMCP wraps it in a FunctionTool)
    result = await get_live_tournaments.fn()

    # Exact match assertion
    assert result == expected_output
