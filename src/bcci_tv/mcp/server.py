from fastmcp import FastMCP
import json
from bcci_tv.api.client import BCCIApiClient
from bcci_tv.api.utils import filter_tournament_standings, simplify_standings

# Create FastMCP instance
mcp = FastMCP("bcci-tv")

@mcp.resource("tournaments://catalog")
async def get_tournaments_catalog() -> str:
    """
    Returns a minimal catalog of all tournaments/competitions/series (CompetitionID and CompetitionName).
    Use this to look up tournament IDs without calling a tool.
    """
    async with BCCIApiClient() as client:
        data = await client.get_competitions()
        all_comps = data.get("competition", [])
        catalog = [
            {
                "CompetitionID": c.get("CompetitionID"),
                "CompetitionName": c.get("CompetitionName")
            }
            for c in all_comps
        ]
        return json.dumps(catalog, indent=2)

@mcp.tool()
async def search_competitions(query: str) -> list:
    """
    Searches for tournaments/competitions/series by name to find their ID.
    Use this to find the CompetitionID required for other tools.

    Args:
        query (str): The search term (e.g., 'Vijay Hazare Trophy', 'Ranji').
    """
    async with BCCIApiClient() as client:
        data = await client.get_competitions()
        all_comps = data.get("competition", [])
        query = query.lower()
        return [
            {
                "CompetitionID": c.get("CompetitionID"),
                "CompetitionName": c.get("CompetitionName")
            }
            for c in all_comps
            if query in c.get("CompetitionName", "").lower()
        ]

@mcp.tool()
async def get_live_tournaments() -> list:
    """
    Fetches and returns a list of live cricket tournaments/competitions.
    Returns only a summary (ID and Name) to save tokens.
    """
    async with BCCIApiClient() as client:
        tournaments = await client.get_live_tournaments()
        return [
            {
                "CompetitionID": c.get("CompetitionID"),
                "CompetitionName": c.get("CompetitionName")
            }
            for c in tournaments
        ]

@mcp.tool()
async def get_tournament_details(competition_id: int) -> dict:
    """
    Fetches full metadata/details for a specific tournament/competition/series.
    Use this to get dates, category, and other info once you have a CompetitionID.

    Args:
        competition_id (int): The unique ID of the competition.
    """
    async with BCCIApiClient() as client:
        details = await client.get_competition_details(competition_id)
        return details if details else {"error": "Competition not found"}

@mcp.tool()
async def get_tournament_standings(competition_id: int) -> dict:
    """
    Fetches the standings for a specific tournament/competition/series.

    Returns a JSON object where teams are grouped by category (e.g., 'Group A')
    and sorted by 'OrderNo'.

    AI Instructions: Always present this data to the user as a clean,
    professionally formatted Markdown table. Include columns for:
    Pos, Team, P (Played), W (Wins), L (Losses), D (Draws), Pts (Points), and NRR (Net Run Rate).

    Args:
        competition_id (int): The unique ID of the competition/tournament.
    """
    async with BCCIApiClient() as client:
        raw_data = await client.get_tournament_standings(competition_id)
        filtered = filter_tournament_standings(raw_data)
        return simplify_standings(filtered)
