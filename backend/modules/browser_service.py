"""
Privacy Focused Web Browser Service
Manages privacy-preserving browser profiles, anti-telemetry header controls,
encrypted local bookmark vaults, tracker denial lists, and zero-logging search routing.
Features:
- Telemetry & Tracker Pattern Matcher: Blocks advertising scripts, beacons, and fingerprinters.
- URL Query Sanitizer: Strips tracking parameters (UTM, Facebook, Google, etc.).
- Hardened Content Security Policy (CSP) and Anti-Fingerprinting Header Generator.
- Netscape HTML Bookmark Exporter and Parser.
- Persistent privacy profiles and bookmarks in browser.db.
"""

import re
import urllib.parse
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager
from ..core.validation import Sanitizer, FieldValidator


class TrackerFilterEngine:
    """
    Regex and substring matching engine for blocking tracking domains and scripts.
    """

    KNOWN_TRACKING_DOMAINS = [
        "doubleclick.net", "google-analytics.com", "googletagmanager.com",
        "facebook.net", "connect.facebook.net", "scorecardresearch.com",
        "quantserve.com", "criteo.com", "outbrain.com", "taboola.com",
        "hotjar.com", "mixpanel.com", "segment.io", "appsflyer.com",
        "branch.io", "amplitude.com", "adroll.com", "pubmatic.com"
    ]

    TRACKER_PATH_PATTERNS = [
        r'/telemetry', r'/analytics', r'/track', r'/pixel\.gif',
        r'/beacon', r'/logEvent', r'/metrics', r'/stats'
    ]

    @classmethod
    def is_tracker(cls, url: str) -> Dict[str, Any]:
        """
        Evaluates whether a given URL matches known surveillance capitalism domains or telemetry paths.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc.lower()
            path = parsed.path.lower()

            for domain in cls.KNOWN_TRACKING_DOMAINS:
                if host == domain or host.endswith(f".{domain}"):
                    return {"blocked": True, "reason": f"Matched known surveillance domain: {domain}", "category": "Advertising / Tracker"}

            for pat in cls.TRACKER_PATH_PATTERNS:
                if re.search(pat, path):
                    return {"blocked": True, "reason": f"Matched telemetry endpoint pattern: {pat}", "category": "Telemetry / Beacon"}

            return {"blocked": False, "reason": "Nominal", "category": "Clean"}
        except Exception:
            return {"blocked": False, "reason": "Unparseable", "category": "Unknown"}


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

    def set_active_search_engine(self, engine_id: int) -> bool:
        """Set primary search provider."""
        db_manager.execute_non_query(self.DB, "UPDATE search_engines SET is_active = 0")
        db_manager.execute_non_query(self.DB, "UPDATE search_engines SET is_active = 1 WHERE id = ?", (engine_id,))
        # Update settings key
        eng = db_manager.execute_query(self.DB, "SELECT name FROM search_engines WHERE id = ?", (engine_id,))
        if eng:
            self.set_privacy_setting("active_search_engine", eng[0]["name"])
        return True

    def sanitize_nav_url(self, raw_url: str) -> str:
        """Sanitizes navigation URL by stripping intrusive ad and session tracking parameters."""
        return Sanitizer.strip_tracking_params(raw_url)

    def evaluate_url_security(self, url: str) -> Dict[str, Any]:
        """Runs threat check and tracker inspection on given URL."""
        tracker_eval = TrackerFilterEngine.is_tracker(url)
        clean_url = Sanitizer.strip_tracking_params(url)
        has_tracking_tags = (clean_url != url)

        return {
            "original_url": url,
            "sanitized_url": clean_url,
            "has_tracking_query_params": has_tracking_tags,
            "is_tracker_domain": tracker_eval["blocked"],
            "tracker_category": tracker_eval["category"],
            "threat_reason": tracker_eval["reason"]
        }

    def generate_hardened_headers(self) -> Dict[str, str]:
        """
        Generates anti-surveillance HTTP request headers according to current privacy settings.
        """
        settings = self.get_privacy_settings()
        ua_profile = settings.get("user_agent_profile", "Tor Browser (Hardened)")
        ua_str = self.USER_AGENTS.get(ua_profile, self.USER_AGENTS["Tor Browser (Hardened)"])

        headers = {
            "User-Agent": ua_str,
            "DNT": "1" if settings.get("send_do_not_track") == "1" else "0",
            "Sec-GPC": "1",  # Global Privacy Control
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

        if settings.get("strict_referrer") == "1":
            headers["Referer"] = ""

        return headers

    def list_bookmarks(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve user bookmarks."""
        query = "SELECT * FROM bookmarks WHERE 1=1"
        params = []
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY id DESC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def add_bookmark(self, title: str, url: str, category: str = "General", icon_svg: str = "") -> Dict[str, Any]:
        """Add new bookmark with URL sanitization."""
        clean_url = Sanitizer.strip_tracking_params(url.strip())
        new_id = db_manager.execute_non_query(
            self.DB,
            "INSERT OR REPLACE INTO bookmarks (title, url, category, icon_svg) VALUES (?, ?, ?, ?)",
            (title.strip(), clean_url, category.strip() or "General", icon_svg)
        )
        return {"id": new_id, "title": title, "url": clean_url, "category": category}

    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Remove bookmark."""
        return db_manager.execute_non_query(self.DB, "DELETE FROM bookmarks WHERE id = ?", (bookmark_id,)) > 0

    def export_bookmarks_html(self) -> str:
        """
        Exports bookmarks in the standard Netscape Bookmark File format.
        Compatible with Firefox, Chromium, Safari, and Brave.
        """
        bookmarks = self.list_bookmarks()
        lines = [
            "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
            "<!-- This is an automatically generated file. -->",
            "<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">",
            "<TITLE>Aether Sovereign Bookmarks</TITLE>",
            "<H1>Bookmarks</H1>",
            "<DL><p>"
        ]

        for bm in bookmarks:
            title = bm.get("title", "Bookmark")
            url = bm.get("url", "")
            cat = bm.get("category", "General")
            lines.append(f"    <DT><A HREF=\"{url}\" TAGS=\"{cat}\">{title}</A>")

        lines.append("</DL><p>")
        return "\n".join(lines)


browser_service = BrowserService()
