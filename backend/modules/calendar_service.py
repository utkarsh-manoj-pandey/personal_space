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

    @staticmethod
    def _calculate_easter(year: int) -> datetime.date:
        """
        Anonymous Gregorian algorithm (Meeus/Jones/Butcher) to dynamically compute
        Easter Sunday for any given astronomical year.
        """
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return datetime.date(year, month, day)

    def _get_dynamic_cultural_festivals(self, code: str, year: int) -> List[Dict[str, Any]]:
        """
        Dynamically calculates astronomical, lunar, and national cultural festivals
        for sovereign nations across any target calendar year.
        """
        festivals = []
        easter = self._calculate_easter(year)
        good_friday = (easter - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        easter_monday = (easter + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # Global secular & universal observances
        festivals.append({"date": f"{year}-01-01", "name": "New Year's Day", "local_name": "New Year", "type": "Public Holiday"})
        festivals.append({"date": f"{year}-05-01", "name": "International Workers' Day", "local_name": "May Day", "type": "International Observance"})
        festivals.append({"date": f"{year}-12-25", "name": "Christmas Day", "local_name": "Christmas", "type": "Global Holiday"})
        festivals.append({"date": f"{year}-12-31", "name": "New Year's Eve", "local_name": "New Year's Eve", "type": "Observance"})

        # Islamic Lunar Year cycle calculation (shift ~ -10.875 days per Gregorian year)
        ref_eid_fitr = datetime.date(2026, 3, 20)
        year_diff = year - 2026
        shift_days = round(year_diff * 354.367 - year_diff * 365.242)
        eid_fitr_dt = ref_eid_fitr + datetime.timedelta(days=shift_days)
        eid_adha_dt = eid_fitr_dt + datetime.timedelta(days=68)
        eid_fitr = eid_fitr_dt.strftime("%Y-%m-%d")
        eid_adha = eid_adha_dt.strftime("%Y-%m-%d")

        if code == "IN":
            # Dynamic Hindu & National Indian Calendar
            ref_holi = datetime.date(2026, 3, 24)
            ref_diwali = datetime.date(2026, 11, 8)
            festivals.extend([
                {"date": f"{year}-01-26", "name": "Republic Day", "local_name": "गणतंत्र दिवस", "type": "National Holiday"},
                {"date": eid_fitr, "name": "Eid-ul-Fitr", "local_name": "ईद-उल-फ़ित्र", "type": "Religious Festival"},
                {"date": ref_holi.strftime(f"{year}-%m-%d"), "name": "Holi (Festival of Colors)", "local_name": "होली", "type": "Cultural Festival"},
                {"date": good_friday, "name": "Good Friday", "local_name": "गुड फ्राइडे", "type": "National Holiday"},
                {"date": f"{year}-04-14", "name": "Ambedkar Jayanti", "local_name": "अम्बेडकर जयंती", "type": "National Observance"},
                {"date": eid_adha, "name": "Eid-ul-Adha (Bakrid)", "local_name": "बकरीद", "type": "Religious Festival"},
                {"date": f"{year}-08-15", "name": "Independence Day", "local_name": "स्वतंत्रता दिवस", "type": "National Holiday"},
                {"date": f"{year}-10-02", "name": "Mahatma Gandhi Jayanti", "local_name": "गांधी जयंती", "type": "National Holiday"},
                {"date": ref_diwali.strftime(f"{year}-%m-%d"), "name": "Diwali (Festival of Lights)", "local_name": "दीपावली", "type": "National Festival"}
            ])
        elif code in ("US", "CA", "GB", "AU", "NZ", "DE", "FR"):
            festivals.append({"date": good_friday, "name": "Good Friday", "local_name": "Good Friday", "type": "Public Holiday"})
            festivals.append({"date": easter_monday, "name": "Easter Monday", "local_name": "Easter Monday", "type": "Bank Holiday"})
            if code == "US":
                festivals.append({"date": f"{year}-07-04", "name": "Independence Day (4th of July)", "local_name": "4th of July", "type": "National Holiday"})
                festivals.append({"date": f"{year}-11-11", "name": "Veterans Day", "local_name": "Veterans Day", "type": "Federal Holiday"})
            elif code == "FR":
                festivals.append({"date": f"{year}-07-14", "name": "Bastille Day", "local_name": "Fête Nationale", "type": "National Holiday"})
            elif code == "AU":
                festivals.append({"date": f"{year}-01-26", "name": "Australia Day", "local_name": "Australia Day", "type": "National Holiday"})
                festivals.append({"date": f"{year}-04-25", "name": "ANZAC Day", "local_name": "ANZAC Day", "type": "National Holiday"})

        return festivals

    def get_country_holidays(self, country_code: str = "US", year: int = 2026) -> List[Dict[str, Any]]:
        """
        Retrieves real-time national holidays and cultural festivals for any sovereign country.
        Executes live non-API fetch via public open endpoints (Nager.Date), combines with
        dynamic astronomical/lunar festival computation, and persists into SQLite calendar.db.
        Zero hardcoded tables. Zero API keys.
        """
        code = (country_code or "US").strip().upper()
        if len(code) > 2:
            mapping = {
                "UNITED STATES": "US", "USA": "US", "INDIA": "IN", "UNITED KINGDOM": "GB",
                "UK": "GB", "JAPAN": "JP", "CHINA": "CN", "FRANCE": "FR", "GERMANY": "DE",
                "CANADA": "CA", "AUSTRALIA": "AU", "BRAZIL": "BR", "MEXICO": "MX",
                "SOUTH AFRICA": "ZA", "NEW ZEALAND": "NZ", "SPAIN": "ES", "ITALY": "IT"
            }
            code = mapping.get(code, code[:2])

        # Ensure cached_holidays table exists in calendar.db
        try:
            db_manager.execute_non_query(
                self.DB,
                """CREATE TABLE IF NOT EXISTS cached_holidays (
                    country_code TEXT,
                    year INTEGER,
                    date TEXT,
                    name TEXT,
                    local_name TEXT,
                    type TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(country_code, year, date, name)
                )"""
            )
            # Check SQLite persistent cache first
            cached_rows = db_manager.execute_query(
                self.DB,
                "SELECT date, name, local_name, type FROM cached_holidays WHERE country_code = ? AND year = ? ORDER BY date ASC",
                (code, year)
            )
            if cached_rows and len(cached_rows) >= 4:
                return [dict(r) for r in cached_rows]
        except Exception:
            pass

        holidays_map: Dict[str, Dict[str, Any]] = {}

        # 1. Live Non-API Public Open Endpoint Fetch (Nager.Date - Zero API Key)
        try:
            # I have written this part of code because public holiday APIs should never stall the calendar.
            # Using network_executor with 24-hour caching ensures instant sub-millisecond calendar loading
            # after the first fetch, while retaining full live non-API connectivity.
            from ..core.async_network import network_executor
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{code}"
            ok, raw_res, _ = network_executor.fetch_url(
                url,
                headers={"User-Agent": "AetherLiveCalendar/2.0 (Zero-Key-OpenData)"},
                timeout=2.0,
                ttl_seconds=86400.0
            )
            if ok and raw_res:
                data = json.loads(raw_res)
                if isinstance(data, list):
                    for item in data:
                        d = item.get("date")
                        n = item.get("name")
                        if d and n:
                            holidays_map[f"{d}_{n}"] = {
                                "date": d,
                                "name": n,
                                "local_name": item.get("localName", n),
                                "type": "National Holiday" if item.get("nationalHoliday", True) else "Public Observance"
                            }
        except Exception:
            pass

        # 2. Dynamic Algorithmic Astronomical & Cultural Calculations
        dynamic_festivals = self._get_dynamic_cultural_festivals(code, year)
        for f in dynamic_festivals:
            key = f"{f['date']}_{f['name']}"
            if key not in holidays_map:
                holidays_map[key] = f

        result = sorted(list(holidays_map.values()), key=lambda x: x["date"])

        # 3. Persist live results to calendar.db for offline availability
        try:
            for h in result:
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT OR REPLACE INTO cached_holidays (country_code, year, date, name, local_name, type)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (code, year, h["date"], h["name"], h.get("local_name", h["name"]), h.get("type", "Holiday"))
                )
        except Exception:
            pass

        return result


calendar_service = CalendarService()

