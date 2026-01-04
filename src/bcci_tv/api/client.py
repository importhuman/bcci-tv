import httpx
import logging
import json
import time
import asyncio
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
        DOMESTIC_COMPETITIONS = "/feeds/competition.js"
        INTERNATIONAL_COMPETITIONS = "/matchcentre/mc/competition.js"
        STANDINGS = "/feeds/stats/{CompetitionID}-groupstandings.js"
        DOMESTIC_SCHEDULE = "/feeds/{CompetitionID}-matchschedule.js"
        INTERNATIONAL_SCHEDULE = "/feeds-international/scoringfeeds/{CompetitionID}-matchschedule.js"
        DOMESTIC_MATCH_DETAILS = "/feeds/{MatchID}-{suffix}.js"
        INTERNATIONAL_MATCH_SUMMARY = "/feeds-international/scoringfeeds/{MatchID}-matchsummary.js"
        INTERNATIONAL_MATCH_INNINGS = "https://www.bcci.tv/fetch-inning?inning={innings_str}&competitionId={MatchID}&section=scorecard"

    class Cache:
        DOMESTIC_COMPETITIONS = "domestic_competitions.json"
        INTERNATIONAL_COMPETITIONS = "intl_competitions.json"

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

    async def _get_cached_feed(self, endpoint: str, cache_filename: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Generic helper to fetch and cache API feeds.
        """
        cache_file = self._get_cache_dir() / cache_filename

        if use_cache and cache_file.exists():
            if (time.time() - cache_file.stat().st_mtime) < 86400:
                try:
                    with open(cache_file, "r") as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to read cache {cache_filename}: {e}")

        response = await self._make_request("GET", endpoint)
        data = self._parse_jsonp(response.text)

        try:
            with open(cache_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to write cache {cache_filename}: {e}")

        return data

    async def get_domestic_competitions(self, use_cache: bool = True) -> Dict[str, Any]:
        """Fetches domestic competitions."""
        return await self._get_cached_feed(self.Endpoints.DOMESTIC_COMPETITIONS, self.Cache.DOMESTIC_COMPETITIONS, use_cache)

    async def get_international_competitions(self, use_cache: bool = True) -> Dict[str, Any]:
        """Fetches international competitions."""
        return await self._get_cached_feed(self.Endpoints.INTERNATIONAL_COMPETITIONS, self.Cache.INTERNATIONAL_COMPETITIONS, use_cache)

    async def get_live_tournaments(self, circuit: str = "domestic") -> List[Dict[str, Any]]:
        """
        Fetches and returns a list of live cricket tournaments/competitions for a specific circuit.
        """
        if circuit == "international":
            data = await self.get_international_competitions(use_cache=False)
        else:
            data = await self.get_domestic_competitions(use_cache=False)
        return filter_live_competitions(data)

    async def get_competition_details(self, competition_id: int, circuit: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves full details for a specific competition from the specified circuit catalog.
        """
        if circuit == "international":
            data = await self.get_international_competitions()
        else:
            data = await self.get_domestic_competitions()

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

    async def get_tournament_schedule(self, competition_id: int, circuit: str) -> Dict[str, Any]:
        """
        Fetches the match schedule for a specific tournament.
        """
        if circuit == "international":
            endpoint = self.Endpoints.INTERNATIONAL_SCHEDULE.format(CompetitionID=competition_id)
        else:
            endpoint = self.Endpoints.DOMESTIC_SCHEDULE.format(CompetitionID=competition_id)

        response = await self._make_request("GET", endpoint)
        return self._parse_jsonp(response.text)

    async def get_domestic_match_summary(self, match_id: int, innings: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetches the match summary for a domestic match.
        If innings is provided (1-4), fetches details for that specific innings.
        """
        if innings is not None and (innings < 1 or innings > 4):
            raise ValueError("Innings must be between 1 and 4")

        suffix = f"Innings{innings}" if innings is not None else "matchsummary"
        endpoint = self.Endpoints.DOMESTIC_MATCH_DETAILS.format(
            MatchID=match_id,
            suffix=suffix
        )
        response = await self._make_request("GET", endpoint)
        data = self._parse_jsonp(response.text)

        # If a specific innings was requested, filter the nested object
        if innings is not None:
            innings_key = f"Innings{innings}"
            if innings_key in data:
                inner_data = data[innings_key]
                keys_to_retain = ["BattingCard", "BowlingCard", "Extras", "FallOfWickets"]
                data[innings_key] = {
                    k: inner_data.get(k) for k in keys_to_retain if k in inner_data
                }

        return data

    async def get_international_match_summary(self, match_id: int, innings: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetches the match summary for an international match.
        If innings is provided (1-4), fetches details for that specific innings.
        """
        if innings is not None and (innings < 1 or innings > 4):
            raise ValueError("Innings must be between 1 and 4")

        if innings is None:
            endpoint = self.Endpoints.INTERNATIONAL_MATCH_SUMMARY.format(MatchID=match_id)
            response = await self._make_request("GET", endpoint)
            return self._parse_jsonp(response.text)
        else:
            innings_str = f"Innings{innings}"
            url = self.Endpoints.INTERNATIONAL_MATCH_INNINGS.format(
                MatchID=match_id,
                innings_str=innings_str
            )
            response = await self._make_request("GET", url)
            data = self._parse_jsonp(response.text)

            # Filter for specific keys
            if innings_str in data:
                inner_data = data[innings_str]
                keys_to_retain = ["BattingCard", "BowlingCard", "Extras", "FallOfWickets"]
                data[innings_str] = {
                    k: inner_data.get(k) for k in keys_to_retain if k in inner_data
                }
            return data

    def _parse_jsonp(self, text: str) -> Dict[str, Any]:
        """
        Parses JSONP-like response by removing the function wrapper.
        Example: oncomptetion({...}); -> {...}
        """
        text = text.strip()
        try:
            # If it starts with { or [, it is likely pure JSON
            if text.startswith(("{", "[")):
                return json.loads(text)

            # Otherwise, look for JSONP pattern: callback(...)
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
