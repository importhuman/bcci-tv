import httpx
import logging
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, List
from bcci_tv.api.utils import filter_live_competitions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BCCIApiClient:
    """
    Client for interacting with the BCCI scores API.
    """
    BASE_URL = "https://scores.bcci.tv"

    class Endpoints:
        COMPETITIONS = "/feeds/competition.js"
        STANDINGS = "/feeds/stats/{CompetitionID}-groupstandings.js"

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0
        )

    def _get_cache_dir(self) -> Path:
        """Determines the local cache directory."""
        cache_dir = Path.home() / ".bcci-tv" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @classmethod
    def get_full_url(cls, endpoint: str) -> str:
        """Helper to construct full URLs for testing or logging."""
        return f"{cls.BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    async def get_competitions(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetches competitions, using a local cache if available and fresh.
        """
        cache_file = self._get_cache_dir() / "competitions.json"
        
        if use_cache and cache_file.exists():
            # Check TTL (24 hours = 86400 seconds)
            if (time.time() - cache_file.stat().st_mtime) < 86400:
                try:
                    with open(cache_file, "r") as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to read cache: {e}")

        # Fetch from API
        response = await self._make_request("GET", self.Endpoints.COMPETITIONS)
        data = self._parse_jsonp(response.text)
        
        # Save to cache
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")
            
        return data

    async def get_live_tournaments(self) -> List[Dict[str, Any]]:
        """
        Fetches and returns a list of live cricket tournaments/competitions.
        Calls API instead of using cached response.
        """
        data = await self.get_competitions(use_cache=False)
        return filter_live_competitions(data)

    async def get_competition_details(self, competition_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves full details for a specific competition from the catalog.
        """
        data = await self.get_competitions()
        all_comps = data.get("competition", [])
        str_id = str(competition_id)
        for comp in all_comps:
            if str(comp.get("CompetitionID")) == str_id:
                return comp
        return None
    
    async def get_tournament_standings(self, competition_id: int) -> Dict[str, Any]:
        """
        Fetches standings for a specific tournament.
        """
        endpoint = self.Endpoints.STANDINGS.format(CompetitionID=competition_id)
        response = await self._make_request("GET", endpoint)
        return self._parse_jsonp(response.text)

    def _parse_jsonp(self, text: str) -> Dict[str, Any]:
        """
        Parses JSONP-like response by removing the function wrapper.
        Example: oncomptetion({...}); -> {...}
        """
        try:
            start = text.find('(')
            end = text.rfind(')')
            if start != -1 and end != -1:
                json_str = text[start + 1:end]
                return json.loads(json_str)
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {str(e)}")
            raise

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """
        Internal method to handle HTTP requests.
        Returns the raw Response object.
        """
        try:
            response = await self.client.request(method, endpoint, params=params)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An error occurred during request to {endpoint}: {str(e)}")
            raise

    async def close(self):
        """Closes the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()