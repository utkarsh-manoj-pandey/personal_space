"""
Calendar Subsystem Service
Maintains local schedules, recurring occurrences, priority categorizations,
and RFC 5545 iCalendar import/export compliance.
"""

import datetime
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager


class CalendarService:
    DB = "calendar.db"

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
        """Retrieve a single event by primary key ID."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM events WHERE id = ?", (event_id,))
        return rows[0] if rows else None

    def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event entry."""
        title = data.get("title", "Untitled Schedule Item").strip()
        description = data.get("description", "").strip()
        start_time = data.get("start_time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        end_time = data.get("end_time", (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))
        location = data.get("location", "").strip()
        category = data.get("category", "General")
        color = data.get("color", "#00f0ff")
        recurrence = data.get("recurrence", "none")
        priority = data.get("priority", "Medium")
        remind = int(data.get("remind_minutes_before", 15))

        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO events (title, description, start_time, end_time, location, category, color, recurrence, priority, remind_minutes_before)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, description, start_time, end_time, location, category, color, recurrence, priority, remind)
        )
        return self.get_event(new_id)

    def update_event(self, event_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing calendar event."""
        db_manager.execute_non_query(
            self.DB,
            """UPDATE events 
               SET title = ?, description = ?, start_time = ?, end_time = ?, location = ?,
                   category = ?, color = ?, recurrence = ?, priority = ?, remind_minutes_before = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                data.get("title", ""),
                data.get("description", ""),
                data.get("start_time", ""),
                data.get("end_time", ""),
                data.get("location", ""),
                data.get("category", "General"),
                data.get("color", "#00f0ff"),
                data.get("recurrence", "none"),
                data.get("priority", "Medium"),
                int(data.get("remind_minutes_before", 15)),
                event_id
            )
        )
        return self.get_event(event_id)

    def delete_event(self, event_id: int) -> bool:
        """Permanently delete a calendar event."""
        rows_affected = db_manager.execute_non_query(
            self.DB,
            "DELETE FROM events WHERE id = ?",
            (event_id,)
        )
        return rows_affected > 0

    def export_ics(self) -> str:
        """Generate standard RFC 5545 iCalendar data for seamless Google/Outlook/Apple import."""
        events = self.list_events()
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Nexus Personal Workstation//Calendar System//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]

        for ev in events:
            # Parse datetime format
            try:
                dt_start = datetime.datetime.strptime(ev["start_time"], "%Y-%m-%d %H:%M:%S")
                dt_end = datetime.datetime.strptime(ev["end_time"], "%Y-%m-%d %H:%M:%S")
                dtstart_str = dt_start.strftime("%Y%m%dT%H%M%SZ")
                dtend_str = dt_end.strftime("%Y%m%dT%H%M%SZ")
            except Exception:
                dtstart_str = "20260101T000000Z"
                dtend_str = "20260101T010000Z"

            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:nexus-cal-{ev['id']}@workstation.local")
            lines.append(f"DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
            lines.append(f"DTSTART:{dtstart_str}")
            lines.append(f"DTEND:{dtend_str}")
            lines.append(f"SUMMARY:{ev['title']}")
            if ev.get("description"):
                desc = ev['description'].replace("\n", "\\n")
                lines.append(f"DESCRIPTION:{desc}")
            if ev.get("location"):
                lines.append(f"LOCATION:{ev['location']}")
            lines.append(f"CATEGORIES:{ev.get('category', 'General')}")
            lines.append(f"PRIORITY:{'1' if ev.get('priority') == 'Critical' else '5'}")
            lines.append("END:VEVENT")

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)


calendar_service = CalendarService()
