from fastmcp import FastMCP
from bcci_tv.api.client import BCCIApiClient

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
