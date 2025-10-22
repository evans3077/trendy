# core/services/kenya_news.py
import requests
from bs4 import BeautifulSoup
import feedparser
import time
import random

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# A prioritized list of RSS feed URLs for Kenyan / regional news.
# These were chosen because they expose machine-readable feeds (RSS/Atom).
RSS_FEEDS = [
    # Standard Media (explicit RSS)
    "https://www.standardmedia.co.ke/rss/headlines.php",
    "https://www.standardmedia.co.ke/rss/kenya.php",
    # Africanews (pan-Africa)
    "https://www.africanews.com/feed/rss",
    # AllAfrica (aggregator)
    "https://allafrica.com/tools/headlines/africa/africa/index.rss",  # generic; will try site
    # Business Daily (common listing, try a couple variants)
    "https://www.businessdailyafrica.com/bd/news/feed/",  # common feed path
    "https://www.businessdailyafrica.com/feed/",
    # Nation (try a couple reasonable feed endpoints)
    "https://nation.africa/feeds/podcast",  # fallback; sites sometimes vary
    "https://nation.africa/kenya/rss",      # try possible pattern
    "https://nation.africa/rss",
]

def _parse_feed(url, limit=10):
    """Return list of titles from a feed URL, handling errors."""
    try:
        d = feedparser.parse(url)
        entries = d.get('entries', [])
        titles = []
        for e in entries[:limit]:
            # try several fields for a clean headline
            title = e.get('title') or e.get('headline') or e.get('summary')
            if title:
                titles.append(title.strip())
        return titles
    except Exception:
        return []

def _scrape_html_headlines(url, selectors, limit=10):
    """Fallback HTML scraping using provided CSS selectors."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for sel in selectors:
            for h in soup.select(sel)[:limit]:
                txt = h.get_text(strip=True)
                if txt:
                    results.append(txt)
        return results[:limit]
    except Exception:
        return []

def scrape_kenya_news(limit=10):
    """
    Robust Kenya news aggregator:
    1) Try RSS feeds first (fast, stable).
    2) If not enough items, fallback to targeted HTML scrapes for specific sites.
    Returns a list of cleaned headlines (deduped; meaningful length).
    """
    titles = []

    # 1) Try RSS feeds
    for feed in RSS_FEEDS:
        if len(titles) >= limit:
            break
        new = _parse_feed(feed, limit=limit - len(titles))
        for t in new:
            if t and t not in titles:
                titles.append(t)

    # 2) If RSS didn't return enough, fallback to scraping well-known pages.
    if len(titles) < limit:
        # nation.africa homepage (fallback selectors)
        nation_selectors = [
            "a.story-card__link",    # common pattern
            "h3 a", "h2 a", "a.title"
        ]
        n = _scrape_html_headlines("https://nation.africa/kenya", nation_selectors, limit=limit - len(titles))
        for t in n:
            if t and t not in titles:
                titles.append(t)
        if len(titles) >= limit:
            return _clean_headlines(titles, limit)

        # the-star
        star_selectors = ["a.article-title", "h4.title a", "h2.title a", ".entry-title a"]
        s = _scrape_html_headlines("https://www.the-star.co.ke/news/", star_selectors, limit=limit - len(titles))
        for t in s:
            if t and t not in titles:
                titles.append(t)
        if len(titles) >= limit:
            return _clean_headlines(titles, limit)

        # businessdaily
        bda_selectors = ["a.story-link", "h3.article-title a", "h2.title a"]
        b = _scrape_html_headlines("https://www.businessdailyafrica.com/", bda_selectors, limit=limit - len(titles))
        for t in b:
            if t and t not in titles:
                titles.append(t)

    # Final cleaning and filter: remove very short strings / junk
    return _clean_headlines(titles, limit)

def _clean_headlines(titles, limit):
    out = []
    for t in titles:
        # ignore extremely short tokens, e.g., 'Video', 'Latest'
        if not t or len(t.split()) < 3:
            continue
        # basic sanitization
        txt = t.replace("\n", " ").strip()
        if txt and txt not in out:
            out.append(txt)
        if len(out) >= limit:
            break
    return out[:limit]
