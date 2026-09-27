"""
Clock and Timers Subsystem Service
High-precision temporal synchronization engine.
Features real-time world clock matrix with timezone offset delta calculations,
millisecond stopwatch lap ledger, and Pomodoro focus sprint cycles.
"""

import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any
from ..database_manager import db_manager


class ClockService:
    DB = "clocks.db"

    DEFAULT_CITIES = [
        ("UTC Coordinated Universal Time", "UTC", "Global", 1),
        ("New York (Wall St / Financial)", "America/New_York", "USA", 2),
        ("London (City / Greenwhich)", "Europe/London", "UK", 3),
        ("Zurich (Strategic Banking)", "Europe/Zurich", "Switzerland", 4),
        ("Dubai (GCC Operations)", "Asia/Dubai", "UAE", 5),
        ("Singapore (Southeast Asia Hub)", "Asia/Singapore", "Singapore", 6),
        ("Tokyo (Japan Standard)", "Asia/Tokyo", "Japan", 7),
        ("Sydney (Australian Eastern)", "Australia/Sydney", "Australia", 8),
        ("San Francisco (Silicon Valley)", "America/Los_Angeles", "USA", 9)
    ]

    def __init__(self):
        self._seed_default_cities()

    def _seed_default_cities(self):
        """Seed major geopolitical and financial time hubs."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM world_cities")
        if count and count[0]["count"] == 0:
            for city, tz, country, order in self.DEFAULT_CITIES:
                db_manager.execute_non_query(
                    self.DB,
                    "INSERT OR IGNORE INTO world_cities (city_name, timezone, country, display_order) VALUES (?, ?, ?, ?)",
                    (city, tz, country, order)
                )

    def get_world_clocks(self) -> List[Dict[str, Any]]:
        """Compute live world times across all registered strategic cities."""
        cities = db_manager.execute_query(self.DB, "SELECT * FROM world_cities ORDER BY display_order ASC")
        now_utc = datetime.datetime.now(ZoneInfo("UTC"))
        results = []

        for c in cities:
            try:
                tz = ZoneInfo(c["timezone"])
                loc_dt = now_utc.astimezone(tz)
                offset = loc_dt.utcoffset()
                offset_hrs = offset.total_seconds() / 3600 if offset else 0.0
                sign = "+" if offset_hrs >= 0 else ""
                results.append({
                    "id": c["id"],
                    "city": c["city_name"],
                    "timezone": c["timezone"],
                    "country": c["country"],
                    "time_str": loc_dt.strftime("%H:%M:%S"),
                    "date_str": loc_dt.strftime("%a, %b %d, %Y"),
                    "offset_str": f"UTC {sign}{offset_hrs:.1f}h",
                    "hours": loc_dt.hour,
                    "minutes": loc_dt.minute,
                    "seconds": loc_dt.second,
                    "is_day": 6 <= loc_dt.hour < 19
                })
            except Exception:
                pass

        return results

    def save_stopwatch_lap(self, session_id: str, lap_number: int, lap_time_ms: int, total_time_ms: int) -> Dict[str, Any]:
        """Record stopwatch lap split."""
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO stopwatch_laps (session_id, lap_number, lap_time_ms, total_time_ms)
               VALUES (?, ?, ?, ?)""",
            (session_id, lap_number, lap_time_ms, total_time_ms)
        )
        return {"id": new_id, "lap_number": lap_number, "lap_time_ms": lap_time_ms, "total_time_ms": total_time_ms}

    def get_stopwatch_laps(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve recorded laps for a session."""
        return db_manager.execute_query(
            self.DB,
            "SELECT * FROM stopwatch_laps WHERE session_id = ? ORDER BY lap_number ASC",
            (session_id,)
        )


clock_service = ClockService()
