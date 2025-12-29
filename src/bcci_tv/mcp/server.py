from fastmcp import FastMCP
from bcci_tv.api.client import BCCIApiClient
from bcci_tv.api.utils import filter_live_competitions

# Create FastMCP instance
mcp = FastMCP("bcci-tv")

@mcp.tool()
async def get_live_tournaments() -> list:
    """
    Fetches and returns a list of live cricket tournaments/competitions from bcci.tv.
    
    Returns:
        list: A list of dictionaries containing live tournament details.
    """
    async with BCCIApiClient() as client:
        data = await client.get_competitions()
        return filter_live_competitions(data)
