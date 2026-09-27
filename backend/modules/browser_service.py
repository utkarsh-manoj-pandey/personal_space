"""
Privacy Focused Web Browser Service
Manages privacy-preserving browser profiles, anti-telemetry header controls,
encrypted local bookmark vaults, tracker denial lists, and zero-logging search routing.
"""

from typing import List, Dict, Any, Optional
from ..database_manager import db_manager


class BrowserService:
    DB = "browser.db"

    USER_AGENTS = {
        "Tor Browser (Hardened)": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Linux Firefox ESR (Privacy Edition)": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "macOS Safari (Anti-Fingerprinting)": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Chromium Secure Sandbox": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    def __init__(self):
        self._seed_default_browser_data()

    def _seed_default_browser_data(self):
        """Populate initial privacy engines and default privacy bookmarks if not present."""
        # Seed search engines
        eng_count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM search_engines")
        if eng_count and eng_count[0]["count"] == 0:
            engines = [
                ("DuckDuckGo", "https://duckduckgo.com/?q=", 1),
                ("Brave Search", "https://search.brave.com/search?q=", 0),
                ("Startpage", "https://www.startpage.com/sp/search?query=", 0),
                ("SearXNG Public", "https://searx.be/search?q=", 0),
                ("Qwant Privacy", "https://www.qwant.com/?q=", 0),
            ]
            for eng in engines:
                db_manager.execute_non_query(
                    self.DB,
                    "INSERT INTO search_engines (name, search_url, is_active) VALUES (?, ?, ?)",
                    eng
                )

        # Seed privacy defaults
        defaults = {
            "user_agent_profile": "Tor Browser (Hardened)",
            "block_trackers": "1",
            "block_fingerprinting": "1",
            "send_do_not_track": "1",
            "disable_webrtc_leak": "1",
            "strict_referrer": "1",
            "active_search_engine": "DuckDuckGo"
        }
        for k, v in defaults.items():
            db_manager.execute_non_query(
                self.DB,
                "INSERT OR IGNORE INTO privacy_settings (key, value) VALUES (?, ?)",
                (k, v)
            )

        # Seed starter privacy bookmarks
        bm_count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM bookmarks")
        if bm_count and bm_count[0]["count"] == 0:
            bookmarks = [
                ("DuckDuckGo Privacy", "https://duckduckgo.com", "Search", "search"),
                ("Brave Search", "https://search.brave.com", "Search", "shield"),
                ("Electronic Frontier Foundation", "https://www.eff.org", "Privacy", "lock"),
                ("OpenStreetMap", "https://www.openstreetmap.org", "Maps", "map"),
                ("Wikipedia Portal", "https://en.wikipedia.org", "Knowledge", "book-open"),
                ("Ars Technica", "https://arstechnica.com", "Technology", "cpu"),
                ("Hacker News", "https://news.ycombinator.com", "Engineering", "terminal")
            ]
            for bm in bookmarks:
                db_manager.execute_non_query(
                    self.DB,
                    "INSERT OR IGNORE INTO bookmarks (title, url, category, icon_svg) VALUES (?, ?, ?, ?)",
                    bm
                )

    def get_privacy_settings(self) -> Dict[str, str]:
        """Fetch all current privacy shields and header configuration."""
        rows = db_manager.execute_query(self.DB, "SELECT key, value FROM privacy_settings")
        return {r["key"]: r["value"] for r in rows}

    def set_privacy_setting(self, key: str, value: str) -> bool:
        """Update a specific privacy setting."""
        db_manager.execute_non_query(
            self.DB,
            "INSERT INTO privacy_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value))
        )
        return True

    def get_user_agents(self) -> Dict[str, str]:
        """Return the dictionary of available privacy-hardened user agent signatures."""
        return self.USER_AGENTS

    def get_search_engines(self) -> List[Dict[str, Any]]:
        """List all privacy search engines and currently active engine."""
        return db_manager.execute_query(self.DB, "SELECT * FROM search_engines ORDER BY id ASC")

    def set_active_engine(self, engine_name: str) -> bool:
        """Activate a chosen search engine."""
        db_manager.execute_non_query(self.DB, "UPDATE search_engines SET is_active = 0")
        db_manager.execute_non_query(self.DB, "UPDATE search_engines SET is_active = 1 WHERE name = ?", (engine_name,))
        self.set_privacy_setting("active_search_engine", engine_name)
        return True

    def get_search_url_for_query(self, query: str) -> str:
        """Construct the full target URL for an arbitrary user query string."""
        active_engine = db_manager.execute_query(
            self.DB,
            "SELECT search_url FROM search_engines WHERE is_active = 1 LIMIT 1"
        )
        base_url = active_engine[0]["search_url"] if active_engine else "https://duckduckgo.com/?q="
        import urllib.parse
        return f"{base_url}{urllib.parse.quote_plus(query.strip())}"

    def list_bookmarks(self) -> List[Dict[str, Any]]:
        """List all bookmarks ordered by category."""
        return db_manager.execute_query(self.DB, "SELECT * FROM bookmarks ORDER BY category ASC, title ASC")

    def add_bookmark(self, title: str, url: str, category: str = "General", icon_svg: str = "bookmark") -> Dict[str, Any]:
        """Save a new privacy bookmark."""
        new_id = db_manager.execute_non_query(
            self.DB,
            "INSERT INTO bookmarks (title, url, category, icon_svg) VALUES (?, ?, ?, ?)",
            (title.strip(), url.strip(), category.strip(), icon_svg.strip())
        )
        rows = db_manager.execute_query(self.DB, "SELECT * FROM bookmarks WHERE id = ?", (new_id,))
        return rows[0] if rows else {}

    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Remove a bookmark from local storage."""
        count = db_manager.execute_non_query(self.DB, "DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        return count > 0


browser_service = BrowserService()
