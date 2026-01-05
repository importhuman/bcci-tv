from fastmcp import FastMCP
import json
import asyncio
from typing import Optional
from bcci_tv.api.client import BCCIApiClient
from bcci_tv.api.utils import (
    filter_tournament_standings,
    simplify_standings,
    summarize_competitions,
    search_competitions as search_competitions_util,
    filter_matches_by_status,
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
async def get_tournament_schedule(
    competition_id: int, circuit: str, match_status: Optional[str] = None
) -> list:
    """
    Fetches the match schedule for a specific tournament.

    Args:
        competition_id (int): The unique ID of the competition.
        circuit (str): The circuit ('domestic' or 'international').
        match_status (str, optional): Filter matches by their status.
            Supported values:
            - 'upcoming': For matches that are yet to start.
            - 'live': For matches currently in progress.
            - 'post': For matches that have already completed.
    """
    async with BCCIApiClient() as client:
        data = await client.get_tournament_schedule(competition_id, circuit)

        if match_status:
            return filter_matches_by_status(data, match_status)

        return data.get("Matchsummary") or []


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


@mcp.tool()
async def get_domestic_match_summary(
    match_id: int, innings: Optional[int] = None
) -> dict:
    """
    Fetches the summary for a specific domestic match.
    If no innings is specified, it automatically retrieves the overall summary
    and all completed innings details.

    Args:
        match_id (int): The unique ID of the match.
        innings (int, optional): Specific innings number (1-4) to retrieve.
    """
    async with BCCIApiClient() as client:
        # 1. If user specified a particular innings, get only that.
        if innings is not None:
            return await client.get_domestic_match_summary(match_id, innings)

        # 2. Get the match summary without any innings (overall summary).
        overall_data = await client.get_domestic_match_summary(match_id)

        # Match data is nested within 'MatchSummary' list
        match_summary_list = overall_data.get("MatchSummary", [])
        overall_summary = match_summary_list[0] if match_summary_list else {}

        # 3. Use CurrentInnings to determine how many innings to fetch.
        # User confirmed we can assume this is a string value.
        current_innings_str = overall_summary.get("CurrentInnings", "0")
        try:
            num_innings = int(current_innings_str)
        except (ValueError, TypeError):
            num_innings = 0

        # 4. Collect details for each innings concurrently.
        innings_details = []
        if num_innings > 0:
            tasks = [
                client.get_domestic_match_summary(match_id, i)
                for i in range(1, num_innings + 1)
            ]
            innings_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(innings_results):
                if not isinstance(result, Exception):
                    innings_details.append(result)

        return {"overall": overall_summary, "innings_details": innings_details}


@mcp.tool()
async def get_intl_match_summary(match_id: int, innings: Optional[int] = None) -> dict:
    """
    Fetches the summary for a specific international match.
    If no innings is specified, it automatically retrieves the overall summary
    and all completed innings details.

    Args:
        match_id (int): The unique ID of the match.
        innings (int, optional): Specific innings number (1-4) to retrieve.
    """
    async with BCCIApiClient() as client:
        # 1. If user specified a particular innings, get only that.
        if innings is not None:
            return await client.get_international_match_summary(match_id, innings)

        # 2. Get the match summary without any innings (overall summary).
        overall_data = await client.get_international_match_summary(match_id)

        # Match data is nested within 'MatchSummary' list
        match_summary_list = overall_data.get("MatchSummary", [])
        overall_summary = match_summary_list[0] if match_summary_list else {}

        # 3. Use CurrentInnings to determine how many innings to fetch.
        current_innings_str = overall_summary.get("CurrentInnings", "0")
        try:
            num_innings = int(current_innings_str)
        except (ValueError, TypeError):
            num_innings = 0

        # 4. Collect details for each innings concurrently.
        innings_details = []
        if num_innings > 0:
            tasks = [
                client.get_international_match_summary(match_id, i)
                for i in range(1, num_innings + 1)
            ]
            innings_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(innings_results):
                if not isinstance(result, Exception):
                    innings_details.append(result)

        return {"overall": overall_summary, "innings_details": innings_details}
