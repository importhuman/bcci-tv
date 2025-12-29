import asyncio
import json
from bcci_tv_mcp.api.client import BCCIApiClient

async def main():
    async with BCCIApiClient() as client:
        try:
            print("Fetching competitions...")
            competitions = await client.get_competitions()
            print("Successfully fetched competitions:")
            print(json.dumps(competitions, indent=2))
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
