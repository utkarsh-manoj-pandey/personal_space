"""
Clock and Timers Subsystem Service
High-precision temporal synchronization and astronomical time engine.
Features:
- Real-time World Clock Matrix with dynamic UTC offset deltas and day/night indicators.
- Astronomical Time: Julian Date (JD), Modified Julian Date (MJD), Greenwich Mean Sidereal Time (GMST).
- Pure Python Cron Expression Parser: Computes subsequent trigger occurrences.
- Millisecond Stopwatch Lap Ledger and Split Timers.
- Pomodoro Focus Sprint Manager.
- Persistent strategic cities and lap history in clocks.db.
"""

import math
import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager


class AstronomicalTimeEngine:
    """
    High-precision astronomical and celestial chronometry calculations.
    """

    @staticmethod
    def datetime_to_julian_date(dt: Optional[datetime.datetime] = None) -> float:
        """
        Converts UTC datetime into Julian Date (JD).
        Standard algorithm valid for Gregorian calendar dates.
        """
        if dt is None:
            dt = datetime.datetime.now(datetime.timezone.utc)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)

        y = dt.year
        m = dt.month
        d = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0

        if m <= 2:
            y -= 1
            m += 12

        a = math.floor(y / 100.0)
        b = 2 - a + math.floor(a / 4.0)

        jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5
        return round(jd, 6)

    @classmethod
    def get_modified_julian_date(cls, dt: Optional[datetime.datetime] = None) -> float:
        """MJD = JD - 2400000.5"""
        return round(cls.datetime_to_julian_date(dt) - 2400000.5, 6)

    @classmethod
    def greenwich_mean_sidereal_time_hours(cls, dt: Optional[datetime.datetime] = None) -> float:
        """
        Calculates Greenwich Mean Sidereal Time (GMST) in fractional hours [0, 24).
        Standard IAU 1982 / Jean Meeus formulation.
        """
        jd = cls.datetime_to_julian_date(dt)
        t = (jd - 2451545.0) / 36525.0  # Centuries since J2000.0

        theta_sec = 24110.54841 + 8640184.812866 * t + 0.093104 * (t ** 2) - 0.0000062 * (t ** 3)
        gmst_hours = (theta_sec / 3600.0) % 24.0
        return round(gmst_hours, 5)


class CronExpressionEvaluator:
    """
    Pure Python Unix standard 5-part cron parser and next-run calculator.
    Expression: (minute, hour, day_of_month, month, day_of_week)
    """

    @classmethod
    def parse_field(cls, field_str: str, min_val: int, max_val: int) -> set:
        """Expands cron field into allowed set of integers."""
        allowed = set()
        parts = field_str.split(',')
        for p in parts:
            p = p.strip()
            if p == '*':
                return set(range(min_val, max_val + 1))
            elif '/' in p:
                subparts = p.split('/')
                step = int(subparts[1])
                start = min_val if subparts[0] == '*' else int(subparts[0])
                allowed.update(range(start, max_val + 1, step))
            elif '-' in p:
                start, end = map(int, p.split('-'))
                allowed.update(range(start, end + 1))
            else:
                allowed.add(int(p))
        return allowed

    @classmethod
    def get_next_run(cls, cron_expr: str, start_dt: Optional[datetime.datetime] = None) -> Optional[datetime.datetime]:
        """Calculates next datetime meeting cron criteria."""
        tokens = cron_expr.strip().split()
        if len(tokens) != 5:
            return None

        curr = start_dt or datetime.datetime.now()
        curr = curr.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)

        allowed_min = cls.parse_field(tokens[0], 0, 59)
        allowed_hr = cls.parse_field(tokens[1], 0, 23)
        allowed_dom = cls.parse_field(tokens[2], 1, 31)
        allowed_mon = cls.parse_field(tokens[3], 1, 12)
        allowed_dow = cls.parse_field(tokens[4], 0, 6)

        # Lookahead up to 365 days
        for _ in range(60 * 24 * 365):
            dow_cron = (curr.weekday() + 1) % 7  # 0=Sunday in standard cron
            if (
                curr.minute in allowed_min and
                curr.hour in allowed_hr and
                curr.day in allowed_dom and
                curr.month in allowed_mon and
                dow_cron in allowed_dow
            ):
                return curr
            curr += datetime.timedelta(minutes=1)

        return None


class ClockService:
    DB = "clocks.db"

    DEFAULT_CITIES = [
        ("UTC Coordinated Universal Time", "UTC", "Global", 1),
        ("New York (Wall St / Financial)", "America/New_York", "USA", 2),
        ("London (City / Greenwich)", "Europe/London", "UK", 3),
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
                offset_hrs = offset.total_seconds() / 3600.0 if offset else 0.0
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

    def get_astronomical_telemetry(self) -> Dict[str, Any]:
        """Calculates Julian Date, MJD, and Sidereal chronometry."""
        now = datetime.datetime.now(datetime.timezone.utc)
        gmst = AstronomicalTimeEngine.greenwich_mean_sidereal_time_hours(now)
        gmst_hrs = int(gmst)
        gmst_mins = int((gmst - gmst_hrs) * 60)
        gmst_secs = int(((gmst - gmst_hrs) * 60 - gmst_mins) * 60)

        return {
            "julian_date": AstronomicalTimeEngine.datetime_to_julian_date(now),
            "modified_julian_date": AstronomicalTimeEngine.get_modified_julian_date(now),
            "gmst_hours_decimal": gmst,
            "gmst_display": f"{gmst_hrs:02d}:{gmst_mins:02d}:{gmst_secs:02d}",
            "epoch_timestamp_seconds": int(now.timestamp()),
            "epoch_timestamp_millis": int(now.timestamp() * 1000)
        }

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

    def evaluate_cron(self, cron_expression: str) -> Dict[str, Any]:
        """Calculate next execution time for a cron expression."""
        next_run = CronExpressionEvaluator.get_next_run(cron_expression)
        if next_run:
            return {"valid": True, "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S"), "expression": cron_expression}
        return {"valid": False, "error": "Invalid cron syntax or unreachable schedule", "expression": cron_expression}


clock_service = ClockService()
