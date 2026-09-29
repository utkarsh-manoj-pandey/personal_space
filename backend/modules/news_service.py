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
        feeds = db_manager.execute_query(self.DB, "SELECT * FROM news_feeds WHERE is_active = 1")
        new_articles_count = 0

        for f in feeds:
            feed_id = f["id"]
            url = f["feed_url"]
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "AetherIntelligenceReader/2.0 (offline-syndication)"}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)

                    # Handle standard RSS 2.0 item structure
                    items = root.findall(".//item")
                    # Handle Atom entry structure if RSS item is empty
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
                                new_articles_count += 1
            except Exception as e:
                logger.error(f"Error syncing feed {f['title']}: {e}")

        return new_articles_count

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

    def export_feeds_opml(self) -> str:
        """Export active RSS feeds in OPML 2.0 XML schema."""
        feeds = db_manager.execute_query(self.DB, "SELECT * FROM news_feeds WHERE is_active = 1")
        return OPMLExporter.export_opml(feeds)


news_service = NewsService()
