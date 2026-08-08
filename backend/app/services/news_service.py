import httpx
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from app.models.news import NewsArticle

logger = logging.getLogger(__name__)

RSS_URLS = {
    "india": "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en",
    "world": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en"
}

def fetch_rss_news(category: str, limit: int = 10) -> list[dict]:
    """Fetch and parse RSS feed for the given category."""
    url = RSS_URLS.get(category.lower(), RSS_URLS["world"])
    
    try:
        response = httpx.get(url, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        
        articles = []
        for item in items[:limit]:
            title_text = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date_str = item.findtext("pubDate", "")
            source_text = item.findtext("source", "Google News")
            
            # The title usually contains the source at the end " - Source Name"
            # Let's clean up the title if possible
            title = title_text
            if " - " in title_text:
                parts = title_text.rsplit(" - ", 1)
                title = parts[0]
                if not source_text or source_text == "Google News":
                    source_text = parts[1]
                    
            try:
                published_at = parsedate_to_datetime(pub_date_str) if pub_date_str else datetime.now(timezone.utc)
            except Exception:
                published_at = datetime.now(timezone.utc)

            article_data = {
                "title": title,
                "summary": "Read the full article for more details.", # RSS doesn't give good summaries
                "source": source_text,
                "url": link,
                "image_url": None, # Standard RSS doesn't consistently provide images
                "category": category.capitalize(),
                "published_at": published_at.isoformat(),
                "ai_summary": None
            }
            articles.append(article_data)
            
        return articles
    except Exception as e:
        logger.error(f"Error fetching RSS news for {category}: {e}")
        return []

def get_or_fetch_daily_news(category: str, limit: int = 10) -> list[dict]:
    """
    Main entrypoint. Fetches the news. We don't necessarily save this to DB 
    since news is highly ephemeral. We just fetch and return. Caching is handled at the API level.
    """
    # Simply fetch from RSS directly (caching will prevent spamming Google)
    articles_data = fetch_rss_news(category, limit)
    
    # We assign mock IDs so the frontend loop has keys if needed, 
    # but the frontend schema expects NewsArticle.
    # In Pydantic v2, we can just return dicts and it validates to the schema.
    for i, article in enumerate(articles_data):
        article["id"] = i + 1
        
    return articles_data
