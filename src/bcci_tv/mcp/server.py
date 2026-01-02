from fastmcp import FastMCP
import json
from typing import Optional
from bcci_tv.api.client import BCCIApiClient
from bcci_tv.api.utils import (
    filter_tournament_standings,
    simplify_standings,
    summarize_competitions,
    search_competitions as search_competitions_util
)

# Create FastMCP instance
mcp = FastMCP("bcci-tv")

@mcp.resource("tournaments://domestic/catalog")
async def get_domestic_tournaments_catalog() -> str:
    """
    Returns a minimal catalog of all domestic tournaments (CompetitionID and CompetitionName).
    Use this to look up domestic tournament IDs.
    """
    async with BCCIApiClient() as client:
        data = await client.get_domestic_competitions()
        all_comps = data.get("competition", [])
        catalog = summarize_competitions(all_comps)
        return json.dumps(catalog, indent=2)

@mcp.resource("tournaments://international/catalog")
async def get_international_tournaments_catalog() -> str:
    """
    Returns a minimal catalog of all international tournaments (CompetitionID and CompetitionName).
    Use this to look up international tournament IDs.
    """
    async with BCCIApiClient() as client:
        data = await client.get_international_competitions()
        all_comps = data.get("competition", [])
        catalog = summarize_competitions(all_comps)
        return json.dumps(catalog, indent=2)

@mcp.tool()
async def search_competitions(query: str, circuit: Optional[str] = None) -> list:
    """
    Searches for tournaments/competitions/series by name to find their ID.

    It is best to provide the circuit ('domestic' or 'international') if known
    from context to speed up the search and avoid multiple lookups.
    If circuit is not provided, domestic is searched first, followed by international.

    Args:
        query (str): The search term (e.g., 'Vijay Hazare Trophy', 'Ranji').
        circuit (str, optional): The circuit to search in ('domestic' or 'international').
    """
    async with BCCIApiClient() as client:
        results = []

        # Determine which circuits to search
        circuits_to_search = []
        if circuit in ["domestic", "international"]:
            circuits_to_search = [circuit]
        else:
            circuits_to_search = ["domestic", "international"]

        for c in circuits_to_search:
            if c == "domestic":
                data = await client.get_domestic_competitions()
            else:
                data = await client.get_international_competitions()

            all_comps = data.get("competition", [])
            matches = search_competitions_util(all_comps, query, circuit=c)
            results.extend(matches)

            # If we were searching without context and found matches in domestic,
            # we return them immediately as per "domestic first" logic
            if not circuit and results:
                break

        return results

@mcp.tool()
async def get_live_tournaments(circuit: Optional[str] = None) -> list:
    """
    Fetches and returns a list of live cricket tournaments/competitions.

    Args:
        circuit (str, optional): The circuit ('domestic' or 'international').
        Defaults to 'domestic' if unclear.
    """
    target_circuit = circuit if circuit in ["domestic", "international"] else "domestic"
    async with BCCIApiClient() as client:
        tournaments = await client.get_live_tournaments(circuit=target_circuit)
        return summarize_competitions(tournaments, circuit=target_circuit)

@mcp.tool()
async def get_tournament_details(competition_id: int, circuit: str) -> dict:
    """
    Fetches full metadata/details for a specific tournament/competition/series.
    Requires both the CompetitionID and the circuit.

    Args:
        competition_id (int): The unique ID of the competition.
        circuit (str): The circuit the tournament belongs to ('domestic' or 'international').
    """
    async with BCCIApiClient() as client:
        details = await client.get_competition_details(competition_id, circuit=circuit)
        if details:
            return details
        return {"error": f"Competition {competition_id} not found in {circuit} circuit"}

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
