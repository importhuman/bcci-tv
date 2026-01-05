import json
from bcci_tv.api.utils import (
    filter_live_competitions,
    filter_tournament_standings,
    simplify_standings,
    filter_matches_by_status,
)
from bcci_tv.api.client import BCCIApiClient


def test_filter_live_competitions():
    mock_data = {
        "livecompetition": [{"CompetitionID": "1"}, {"CompetitionID": "3"}],
        "competition": [
            {"CompetitionID": "1", "name": "Live Match A"},
            {"CompetitionID": "2", "name": "Finished Match B"},
            {"CompetitionID": "3", "name": "Live Match C"},
            {"CompetitionID": "4", "name": "Upcoming Match D"},
        ],
    }

    result = filter_live_competitions(mock_data)

    assert len(result) == 2
    assert result[0]["CompetitionID"] == "1"
    assert result[1]["CompetitionID"] == "3"
    assert all(c["CompetitionID"] in ["1", "3"] for c in result)


def test_filter_live_competitions_empty():
    mock_data = {"livecompetition": [], "competition": [{"CompetitionID": "1"}]}
    assert filter_live_competitions(mock_data) == []

    assert filter_live_competitions({}) == []


def test_filter_tournament_standings():
    # Read and parse JSONP fixture
    with open("tests/fixtures/standings.js", "r") as f:
        raw_text = f.read()

    # Read expected JSON result
    with open("tests/fixtures/filtered_standings.json", "r") as f:
        expected_filtered_result = json.load(f)

    with open("tests/fixtures/simplified_standings.json", "r") as f:
        expected_simplified_result = json.load(f)

    # We use the client's parser as a helper here
    client = BCCIApiClient()
    parsed_data = client._parse_jsonp(raw_text)

    filtered_result = filter_tournament_standings(parsed_data)
    assert filtered_result == expected_filtered_result

    simplified_result = simplify_standings(filtered_result)
    assert simplified_result == expected_simplified_result


def test_filter_tournament_standings_empty():
    assert filter_tournament_standings({}) == {}
    assert filter_tournament_standings({"category": []}) == {}


def test_filter_matches_by_status():
    # Read and parse the international schedule fixture
    with open("tests/fixtures/intl_schedule.js", "r") as f:
        raw_text = f.read()

    client = BCCIApiClient()
    parsed_data = client._parse_jsonp(raw_text)

    # Assert upcoming: 5 matches
    upcoming = filter_matches_by_status(parsed_data, "upcoming")
    assert len(upcoming) == 5

    # Assert live: 0 matches
    live = filter_matches_by_status(parsed_data, "live")
    assert len(live) == 0

    # Assert post: 0 matches
    post = filter_matches_by_status(parsed_data, "post")
    assert len(post) == 0
