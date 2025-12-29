from typing import Any, Dict, List

def filter_live_competitions(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filters the competitions list to only include those marked as live.
    
    The 'livecompetition' array is treated as the source of truth for IDs.
    """
    live_ids = {
        item.get("CompetitionID") 
        for item in data.get("livecompetition", []) 
        if item.get("CompetitionID")
    }
    
    all_competitions = data.get("competition", [])
    
    return [
        comp for comp in all_competitions 
        if comp.get("CompetitionID") in live_ids
    ]
