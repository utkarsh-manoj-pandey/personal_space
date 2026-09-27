"""
Planner and Task Schedule Subsystem Service
Advanced productivity coordinator featuring:
- 4-Tier Kanban Workflow (Backlog, InProgress, Review, Completed)
- Eisenhower Matrix Quadrant Categorization (Urgent vs Important)
- 24-Hour Daily Timeblock Schedule Maker
- Pomodoro Sprint Allocation and Task Progress Metrics
"""

import datetime
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager


class PlannerService:
    DB = "planner.db"

    def __init__(self):
        self._seed_default_tasks_and_schedule()

    def _seed_default_tasks_and_schedule(self):
        """Seed initial productivity tasks and daily schedule blocks if empty."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM tasks")
        if count and count[0]["count"] == 0:
            today_str = datetime.date.today().isoformat()
            starter_tasks = [
                (
                    "Perform Full Hardened Security Audit",
                    "Verify local SQLite encryption wrappers, zero-telemetry policy, and network sandbox isolation.",
                    "InProgress",
                    "Urgent_Important",
                    "Critical",
                    today_str,
                    4, 2, 50,
                    "Security,Audit"
                ),
                (
                    "Calibrate Minimax Chess Alpha-Beta Engine",
                    "Profile move search depth down to ply 4 with positional square tables.",
                    "InProgress",
                    "NotUrgent_Important",
                    "High",
                    today_str,
                    3, 1, 33,
                    "Algorithms,AI-Free"
                ),
                (
                    "Deploy Subsea Cable Fiber Telemetry Model",
                    "Map primary intercontinental fiber optics corridors in the World Monitor.",
                    "Review",
                    "NotUrgent_Important",
                    "Medium",
                    today_str,
                    2, 2, 100,
                    "WorldMonitor,Telemetry"
                ),
                (
                    "Archive Weekly Offline Backups",
                    "Execute atomic SQLite VACUUM and snapshot all 17 isolated subsystem databases.",
                    "Backlog",
                    "Urgent_Important",
                    "High",
                    today_str,
                    2, 0, 0,
                    "Maintenance,Ops"
                )
            ]

            for t in starter_tasks:
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT INTO tasks 
                       (title, description, status, eisenhower, priority, due_date, estimated_pomodoros, completed_pomodoros, progress_percent, tags)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    t
                )

        # Seed daily schedule blocks
        s_count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM schedule_blocks")
        if s_count and s_count[0]["count"] == 0:
            today_str = datetime.date.today().isoformat()
            blocks = [
                (today_str, "08:00", "09:00", "System Telemetry & Health Audit", "Operations", "#00f0ff"),
                (today_str, "09:30", "12:00", "Deep Coding: Offline Engine Refinements", "Focus", "#8b5cf6"),
                (today_str, "13:30", "15:00", "Situational World Monitor Review", "Intelligence", "#f59e0b"),
                (today_str, "15:30", "17:00", "Algorithmic Chess Engine Optimization", "Focus", "#10b981"),
                (today_str, "17:30", "18:30", "Evening Physical Conditioning", "Health", "#ec4899")
            ]
            for b in blocks:
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT INTO schedule_blocks (day_date, start_time, end_time, title, category, color)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    b
                )

    def list_tasks(self, status: Optional[str] = None, eisenhower: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks with optional status or quadrant filters."""
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status and status != "All":
            query += " AND status = ?"
            params.append(status)
        if eisenhower and eisenhower != "All":
            query += " AND eisenhower = ?"
            params.append(eisenhower)
        query += " ORDER BY id DESC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve task by ID."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM tasks WHERE id = ?", (task_id,))
        return rows[0] if rows else None

    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO tasks 
               (title, description, status, eisenhower, priority, due_date, estimated_pomodoros, completed_pomodoros, progress_percent, tags)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get("title", "New Task").strip(),
                data.get("description", "").strip(),
                data.get("status", "Backlog"),
                data.get("eisenhower", "NotUrgent_Important"),
                data.get("priority", "Medium"),
                data.get("due_date", datetime.date.today().isoformat()),
                int(data.get("estimated_pomodoros", 1)),
                int(data.get("completed_pomodoros", 0)),
                int(data.get("progress_percent", 0)),
                data.get("tags", "")
            )
        )
        return self.get_task(new_id) or {}

    def update_task_status(self, task_id: int, status: str) -> Optional[Dict[str, Any]]:
        """Move a task to a different Kanban column."""
        completed_at = datetime.datetime.now().isoformat() if status == "Completed" else None
        db_manager.execute_non_query(
            self.DB,
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, completed_at, task_id)
        )
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        """Permanently delete a task."""
        count = db_manager.execute_non_query(self.DB, "DELETE FROM tasks WHERE id = ?", (task_id,))
        return count > 0

    def list_schedule_blocks(self, day_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """List schedule timeblocks for a specific calendar day."""
        target_date = day_date or datetime.date.today().isoformat()
        return db_manager.execute_query(
            self.DB,
            "SELECT * FROM schedule_blocks WHERE day_date = ? ORDER BY start_time ASC",
            (target_date,)
        )

    def add_schedule_block(self, day_date: str, start_time: str, end_time: str, title: str, category: str = "Focus", color: str = "#8b5cf6") -> Dict[str, Any]:
        """Create a new time block on the daily timeline."""
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO schedule_blocks (day_date, start_time, end_time, title, category, color)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (day_date, start_time, end_time, title.strip(), category, color)
        )
        rows = db_manager.execute_query(self.DB, "SELECT * FROM schedule_blocks WHERE id = ?", (new_id,))
        return rows[0] if rows else {}

    def delete_schedule_block(self, block_id: int) -> bool:
        """Delete a schedule time block."""
        count = db_manager.execute_non_query(self.DB, "DELETE FROM schedule_blocks WHERE id = ?", (block_id,))
        return count > 0


planner_service = PlannerService()
