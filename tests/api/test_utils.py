import pytest
from bcci_tv_mcp.api.utils import filter_live_competitions

def test_filter_live_competitions():
    mock_data = {
        "livecompetition": [
            {"CompetitionID": "1"},
            {"CompetitionID": "3"}
        ],
        "competition": [
            {"CompetitionID": "1", "name": "Live Match A"},
            {"CompetitionID": "2", "name": "Finished Match B"},
            {"CompetitionID": "3", "name": "Live Match C"},
            {"CompetitionID": "4", "name": "Upcoming Match D"}
        ]
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
