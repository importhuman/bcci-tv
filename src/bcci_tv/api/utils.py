from typing import Any, Dict, List, Optional

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

def summarize_competitions(competitions: List[Dict[str, Any]], circuit: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Reduces competition objects to only include CompetitionID and CompetitionName.
    Optionally injects the circuit name.
    """
    results = []
    for c in competitions:
        summary = {
            "CompetitionID": c.get("CompetitionID"),
            "CompetitionName": c.get("CompetitionName")
        }
        if circuit:
            summary["circuit"] = circuit
        results.append(summary)
    return results

def search_competitions(competitions: List[Dict[str, Any]], query: str, circuit: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Searches for competitions by name (case-insensitive) and returns their summaries.
    """
    query = query.lower()
    filtered = [
        c for c in competitions
        if query in c.get("CompetitionName", "").lower()
    ]
    return summarize_competitions(filtered, circuit=circuit)

def filter_tournament_standings(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Filters and groups tournament standings by category.

    1. Returns empty dict if 'category' array is empty or missing.
    2. Groups teams from 'points' by their 'Category'.
    3. Sorts teams within each category by 'OrderNo' ascending.
    """
    categories = data.get("category", [])
    if not categories:
        return {}

    # Extract the string values from category objects (e.g. "Group A")
    # and initialize the result dictionary with those strings as keys
    category_names = [cat.get("Category") for cat in categories if cat.get("Category")]
    grouped_standings = {name: [] for name in category_names}

    points = data.get("points", [])
    for team in points:
        team_cat = team.get("Category")
        if team_cat in grouped_standings:
            grouped_standings[team_cat].append(team)

    # Sort each group by OrderNo (ascending)
    for cat in grouped_standings:
        grouped_standings[cat].sort(key=lambda x: int(x.get("OrderNo", 0)))

    return grouped_standings

def simplify_standings(standings: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Simplifies the grouped standings by keeping only specific keys.
    """
    keys_to_keep = [
        "TeamName", "Matches", "Wins", "Loss", "Tied", "NoResult",
        "Points", "Draw", "ForTeams", "AgainstTeam", "NetRunRate",
        "Quotient", "OrderNo", "MatchPoints"
    ]

    simplified = {}
    for category, teams in standings.items():
        simplified_teams = []
        for team in teams:
            simplified_team = {
                key: team.get(key)
                for key in keys_to_keep
            }
            simplified_teams.append(simplified_team)
        simplified[category] = simplified_teams

    return simplified
