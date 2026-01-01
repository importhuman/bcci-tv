from fastmcp import FastMCP
from bcci_tv.api.client import BCCIApiClient
from bcci_tv.api.utils import filter_tournament_standings, simplify_standings

# Create FastMCP instance
mcp = FastMCP("bcci-tv")

@mcp.tool()
async def get_competitions() -> list:
    """
    Fetches and returns a list of ALL cricket tournaments/competitions from bcci.tv.

    Returns:
        list: A list of dictionaries containing all tournament details.
    """
    async with BCCIApiClient() as client:
        return await client.get_competitions()

@mcp.tool()
async def get_live_tournaments() -> list:
    """
    Fetches and returns a list of live cricket tournaments/competitions from bcci.tv.

    Returns:
        list: A list of dictionaries containing live tournament details.
    """
    async with BCCIApiClient() as client:
        return await client.get_live_tournaments()

@mcp.tool()
async def get_tournament_standings(competition_id: int) -> dict:
    """
    Fetches the standings/points table for a specific tournament/competition.
    
    Returns a JSON object where teams are grouped by category (e.g., 'Group A') 
    and sorted by 'OrderNo'.
    
    AI Instructions: Always present this data to the user as a clean, 
    professionally formatted table. Include columns for: 
    Pos, Team, P (Played), W (Wins), L (Losses), D (Draws), Pts (Points), and NRR (Net Run Rate).
    
    Args:
        competition_id (int): The unique ID of the competition/tournament.
    """
    async with BCCIApiClient() as client:
        raw_data = await client.get_tournament_standings(competition_id)
        filtered = filter_tournament_standings(raw_data)
        return simplify_standings(filtered)

