import pytest
import json
from bcci_tv.mcp.server import (
    get_live_tournaments,
    get_tournament_standings,
    search_competitions,
    get_tournament_details,
    get_tournament_schedule,
    get_match_summary
)
from bcci_tv.api.client import BCCIApiClient

@pytest.mark.asyncio
async def test_get_live_tournaments_tool(httpx_mock):
    # Read raw JS fixture for the API mock
    with open("tests/fixtures/competitions.js", "r") as f:
        mock_raw_response = f.read()

    with open("tests/fixtures/live_tournaments_summary.json", "r") as f:
        expected_output = json.load(f)

    # Default is domestic
    httpx_mock.add_response(
        url=BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.DOMESTIC_COMPETITIONS),
        text=mock_raw_response,
        status_code=200
    )

    # Call the underlying function directly
    result = await get_live_tournaments.fn()

    # Assert against fixture
    assert result == expected_output

@pytest.mark.asyncio
async def test_search_competitions_tool_fallback(httpx_mock):
    with open("tests/fixtures/competitions.js", "r") as f:
        mock_raw_response = f.read()

    with open("tests/fixtures/search_cooch_results.json", "r") as f:
        expected_output = json.load(f)

    # Mock domestic (where we expect to find "COOCH")
    httpx_mock.add_response(
        url=BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.DOMESTIC_COMPETITIONS),
        text=mock_raw_response,
        status_code=200
    )

    # Search without circuit - should find in domestic and stop
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
        url=BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.DOMESTIC_COMPETITIONS),
        text=mock_raw_response,
        status_code=200
    )

    # Must provide circuit
    result = await get_tournament_details.fn(competition_id=competition_id, circuit="domestic")
    assert result == expected_output

@pytest.mark.asyncio
async def test_get_tournament_schedule_tool_intl(httpx_mock):
    competition_id = 236
    # Read raw JS fixture for API mock
    with open("tests/fixtures/intl_schedule.js", "r") as f:
        mock_raw_response = f.read()

    mock_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.INTERNATIONAL_SCHEDULE.format(CompetitionID=competition_id)
    )

    httpx_mock.add_response(
        url=mock_url,
        text=mock_raw_response,
        status_code=200
    )

    # Test upcoming filter
    result = await get_tournament_schedule.fn(
        competition_id=competition_id,
        circuit="international",
        match_status="upcoming"
    )

    assert len(result) == 5
    assert all(match["MatchStatus"].lower() == "upcoming" for match in result)

@pytest.mark.asyncio
async def test_get_match_summary_tool(httpx_mock):
    match_id = 999

    # 1. Mock overall summary
    with open("tests/fixtures/match_summary.js", "r") as f:
        summary_raw = f.read() or "callback({\"CurrentInnings\": \"2\"});"

    summary_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.DOMESTIC_MATCH_DETAILS.format(MatchID=match_id, suffix="matchsummary")
    )
    httpx_mock.add_response(url=summary_url, text=summary_raw, status_code=200)

    # 2. Mock Innings 1
    with open("tests/fixtures/match_innings1.js", "r") as f:
        innings_raw = f.read() or "callback({\"Innings1\": {\"BattingCard\": []}});"
    innings_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.DOMESTIC_MATCH_DETAILS.format(MatchID=match_id, suffix="Innings1")
    )
    httpx_mock.add_response(url=innings_url, text=innings_raw, status_code=200)

    # 3. Mock Innings 2 (reusing fixture for simplicity)
    innings2_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.DOMESTIC_MATCH_DETAILS.format(MatchID=match_id, suffix="Innings2")
    )

    httpx_mock.add_response(url=innings2_url, text=innings_raw, status_code=200)
    result = await get_match_summary.fn(match_id=match_id)

    assert "overall" in result
    assert "innings_details" in result
    assert len(result["innings_details"]) == 2
