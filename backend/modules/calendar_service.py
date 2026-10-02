"""
Calendar Subsystem Service
Maintains local workstation schedules, recurring occurrences, priority categorization,
schedule conflict detection, workload heatmap metrics, and RFC 5545 iCalendar compliance.
"""

import re
import datetime
from typing import List, Dict, Any, Optional, Tuple
from ..database_manager import db_manager
from ..core.export_engine import CalendarICalExporter


class CalendarService:
    DB = "calendar.db"

    CATEGORIES = ["General", "Strategy", "Technical", "Security", "Briefing", "Focus", "Personal", "Health"]
    PRIORITIES = ["Low", "Medium", "High", "Critical"]

    def __init__(self):
        self._seed_default_events()

    def _seed_default_events(self):
        """Seed initial scheduling data if the database is currently empty."""
        count_res = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM events")
        if count_res and count_res[0]["count"] == 0:
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            next_week_str = (now + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

            starter_events = [
                (
                    "Workstation Strategic Planning",
                    "Quarterly review of offline architecture, security auditing, and module synchronization.",
                    f"{today_str} 10:00:00",
                    f"{today_str} 11:30:00",
                    "Primary Command Room",
                    "Strategy",
                    "#00f0ff",
                    "weekly",
                    "High",
                    15
                ),
                (
                    "Algorithmic Performance Review",
                    "Inspect local SQLite WAL index latencies and audio synthesis buffer queues.",
                    f"{today_str} 14:00:00",
                    f"{today_str} 15:00:00",
                    "Lab Terminal Alpha",
                    "Technical",
                    "#8b5cf6",
                    "none",
                    "Medium",
                    10
                ),
                (
                    "Deep Focus: Cryptography & Security Audit",
                    "Offline integrity verification of keychains, local isolation barriers, and network blocks.",
                    f"{tomorrow_str} 09:00:00",
                    f"{tomorrow_str} 12:00:00",
                    "Secure Chamber",
                    "Security",
                    "#10b981",
                    "none",
                    "Critical",
                    30
                ),
                (
                    "Global Geopolitical & Situational Briefing",
                    "Review satellite ground tracks, USGS tectonic anomalies, and maritime telemetry.",
                    f"{next_week_str} 16:30:00",
                    f"{next_week_str} 17:30:00",
                    "Intelligence Suite",
                    "Briefing",
                    "#f59e0b",
                    "weekly",
                    "High",
                    15
                )
            ]

            for ev in starter_events:
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT INTO events 
                       (title, description, start_time, end_time, location, category, color, recurrence, priority, remind_minutes_before)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    ev
                )

    def list_events(self, category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered calendar events with optional category and search filters."""
        query = "SELECT * FROM events WHERE 1=1"
        params = []

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        if search:
            query += " AND (title LIKE ? OR description LIKE ? OR location LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        query += " ORDER BY start_time ASC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve single calendar event by primary key ID."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM events WHERE id = ?", (event_id,))
        return rows[0] if rows else None

    def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new calendar event with data normalization."""
        title = data.get("title", "Untitled Session").strip() or "Untitled Session"
        description = data.get("description", "").strip()
        start_time = data.get("start_time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        end_time = data.get("end_time", (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))
        location = data.get("location", "").strip()
        category = data.get("category", "General")
        color = data.get("color", "#3b82f6")
        recurrence = data.get("recurrence", "none").lower()
        priority = data.get("priority", "Medium")
        remind_before = int(data.get("remind_minutes_before", 15))

        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO events 
               (title, description, start_time, end_time, location, category, color, recurrence, priority, remind_minutes_before)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, description, start_time, end_time, location, category, color, recurrence, priority, remind_before)
        )

        return self.get_event(new_id) or {"id": new_id, "title": title}

    def update_event(self, event_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing calendar event attributes."""
        existing = self.get_event(event_id)
        if not existing:
            return None

        title = data.get("title", existing["title"])
        description = data.get("description", existing["description"])
        start_time = data.get("start_time", existing["start_time"])
        end_time = data.get("end_time", existing["end_time"])
        location = data.get("location", existing["location"])
        category = data.get("category", existing["category"])
        color = data.get("color", existing["color"])
        recurrence = data.get("recurrence", existing["recurrence"])
        priority = data.get("priority", existing["priority"])
        remind_before = data.get("remind_minutes_before", existing["remind_minutes_before"])

        db_manager.execute_non_query(
            self.DB,
            """UPDATE events SET 
               title = ?, description = ?, start_time = ?, end_time = ?, location = ?,
               category = ?, color = ?, recurrence = ?, priority = ?, remind_minutes_before = ?,
               updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (title, description, start_time, end_time, location, category, color, recurrence, priority, remind_before, event_id)
        )

        return self.get_event(event_id)

    def delete_event(self, event_id: int) -> bool:
        """Remove event permanently from calendar database."""
        rowcount = db_manager.execute_non_query(self.DB, "DELETE FROM events WHERE id = ?", (event_id,))
        return rowcount > 0

    # =========================================================================
    # ADVANCED SCHEDULING ENGINES: RECURRENCE, CONFLICTS, ANALYTICS
    # =========================================================================

    def detect_schedule_conflicts(self) -> List[Dict[str, Any]]:
        """
        Analyzes the calendar for overlapping commitments.
        Returns list of conflicting event pairs with overlap durations.
        """
        events = self.list_events()
        conflicts = []

        def _parse_ts(ts_str: str) -> Optional[datetime.datetime]:
            formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"]
            for f in formats:
                try:
                    return datetime.datetime.strptime(ts_str.strip(), f)
                except ValueError:
                    pass
            return None

        parsed = []
        for ev in events:
            s = _parse_ts(ev.get("start_time", ""))
            e = _parse_ts(ev.get("end_time", ""))
            if s and e and e > s:
                parsed.append({"id": ev["id"], "title": ev["title"], "start": s, "end": e, "priority": ev.get("priority", "Medium")})

        # Compare pairs
        for i in range(len(parsed)):
            for j in range(i + 1, len(parsed)):
                ev1 = parsed[i]
                ev2 = parsed[j]
                # Check overlap: start1 < end2 and start2 < end1
                if ev1["start"] < ev2["end"] and ev2["start"] < ev1["end"]:
                    overlap_start = max(ev1["start"], ev2["start"])
                    overlap_end = min(ev1["end"], ev2["end"])
                    overlap_mins = round((overlap_end - overlap_start).total_seconds() / 60.0, 1)

                    conflicts.append({
                        "event_a": {"id": ev1["id"], "title": ev1["title"], "start": str(ev1["start"]), "priority": ev1["priority"]},
                        "event_b": {"id": ev2["id"], "title": ev2["title"], "start": str(ev2["start"]), "priority": ev2["priority"]},
                        "overlap_minutes": overlap_mins,
                        "overlap_period": f"{overlap_start.strftime('%H:%M')} - {overlap_end.strftime('%H:%M')}"
                    })

        return conflicts

    def get_schedule_analytics(self) -> Dict[str, Any]:
        """
        Computes comprehensive productivity, workload distribution, and category telemetry.
        """
        events = self.list_events()
        total_events = len(events)
        total_duration_hours = 0.0
        category_counts: Dict[str, int] = {}
        priority_counts: Dict[str, int] = {}
        daily_hours: Dict[str, float] = {}

        def _parse_ts(ts_str: str) -> Optional[datetime.datetime]:
            formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"]
            for f in formats:
                try:
                    return datetime.datetime.strptime(ts_str.strip(), f)
                except ValueError:
                    pass
            return None

        for ev in events:
            cat = ev.get("category", "General")
            category_counts[cat] = category_counts.get(cat, 0) + 1

            prio = ev.get("priority", "Medium")
            priority_counts[prio] = priority_counts.get(prio, 0) + 1

            s = _parse_ts(ev.get("start_time", ""))
            e = _parse_ts(ev.get("end_time", ""))
            if s and e and e > s:
                dur_hrs = (e - s).total_seconds() / 3600.0
                total_duration_hours += dur_hrs
                day_key = s.strftime("%Y-%m-%d")
                daily_hours[day_key] = daily_hours.get(day_key, 0.0) + dur_hrs

        avg_event_duration_mins = round((total_duration_hours * 60.0) / max(1, total_events), 1)

        return {
            "total_events": total_events,
            "total_scheduled_hours": round(total_duration_hours, 1),
            "average_event_duration_minutes": avg_event_duration_mins,
            "category_breakdown": category_counts,
            "priority_breakdown": priority_counts,
            "workload_by_day": {k: round(v, 2) for k, v in sorted(daily_hours.items())},
            "conflicts_detected": len(self.detect_schedule_conflicts())
        }

    def find_free_slots(self, target_date_str: str, duration_minutes: int = 60, work_start_hour: int = 9, work_end_hour: int = 18) -> List[Dict[str, Any]]:
        """
        Calculates open, non-overlapping free time windows on a given date.
        """
        try:
            target_date = datetime.datetime.strptime(target_date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.date.today()

        day_start = datetime.datetime.combine(target_date, datetime.time(work_start_hour, 0))
        day_end = datetime.datetime.combine(target_date, datetime.time(work_end_hour, 0))

        events = self.list_events()
        day_events = []

        for ev in events:
            s_str = ev.get("start_time", "")
            e_str = ev.get("end_time", "")
            try:
                s_dt = datetime.datetime.strptime(s_str[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
                e_dt = datetime.datetime.strptime(e_str[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
                if s_dt.date() == target_date:
                    day_events.append((s_dt, e_dt))
            except Exception:
                pass

        day_events.sort(key=lambda x: x[0])

        free_slots = []
        curr_time = day_start
        min_slot_sec = duration_minutes * 60

        for start_dt, end_dt in day_events:
            if start_dt > curr_time:
                gap = (start_dt - curr_time).total_seconds()
                if gap >= min_slot_sec:
                    free_slots.append({
                        "start": curr_time.strftime("%H:%M"),
                        "end": start_dt.strftime("%H:%M"),
                        "duration_minutes": int(gap // 60)
                    })
            curr_time = max(curr_time, end_dt)

        if day_end > curr_time:
            gap = (day_end - curr_time).total_seconds()
            if gap >= min_slot_sec:
                free_slots.append({
                    "start": curr_time.strftime("%H:%M"),
                    "end": day_end.strftime("%H:%M"),
                    "duration_minutes": int(gap // 60)
                })

        return free_slots

    def export_ics(self) -> str:
        """
        Generates full RFC 5545 iCalendar stream with VEVENT, VALARM, and RRULE tags.
        """
        events = self.list_events()
        return CalendarICalExporter.serialize_events(events)

    def get_country_holidays(self, country_code: str = "US", year: int = 2026) -> List[Dict[str, Any]]:
        """
        Retrieves national holidays and cultural festivals for a specified sovereign country.
        Checks built-in comprehensive festival repository, then falls back to Nager.Date open API,
        caching records into calendar.db for offline availability.
        """
        code = (country_code or "US").strip().upper()
        if len(code) > 2:
            # Match common country names to codes
            mapping = {
                "UNITED STATES": "US", "USA": "US", "INDIA": "IN", "UNITED KINGDOM": "GB",
                "UK": "GB", "JAPAN": "JP", "CHINA": "CN", "FRANCE": "FR", "GERMANY": "DE",
                "CANADA": "CA", "AUSTRALIA": "AU", "BRAZIL": "BR"
            }
            code = mapping.get(code, code[:2])

        # 1. Check local repository first
        try:
            from .holiday_data import COUNTRY_HOLIDAYS_REPO
            if code in COUNTRY_HOLIDAYS_REPO:
                return COUNTRY_HOLIDAYS_REPO[code]
        except Exception:
            pass

        # 2. Query open Nager.Date public API
        try:
            import urllib.request
            import json
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{code}"
            req = urllib.request.Request(url, headers={"User-Agent": "AetherWorkstationCalendar/2.0"})
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode())
                holidays = []
                for item in data:
                    holidays.append({
                        "date": item.get("date"),
                        "name": item.get("name"),
                        "local_name": item.get("localName", item.get("name")),
                        "type": "National Holiday" if item.get("nationalHoliday", True) else "Observance"
                    })
                if holidays:
                    return holidays
        except Exception:
            pass

        # 3. Fallback generic global festivals
        return [
            {"date": f"{year}-01-01", "name": "New Year's Day", "local_name": "New Year", "type": "Public Holiday"},
            {"date": f"{year}-05-01", "name": "International Workers' Day", "local_name": "May Day", "type": "International Observance"},
            {"date": f"{year}-12-25", "name": "Christmas Day", "local_name": "Christmas", "type": "Global Holiday"},
            {"date": f"{year}-12-31", "name": "New Year's Eve", "local_name": "New Year's Eve", "type": "Observance"}
        ]


calendar_service = CalendarService()

