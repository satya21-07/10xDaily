import httpx
import logging
import xml.etree.ElementTree as ET
import hashlib
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)

RSS_URLS = {
    "for you": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "india": "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en",
    "world": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en",
    "business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-IN&gl=IN&ceid=IN:en",
    "health": "https://news.google.com/rss/headlines/section/topic/HEALTH?hl=en-IN&gl=IN&ceid=IN:en",
    "sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en",
    "entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en"
}

def extract_image_url(html_content: str) -> str | None:
    if not html_content:
        return None
    match = re.search(r'<img[^>]+src="([^">]+)"', html_content)
    if match:
        return match.group(1)
    return None

def fetch_rss_news(category: str, limit: int = 10) -> list[dict]:
    """Fetch and parse RSS feed for the given category."""
    cat_key = category.lower()
    url = RSS_URLS.get(cat_key, RSS_URLS["world"])
    
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
            description_html = item.findtext("description", "")
            
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

            # Generate stable ID from link
            article_id = hashlib.md5(link.encode('utf-8')).hexdigest()
            image_url = extract_image_url(description_html)
            if not image_url:
                image_url = f"https://picsum.photos/seed/{article_id}/800/400"

            article_data = {
                "id": article_id,
                "title": title,
                "summary": title, # Use title as summary for cleaner UI
                "source": source_text,
                "url": link,
                "image_url": image_url,
                "category": category,
                "published_at": published_at.isoformat(),
                "ai_summary": None,
                "language": "en",
                "is_saved": False
            }
            articles.append(article_data)
            
        return articles
    except Exception as e:
        logger.error(f"Error fetching RSS news for {category}: {e}")
        return []

def get_or_fetch_daily_news(category: str, limit: int = 10) -> list[dict]:
    """
    Main entrypoint. Fetches the news.
    """
    articles_data = fetch_rss_news(category, limit)
    return articles_data

