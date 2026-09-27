"""
News Viewer Subsystem Service
High-throughput multi-source RSS and Atom news aggregator.
Maintains persistent article caches in SQLite, category partitioning,
read/bookmark status, and distraction-free reader parsing.
"""

import re
import urllib.request
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager

logger = logging.getLogger("NewsService")


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
        """Strip raw HTML markup for pristine clean text presentation."""
        if not text:
            return ""
        clean = re.sub(r'<[^>]+>', '', text)
        return clean.strip().replace('&quot;', '"').replace('&amp;', '&').replace('&apos;', "'")

    def sync_feeds(self) -> int:
        """Fetch and parse all registered RSS feeds, saving new articles to news.db."""
        feeds = db_manager.execute_query(self.DB, "SELECT * FROM news_feeds WHERE is_active = 1")
        new_articles_count = 0

        for f in feeds:
            feed_id = f["id"]
            url = f["feed_url"]
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)

                    # Handle standard RSS 2.0 channel/item structure
                    items = root.findall(".//item")
                    # Handle Atom entry structure if RSS item is empty
                    if not items:
                        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

                    for item in items[:15]:  # Limit per feed to prevent bloat
                        title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "Untitled"
                        link = item.findtext("link")
                        if not link:
                            link_elem = item.find("{http://www.w3.org/2005/Atom}link")
                            link = link_elem.get("href") if link_elem is not None else ""

                        summary = item.findtext("description") or item.findtext("{http://www.w3.org/2005/Atom}summary") or ""
                        pub_date = item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}updated") or ""

                        if link and title:
                            clean_summary = self._strip_html(summary)[:400]
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
        """List cached news articles."""
        # Run a quick sync if no articles present
        count_res = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM news_articles")
        if not count_res or count_res[0]["count"] == 0:
            self.sync_feeds()

        query = """
            SELECT a.*, f.title as source_title, f.category 
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

        return db_manager.execute_query(self.DB, query, tuple(params))

    def toggle_bookmark(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Toggle bookmark flag on an article."""
        rows = db_manager.execute_query(self.DB, "SELECT is_bookmarked FROM news_articles WHERE id = ?", (article_id,))
        if not rows:
            return None
        new_val = 0 if rows[0]["is_bookmarked"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE news_articles SET is_bookmarked = ? WHERE id = ?", (new_val, article_id))
        return {"id": article_id, "is_bookmarked": new_val}

    def mark_read(self, article_id: int) -> None:
        """Mark article as read."""
        db_manager.execute_non_query(self.DB, "UPDATE news_articles SET is_read = 1 WHERE id = ?", (article_id,))


news_service = NewsService()
