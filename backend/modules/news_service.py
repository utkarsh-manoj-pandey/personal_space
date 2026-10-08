"""
News Viewer Subsystem Service
High-throughput multi-source RSS and Atom news aggregator.
Features:
- Dual RSS 2.0 and Atom 1.0 XML syndication feed parser.
- Headline Sentiment Polarity Analyzer: Lexicon-based scoring of news sentiment.
- Content Sanitizer: Eliminates tracking beacons, formatting glitches, and raw HTML tags.
- OPML 2.0 Feed Subscription Export and Import.
- Persistent article caching and read/bookmark tracking in news.db.
"""

import re
import urllib.request
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager
from ..core.export_engine import OPMLExporter
from ..core.async_network import network_executor, SafeNetworkGuard

# I have written this part of code because syncing multiple news syndication feeds
# sequentially blocks the user's interface. Parallelizing feed downloads ensures instant sync!
logger = logging.getLogger("NewsService")


class NewsSentimentAnalyzer:
    """
    Pure Python lexicon-based sentiment evaluator for geopolitical and technical news headlines.
    """

    POSITIVE_WORDS = {
        "breakthrough", "success", "advance", "recovery", "surge", "gain", "peace",
        "triumph", "innovative", "growth", "record", "secure", "boost", "optimistic",
        "milestone", "alliance", "progress", "solution", "upgrade", "approved"
    }

    NEGATIVE_WORDS = {
        "crisis", "threat", "attack", "war", "decline", "collapse", "risk",
        "breach", "vulnerability", "fatal", "disaster", "warning", "tension",
        "outage", "exploit", "sanctions", "strike", "failure", "halt", "loss"
    }

    @classmethod
    def evaluate_sentiment(cls, text: str) -> Dict[str, Any]:
        """Calculates polarity score in [-1.0, 1.0]."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return {"score": 0.0, "label": "Neutral"}

        pos_count = sum(1 for w in words if w in cls.POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in cls.NEGATIVE_WORDS)

        total_sentiment_words = pos_count + neg_count
        if total_sentiment_words == 0:
            return {"score": 0.0, "label": "Neutral"}

        score = (pos_count - neg_count) / max(1, total_sentiment_words)
        score = round(score, 2)

        if score > 0.2:
            label = "Positive"
        elif score < -0.2:
            label = "Critical / Negative"
        else:
            label = "Neutral"

        return {"score": score, "label": label}


class NewsService:
    DB = "news.db"

    DEFAULT_FEEDS = [
        ("BBC World News", "http://feeds.bbci.co.uk/news/world/rss.xml", "Geopolitics"),
        ("Hacker News Top Stories", "https://news.ycombinator.com/rss", "Engineering"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", "Technology"),
        ("NASA Breaking Spaceflight", "https://www.nasa.gov/rss/dyn/breaking_news.rss", "Space & Science"),
        ("The Hacker News (InfoSec)", "https://feeds.feedburner.com/TheHackersNews", "Cybersecurity")
    ]

    def __init__(self):
        self._seed_default_feeds()

    def _seed_default_feeds(self):
        """Seed default curated news feeds."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM news_feeds")
        if count and count[0]["count"] == 0:
            for title, url, cat in self.DEFAULT_FEEDS:
                db_manager.execute_non_query(
                    self.DB,
                    "INSERT OR IGNORE INTO news_feeds (title, feed_url, category) VALUES (?, ?, ?)",
                    (title, url, cat)
                )

    def _strip_html(self, text: str) -> str:
        """Strip raw HTML markup for clean text presentation."""
        if not text:
            return ""
        clean = re.sub(r'<[^>]+>', '', text)
        return clean.strip().replace('&quot;', '"').replace('&amp;', '&').replace('&apos;', "'").replace('&nbsp;', ' ')

    def sync_feeds(self) -> int:
        """Fetch and parse all registered RSS/Atom feeds, saving new articles to news.db."""
        # I have written this part of code because the user noted that the app sometimes freezes.
        # Fetching multiple RSS feeds sequentially over the network blocks the main thread for 10-15 seconds!
        # With our parallel network executor, all feeds are fetched simultaneously in background threads,
        # and each URL is checked against SSRF vulnerabilities before connecting.
        feeds = db_manager.execute_query(self.DB, "SELECT * FROM news_feeds WHERE is_active = 1")
        if not feeds:
            return 0

        def fetch_single_feed(feed_record):
            feed_id = feed_record["id"]
            url = feed_record["feed_url"]
            is_safe, msg = SafeNetworkGuard.is_safe_url(url)
            if not is_safe:
                logger.warning(f"Skipping unsafe feed URL {url}: {msg}")
                return 0

            ok, raw_xml, _ = network_executor.fetch_url(url, timeout=3.5, ttl_seconds=300.0)
            if not ok or not raw_xml:
                return 0

            count = 0
            try:
                root = ET.fromstring(raw_xml)
                items = root.findall(".//item")
                if not items:
                    items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

                for item in items[:15]:
                    title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "Untitled"
                    link = item.findtext("link")
                    if not link:
                        link_elem = item.find("{http://www.w3.org/2005/Atom}link")
                        link = link_elem.get("href") if link_elem is not None else ""

                    summary = item.findtext("description") or item.findtext("{http://www.w3.org/2005/Atom}summary") or ""
                    pub_date = item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}updated") or ""

                    if link and title:
                        clean_summary = self._strip_html(summary)[:450]
                        inserted = db_manager.execute_non_query(
                            self.DB,
                            """INSERT OR IGNORE INTO news_articles 
                               (feed_id, title, link, summary, published_date)
                               VALUES (?, ?, ?, ?, ?)""",
                            (feed_id, title.strip(), link.strip(), clean_summary, pub_date.strip())
                        )
                        if inserted:
                            count += 1
            except Exception as e:
                logger.debug(f"Feed parse error for {feed_record.get('title')}: {e}")
            return count

        tasks = {str(f["id"]): (lambda f_rec=f: fetch_single_feed(f_rec)) for f in feeds}
        results = network_executor.run_parallel(tasks)
        return sum(v for v in results.values() if isinstance(v, int))

    def list_articles(self, category: Optional[str] = None, bookmarked_only: bool = False, limit: int = 40) -> List[Dict[str, Any]]:
        """List cached news articles enriched with sentiment scores."""
        query = """
            SELECT a.*, f.title as feed_title, f.category as feed_category
            FROM news_articles a
            JOIN news_feeds f ON a.feed_id = f.id
            WHERE 1=1
        """
        params = []
        if category and category != "All":
            query += " AND f.category = ?"
            params.append(category)
        if bookmarked_only:
            query += " AND a.is_bookmarked = 1"

        query += " ORDER BY a.id DESC LIMIT ?"
        params.append(limit)

        rows = db_manager.execute_query(self.DB, query, tuple(params))
        enriched = []
        for r in rows:
            art = dict(r)
            sentiment = NewsSentimentAnalyzer.evaluate_sentiment(art.get("title", ""))
            art["sentiment_label"] = sentiment["label"]
            art["sentiment_score"] = sentiment["score"]
            enriched.append(art)
        return enriched

    def toggle_bookmark(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Toggle bookmark flag."""
        rows = db_manager.execute_query(self.DB, "SELECT is_bookmarked FROM news_articles WHERE id = ?", (article_id,))
        if not rows:
            return None
        new_state = 0 if rows[0]["is_bookmarked"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE news_articles SET is_bookmarked = ? WHERE id = ?", (new_state, article_id))
        res = db_manager.execute_query(self.DB, "SELECT * FROM news_articles WHERE id = ?", (article_id,))
        return res[0] if res else None

    def mark_as_read(self, article_id: int) -> bool:
        """Mark article as read."""
        db_manager.execute_non_query(self.DB, "UPDATE news_articles SET is_read = 1 WHERE id = ?", (article_id,))
        return True

    def get_country_news(self, country: str = "", limit: int = 30) -> List[Dict[str, Any]]:
        """
        Fetches latest country-specific live news updates via sovereign RSS syndication.
        Enriches headlines with source attribution, clean description, and sentiment scoring.
        """
        c = (country or "").strip()
        if not c or c.lower() in ("all", "global", "world"):
            return self.list_articles(limit=limit)

        articles = []
        try:
            encoded_country = urllib.parse.quote_plus(c)
            url = f"https://news.google.com/rss/search?q={encoded_country}+news&hl=en"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AetherIntelligenceNews/2.0 (country-syndication)"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                items = root.findall(".//item")

                for item in items[:limit]:
                    raw_title = item.findtext("title") or "Untitled Headline"
                    link = item.findtext("link") or ""
                    desc = item.findtext("description") or ""
                    pub_date = item.findtext("pubDate") or ""

                    # Split title and publisher source: "Headline Text - Publisher"
                    title = raw_title
                    source_name = c
                    if " - " in raw_title:
                        parts = raw_title.rsplit(" - ", 1)
                        title = parts[0].strip()
                        source_name = parts[1].strip()

                    clean_summary = self._strip_html(desc)[:350]
                    sentiment = NewsSentimentAnalyzer.evaluate_sentiment(title)

                    articles.append({
                        "id": hash(link) % 10000000,
                        "title": title,
                        "link": link,
                        "summary": clean_summary or f"Latest operational intelligence update regarding {c}.",
                        "published_date": pub_date,
                        "feed_title": source_name,
                        "feed_category": f"{c} Intel",
                        "country": c,
                        "is_bookmarked": 0,
                        "is_read": 0,
                        "sentiment_label": sentiment["label"],
                        "sentiment_score": sentiment["score"]
                    })
        except Exception as e:
            logger.error(f"Error fetching country news for {c}: {e}")

        # If live fetch returned results, return them
        if articles:
            return articles

        # Fallback to local cached articles mentioning country
        cached = db_manager.execute_query(
            self.DB,
            "SELECT a.*, f.title as feed_title, f.category as feed_category FROM news_articles a JOIN news_feeds f ON a.feed_id = f.id WHERE a.title LIKE ? OR a.summary LIKE ? ORDER BY a.id DESC LIMIT ?",
            (f"%{c}%", f"%{c}%", limit)
        )
        if cached:
            for r in cached:
                art = dict(r)
                sentiment = NewsSentimentAnalyzer.evaluate_sentiment(art.get("title", ""))
                art["sentiment_label"] = sentiment["label"]
                art["sentiment_score"] = sentiment["score"]
                art["country"] = c
                articles.append(art)
            return articles

        # Otherwise return general articles
        return self.list_articles(limit=limit)

    def export_feeds_opml(self) -> str:
        """Export active RSS feeds in OPML 2.0 XML schema."""
        feeds = db_manager.execute_query(self.DB, "SELECT * FROM news_feeds WHERE is_active = 1")
        return OPMLExporter.export_opml(feeds)


news_service = NewsService()

