import httpx
import logging
import xml.etree.ElementTree as ET
import hashlib
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)

# Direct publisher RSS feeds that include real article photojournalism images
RSS_FEEDS = {
    "for you": [
        {"url": "https://feeds.bbci.co.uk/news/rss.xml", "source": "BBC News"},
        {"url": "https://feeds.feedburner.com/ndtvnews-top-stories", "source": "NDTV"}
    ],
    "india": [
        {"url": "https://feeds.feedburner.com/ndtvnews-top-stories", "source": "NDTV"},
        {"url": "https://indianexpress.com/section/india/feed/", "source": "Indian Express"}
    ],
    "world": [
        {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC World"},
        {"url": "https://feeds.feedburner.com/ndtvnews-world-news", "source": "NDTV World"}
    ],
    "technology": [
        {"url": "https://techcrunch.com/feed/", "source": "TechCrunch"},
        {"url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "source": "BBC Tech"}
    ],
    "business": [
        {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source": "BBC Business"},
        {"url": "https://feeds.feedburner.com/ndtvprofit-latest", "source": "NDTV Profit"},
        {"url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "source": "CNBC"}
    ],
    "sports": [
        {"url": "https://feeds.bbci.co.uk/sport/rss.xml", "source": "BBC Sport"},
        {"url": "https://feeds.feedburner.com/ndtvsports-cricket", "source": "NDTV Cricket"}
    ],
    "entertainment": [
        {"url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "source": "BBC Entertainment"},
        {"url": "https://feeds.feedburner.com/ndtvmovies-latest", "source": "NDTV Movies"}
    ],
    "science": [
        {"url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "source": "BBC Science"},
        {"url": "https://www.sciencedaily.com/rss/all.xml", "source": "Science Daily"}
    ],
    "health": [
        {"url": "https://feeds.bbci.co.uk/news/health/rss.xml", "source": "BBC Health"},
        {"url": "https://feeds.feedburner.com/ndtvcooks-latest", "source": "NDTV Health"}
    ]
}

def extract_real_image(item: ET.Element, html_content: str) -> str | None:
    """Extract ONLY genuine publisher images from XML tags or description HTML."""
    # 1. Check all direct and nested XML elements for media / thumbnail URLs
    for elem in item.iter():
        tag_lower = elem.tag.lower()
        if any(k in tag_lower for k in ['thumbnail', 'content', 'enclosure']):
            url = elem.get('url') or elem.get('src') or elem.get('href')
            if url and url.startswith('http') and not any(x in url.lower() for x in ['1x1', 'pixel', 'favicon', 'spacer']):
                return url
        
        # Check if element text contains HTML with <img> tag (e.g. content:encoded)
        if elem.text and '<img' in elem.text:
            match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', elem.text)
            if match:
                img_src = match.group(1)
                if not any(x in img_src.lower() for x in ['1x1', 'pixel', 'tracking', 'favicon', 'clear.gif', 'feedburner']):
                    return img_src

    # 2. Check HTML description <img> tag
    if html_content:
        match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', html_content)
        if match:
            img_src = match.group(1)
            if not any(x in img_src.lower() for x in ['1x1', 'pixel', 'tracking', 'favicon', 'clear.gif', 'feedburner']):
                return img_src

    return None


def clean_html_summary(html_text: str) -> str:
    """Strip HTML tags and return clean text summary."""
    if not html_text:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    # Strip extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def fetch_rss_feed(feed_info: dict, category: str, limit: int = 10) -> list[dict]:
    url = feed_info["url"]
    default_source = feed_info.get("source", "News")
    articles = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=12.0, follow_redirects=True)
        if response.status_code != 200:
            return []
            
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        
        for item in items[:limit]:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub_date_str = item.findtext("pubDate", "")
            description_raw = item.findtext("description", "")
            
            if not title or not link:
                continue

            summary = clean_html_summary(description_raw)
            if not summary or len(summary) < 10:
                summary = title

            try:
                published_at = parsedate_to_datetime(pub_date_str) if pub_date_str else datetime.now(timezone.utc)
            except Exception:
                published_at = datetime.now(timezone.utc)

            article_id = hashlib.md5(link.encode('utf-8')).hexdigest()
            real_image = extract_real_image(item, description_raw)

            article_data = {
                "id": article_id,
                "title": title,
                "summary": summary,
                "source": default_source,
                "url": link,
                "image_url": real_image,  # ONLY real photo or None (no random stock photos!)
                "category": category,
                "published_at": published_at.isoformat(),
                "ai_summary": None,
                "language": "en",
                "is_saved": False
            }
            articles.append(article_data)
            
    except Exception as e:
        logger.warning(f"Failed to fetch feed {url}: {e}")
        
    return articles

def get_or_fetch_daily_news(category: str, limit: int = 15) -> list[dict]:
    """
    Fetches real news articles with authentic publisher photos.
    """
    cat_key = (category or "for you").lower()
    feeds = RSS_FEEDS.get(cat_key, RSS_FEEDS.get("for you", []))
    
    all_articles = []
    seen_links = set()

    for feed_info in feeds:
        feed_articles = fetch_rss_feed(feed_info, category, limit=limit)
        for art in feed_articles:
            if art["url"] not in seen_links:
                seen_links.add(art["url"])
                all_articles.append(art)
                
    # Sort articles by published date descending
    try:
        all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    except Exception:
        pass

    return all_articles[:limit]


def fetch_full_story(url: str, title: str, summary: str = "", source: str = "News") -> str:
    """
    Fetches the genuine news story paragraphs directly from the original news publisher.
    Uses 100% real journalistic content without any AI generation.
    """
    cache_key = f"news:full:{hashlib.md5((url or title).encode('utf-8')).hexdigest()}"
    from app.core.cache import get_cache, set_cache
    cached = get_cache(cache_key)
    if cached and isinstance(cached, str) and len(cached) > 60:
        return cached

    extracted_paragraphs = []

    # Direct extraction of genuine article paragraphs from the original publisher website
    if url and url.startswith("http"):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            resp = httpx.get(url, headers=headers, timeout=8.0, follow_redirects=True)
            if resp.status_code == 200:
                html = resp.text
                # Remove scripts, styles, header, nav, footer, ads
                html_clean = re.sub(r'<(script|style|nav|header|footer|aside)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
                
                # Find all paragraph tags
                matches = re.findall(r'<p[^>]*>(.*?)</p>', html_clean, flags=re.DOTALL | re.IGNORECASE)
                for m in matches:
                    clean_p = clean_html_summary(m)
                    # Filter out cookie notices, disclaimers, tiny strings, or spam
                    if len(clean_p) > 50 and not any(k in clean_p.lower() for k in [
                        "cookie", "privacy policy", "all rights reserved", "subscribe now",
                        "terms of use", "advertisement", "sign up", "read also", "click here", "newsletter"
                    ]):
                        extracted_paragraphs.append(clean_p)

                if extracted_paragraphs:
                    full_text = "\n\n".join(extracted_paragraphs[:10])
                    set_cache(cache_key, full_text, expire=86400)
                    return full_text
        except Exception as e:
            logger.debug(f"Direct article scraping failed for {url}: {e}")

    # Fallback to the authentic RSS summary provided by the publisher
    fallback_text = summary if (summary and len(summary) > 20) else title
    set_cache(cache_key, fallback_text, expire=86400)
    return fallback_text


