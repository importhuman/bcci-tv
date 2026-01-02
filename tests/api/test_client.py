import pytest
import json
from bcci_tv.api.client import BCCIApiClient

@pytest.mark.asyncio
async def test_get_domestic_competitions(api_client, httpx_mock):
    with open("tests/fixtures/competitions.js", "r") as f:
        mock_raw_response = f.read()

    url = BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.DOMESTIC_COMPETITIONS)
    httpx_mock.add_response(url=url, text=mock_raw_response, status_code=200)

    result = await api_client.get_domestic_competitions()

    # Verify the structure and content of the parsed JSON
    expected_fields = ["division", "competition", "livecompetition", "teams", "venues"]

    for field in expected_fields:
        assert field in result, f"Field '{field}' missing from response"
        assert isinstance(result[field], list), f"Field '{field}' should be a list"

@pytest.mark.asyncio
async def test_get_international_competitions(api_client, httpx_mock):
    with open("tests/fixtures/competitions.js", "r") as f:
        mock_raw_response = f.read()

    url = BCCIApiClient.get_full_url(BCCIApiClient.Endpoints.INTERNATIONAL_COMPETITIONS)
    httpx_mock.add_response(url=url, text=mock_raw_response, status_code=200)

    result = await api_client.get_international_competitions()

    # Verify the structure and content of the parsed JSON
    expected_fields = ["division", "competition", "livecompetition", "teams", "venues"]

    for field in expected_fields:
        assert field in result, f"Field '{field}' missing from response"
        assert isinstance(result[field], list), f"Field '{field}' should be a list"

@pytest.mark.asyncio
async def test_get_tournament_standings(api_client, httpx_mock):
    # Read from fixture file
    with open("tests/fixtures/standings.js", "r") as f:
        mock_raw_response = f.read()

    competition_id = 318
    mock_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.STANDINGS.format(CompetitionID=competition_id)
    )

    httpx_mock.add_response(
        url=mock_url,
        text=mock_raw_response,
        status_code=200
    )

    result = await api_client.get_tournament_standings(competition_id)

    # Verify the structure and content of the parsed JSON
    expected_fields = ["category", "points"]

    for field in expected_fields:
        assert field in result, f"Field '{field}' missing from response"
        assert isinstance(result[field], list), f"Field '{field}' should be a list"

    expected_fields = ["Category", "TeamName", "OrderNo"]
    for field in expected_fields:
        assert field in result["points"][0], f"Field '{field}' missing from response"
        assert isinstance(result["points"][0][field], str), f"Field '{field}' should be a string"
