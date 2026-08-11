import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

FALLBACK_QUOTE = {
    "text": "10x results require 10x thinking. Break the limits of what you believe is possible.",
    "author": "Antigravity AI"
}

def get_daily_quote() -> dict:
    """Fetches a daily motivational quote from Quotable API with a fallback."""
    try:
        # Use tags related to productivity, success, etc.
        url = "https://api.quotable.io/random?tags=success|wisdom|technology|knowledge|education|business"
        
        # Adding verify=False because the API certificate sometimes has issues, 
        # but in production a proper certificate trust store is better. 
        # Using timeout so it doesn't hang the Home page.
        with httpx.Client(timeout=5.0, verify=False) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Quotable API fetched quote: {data.get('content')}")
            
            return {
                "text": data.get("content", FALLBACK_QUOTE["text"]),
                "author": data.get("author", FALLBACK_QUOTE["author"])
            }
            
    except httpx.TimeoutException:
        logger.error("Quotable API timed out. Using fallback quote.")
        return FALLBACK_QUOTE
    except httpx.HTTPError as e:
        logger.error(f"Quotable API HTTP error: {e}. Using fallback quote.")
        return FALLBACK_QUOTE
    except Exception as e:
        logger.error(f"Error fetching quote from Quotable: {e}. Using fallback quote.")
        return FALLBACK_QUOTE
