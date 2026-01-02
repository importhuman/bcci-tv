import pytest
import json
from bcci_tv.mcp.server import get_live_tournaments, get_tournament_standings, search_competitions, get_tournament_details
from bcci_tv.api.client import BCCIApiClient

@pytest.mark.asyncio
async def test_get_live_tournaments_tool(httpx_mock):
    # Read raw JS fixture for the API mock
    with open("tests/fixtures/competitions.js", "r") as f:
        mock_raw_response = f.read()

    with open("tests/fixtures/live_tournaments_summary.json", "r") as f:
        expected_output = json.load(f)

    mock_url = BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.COMPETITIONS)

    httpx_mock.add_response(
        url=mock_url,
        text=mock_raw_response,
        status_code=200
    )

    # Call the underlying function directly
    result = await get_live_tournaments.fn()

    # Assert against fixture
    assert result == expected_output

@pytest.mark.asyncio
async def test_search_competitions_tool(httpx_mock):
    with open("tests/fixtures/competitions.js", "r") as f:
        mock_raw_response = f.read()

    with open("tests/fixtures/search_cooch_results.json", "r") as f:
        expected_output = json.load(f)

    httpx_mock.add_response(
        url=BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.COMPETITIONS),
        text=mock_raw_response,
        status_code=200
    )

    # Search for a known string in the fixture (e.g., "COOCH")
    result = await search_competitions.fn(query="COOCH")

    assert result == expected_output

@pytest.mark.asyncio
async def test_get_tournament_standings_tool(httpx_mock):
    competition_id = 326
    # Read raw JS fixture for API mock
    with open("tests/fixtures/standings.js", "r") as f:
        mock_raw_response = f.read()

    # Read simplified JSON fixture for assertion
    with open("tests/fixtures/simplified_standings.json", "r") as f:
        expected_output = json.load(f)

    mock_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.STANDINGS.format(CompetitionID=competition_id)
    )

    httpx_mock.add_response(
        url=mock_url,
        text=mock_raw_response,
        status_code=200
    )

    result = await get_tournament_standings.fn(competition_id=competition_id)
    assert result == expected_output

@pytest.mark.asyncio
async def test_get_tournament_details_tool(httpx_mock):
    competition_id = 326
    with open("tests/fixtures/competitions.js", "r") as f:
        mock_raw_response = f.read()

    with open("tests/fixtures/tournament_details_326.json", "r") as f:
        expected_output = json.load(f)

    httpx_mock.add_response(
        url=BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.COMPETITIONS),
        text=mock_raw_response,
        status_code=200
    )

    result = await get_tournament_details.fn(competition_id=competition_id)
    assert result == expected_output
