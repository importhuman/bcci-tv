import httpx
import logging
import json
from typing import Any, Dict, Optional

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

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0
        )

    @classmethod
    def get_full_url(cls, endpoint: str) -> str:
        """Helper to construct full URLs for testing or logging."""
        return f"{cls.BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    async def get_competitions(self) -> Dict[str, Any]:
        """Fetches competitions."""
        response = await self._make_request("GET", self.Endpoints.COMPETITIONS)
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