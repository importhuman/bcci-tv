import pytest
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

    httpx_mock.add_response(url=mock_url, text=mock_raw_response, status_code=200)

    result = await api_client.get_tournament_standings(competition_id)

    # Verify the structure and content of the parsed JSON
    expected_fields = ["category", "points"]

    for field in expected_fields:
        assert field in result, f"Field '{field}' missing from response"
        assert isinstance(result[field], list), f"Field '{field}' should be a list"

    expected_fields = ["Category", "TeamName", "OrderNo"]
    for field in expected_fields:
        assert field in result["points"][0], f"Field '{field}' missing from response"
        assert isinstance(result["points"][0][field], str), (
            f"Field '{field}' should be a string"
        )


@pytest.mark.asyncio
async def test_get_tournament_schedule_intl(api_client, httpx_mock):
    # Read from fixture file
    with open("tests/fixtures/intl_schedule.js", "r") as f:
        mock_raw_response = f.read()

    competition_id = 236
    mock_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.INTERNATIONAL_SCHEDULE.format(
            CompetitionID=competition_id
        )
    )

    httpx_mock.add_response(url=mock_url, text=mock_raw_response, status_code=200)

    result = await api_client.get_tournament_schedule(
        competition_id, circuit="international"
    )

    assert isinstance(result, dict)
    assert "Matchsummary" in result
    assert isinstance(result["Matchsummary"], list)
    assert len(result["Matchsummary"]) == 5


@pytest.mark.asyncio
async def test_get_match_summary_overall(api_client, httpx_mock):
    with open("tests/fixtures/match_summary.js", "r") as f:
        mock_raw_response = (
            f.read() or 'callback({"status": true, "CurrentInnings": "1"});'
        )

    match_id = 999
    mock_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.DOMESTIC_MATCH_DETAILS.format(
            MatchID=match_id, suffix="matchsummary"
        )
    )

    httpx_mock.add_response(url=mock_url, text=mock_raw_response, status_code=200)

    result = await api_client.get_domestic_match_summary(match_id)
    assert "MatchSummary" in result
    assert isinstance(result["MatchSummary"], list)
    assert len(result["MatchSummary"]) == 1
    assert "MatchID", "CurrentInnings" in result["MatchSummary"][0]


@pytest.mark.asyncio
async def test_get_match_summary_innings(api_client, httpx_mock):
    with open("tests/fixtures/match_innings1.js", "r") as f:
        mock_raw_response = f.read() or 'callback({"Innings1": {"BattingCard": []}});'

    match_id = 999
    mock_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.DOMESTIC_MATCH_DETAILS.format(
            MatchID=match_id, suffix="Innings1"
        )
    )

    httpx_mock.add_response(url=mock_url, text=mock_raw_response, status_code=200)

    result = await api_client.get_domestic_match_summary(match_id, innings=1)
    assert "Innings1" in result
    # Verify filtering
    assert list(result["Innings1"].keys()) == [
        "BattingCard",
        "BowlingCard",
        "Extras",
        "FallOfWickets",
    ]


@pytest.mark.asyncio
async def test_get_international_match_summary_overall(api_client, httpx_mock):
    # TODO: Use new international match fixture instead of reusing domestic one
    # Reuse domestic fixture for structure check
    with open("tests/fixtures/match_summary.js", "r") as f:
        mock_raw_response = f.read()

    match_id = 888
    mock_url = BCCIApiClient.get_full_url(
        BCCIApiClient.Endpoints.INTERNATIONAL_MATCH_SUMMARY.format(MatchID=match_id)
    )

    httpx_mock.add_response(url=mock_url, text=mock_raw_response, status_code=200)

    result = await api_client.get_international_match_summary(match_id)
    assert "MatchSummary" in result
    assert isinstance(result["MatchSummary"], list)
    assert len(result["MatchSummary"]) == 1
    assert "MatchID", "CurrentInnings" in result["MatchSummary"][0]


@pytest.mark.asyncio
async def test_get_international_match_summary_innings(api_client, httpx_mock):
    # TODO: Use new international innings fixture instead of reusing domestic one
    # Reuse domestic fixture
    with open("tests/fixtures/match_innings1.js", "r") as f:
        mock_raw_response = f.read()

    match_id = 888
    innings_str = "Innings1"
    # Use full URL directly as it is not relative to scores.bcci.tv
    mock_url = BCCIApiClient.Endpoints.INTERNATIONAL_MATCH_INNINGS.format(
        MatchID=match_id, innings_str=innings_str
    )

    httpx_mock.add_response(url=mock_url, text=mock_raw_response, status_code=200)

    result = await api_client.get_international_match_summary(match_id, innings=1)
    assert innings_str in result
    # Verify filtering
    assert list(result[innings_str].keys()) == [
        "BattingCard",
        "BowlingCard",
        "Extras",
        "FallOfWickets",
    ]


def test_parse_jsonp():
    client = BCCIApiClient()

    # 1. Standard JSONP
    jsonp_text = 'callback({"key": "value"});'
    assert client._parse_jsonp(jsonp_text) == {"key": "value"}

    # 2. Pure JSON
    pure_json = '{"key": "value"}'
    assert client._parse_jsonp(pure_json) == {"key": "value"}

    # 3. Pure JSON containing parentheses (the edge case)
    json_with_parens = '{"graph": "(some data)", "id": 1}'
    assert client._parse_jsonp(json_with_parens) == {"graph": "(some data)", "id": 1}

    # 4. JSONP with different wrapper name
    different_wrapper = 'onScoringMatchsummary({"status": true});'
    assert client._parse_jsonp(different_wrapper) == {"status": True}
