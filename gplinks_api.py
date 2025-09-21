import logging
import aiohttp
from urllib.parse import quote_plus

from config import GPLINKS_API_KEY

logger = logging.getLogger(__name__)

async def generate_gplink(long_url: str) -> str | None:
    """Generates a shortlink using the GP Links API."""
    if not GPLINKS_API_KEY:
        logger.error("GP Links API Key not set in config.")
        return None

    # Replace with the actual GP Links API endpoint if it differs
    # This is a common pattern for URL shorteners, adjust if GP Links has a specific API path.
    api_url = f"https://gplinks.in/api?api={GPLINKS_API_KEY}&url={quote_plus(long_url)}"
    # Some shorteners also allow custom aliases, etc., check GP Links API docs.

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                data = await response.json()
                
                # Assuming GP Links API returns a JSON like {'status': 'success', 'shortenedUrl': 'https://gplinks.in/xyz'}
                # or {'status': 'error', 'message': '...'}. Adjust based on actual API response.
                if data.get("status") == "success" and data.get("shortenedUrl"):
                    logger.info(f"Successfully generated GP Link: {data['shortenedUrl']}")
                    return data["shortenedUrl"]
                elif data.get("error"):
                    logger.error(f"GP Links API error: {data.get('error')}")
                    return None
                else:
                    logger.error(f"GP Links API returned unexpected response: {data}")
                    return None
    except aiohttp.ClientError as e:
        logger.error(f"GP Links API request failed due to client error: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during GP Links API call: {e}")
        return None
