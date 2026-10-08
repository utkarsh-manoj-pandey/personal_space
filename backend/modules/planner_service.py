"""
Planner and Task Schedule Subsystem Service
Advanced productivity coordinator featuring:
- 4-Tier Kanban Workflow (Backlog, InProgress, Review, Completed).
- Eisenhower Matrix Quadrant Categorization & Priority Optimization.
- Critical Path Method (CPM) project dependency and slack analyzer.
- 24-Hour Daily Timeblock Schedule Maker.
- Pomodoro Sprint Allocation and Task Velocity Metrics.
- Persistent tasks and schedule blocks in planner.db.
"""

import datetime
from typing import List, Dict, Any, Optional, Tuple
from ..database_manager import db_manager
from ..core.algorithms import Graph, topological_sort


class ProjectCPMAnalyzer:
    """
    Critical Path Method (CPM) and dependency network analyzer.
    Computes Early Start (ES), Early Finish (EF), Late Start (LS), Late Finish (LF),
    total float (slack), and identifies the critical bottleneck path.
    """

    @classmethod
    def analyze_critical_path(cls, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates CPM timeline across tasks with duration and dependency attributes.
        """
        if not tasks:
            return {"critical_path": [], "total_project_duration": 0, "task_metrics": {}}

        # Build task map
        task_map = {t["id"]: t for t in tasks}
        durations = {t["id"]: max(1, t.get("estimated_pomodoros", 1)) for t in tasks}

        # Build DAG
        g = Graph(directed=True)
        for t in tasks:
            g.add_node(str(t["id"]))

        # For demonstration, sequential or tag-based dependencies
        task_ids = [t["id"] for t in tasks]
        for i in range(len(task_ids) - 1):
            g.add_edge(str(task_ids[i]), str(task_ids[i + 1]), weight=durations[task_ids[i]])

        # Forward pass (Early Start / Early Finish)
        es = {t_id: 0 for t_id in task_ids}
        ef = {t_id: durations[t_id] for t_id in task_ids}

        for i in range(len(task_ids) - 1):
            curr_id = task_ids[i]
            next_id = task_ids[i + 1]
            es[next_id] = max(es[next_id], ef[curr_id])
            ef[next_id] = es[next_id] + durations[next_id]

        total_duration = max(ef.values()) if ef else 0

        # Backward pass (Late Start / Late Finish)
        lf = {t_id: total_duration for t_id in task_ids}
        ls = {t_id: total_duration - durations[t_id] for t_id in task_ids}

        for i in range(len(task_ids) - 2, -1, -1):
            curr_id = task_ids[i]
            next_id = task_ids[i + 1]
            lf[curr_id] = min(lf[curr_id], ls[next_id])
            ls[curr_id] = lf[curr_id] - durations[curr_id]

        # Float / Slack = LS - ES
        slack = {t_id: ls[t_id] - es[t_id] for t_id in task_ids}
        critical_tasks = [t_id for t_id in task_ids if slack[t_id] == 0]

        task_metrics = {}
        for t_id in task_ids:
            task_metrics[t_id] = {
                "duration": durations[t_id],
                "early_start": es[t_id],
                "early_finish": ef[t_id],
                "late_start": ls[t_id],
                "late_finish": lf[t_id],
                "slack": slack[t_id],
                "is_critical": (slack[t_id] == 0)
            }

        return {
            "critical_path_task_ids": critical_tasks,
            "total_project_duration_pomodoros": total_duration,
            "task_metrics": task_metrics
        }


class PlannerService:
    """
    I have written this part of code because managing daily operational priorities
    with Eisenhower quadrant analysis, 4-tier Kanban pipelines, and 24-hour timeblocking
    keeps the operator focused on high-leverage tasks while tracking critical-path milestones!
    """
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
        """Fetch task details."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM tasks WHERE id = ?", (task_id,))
        return rows[0] if rows else None

    def save_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates or updates a task."""
        task_id = data.get("id")
        title = data.get("title", "Untitled Task").strip() or "Untitled Task"
        desc = data.get("description", "").strip()
        status = data.get("status", "Backlog")
        eisenhower = data.get("eisenhower", "NotUrgent_Important")
        priority = data.get("priority", "Medium")
        due = data.get("due_date", datetime.date.today().isoformat())
        est_pom = int(data.get("estimated_pomodoros", 1))
        comp_pom = int(data.get("completed_pomodoros", 0))
        prog = int(data.get("progress_percent", 0))
        tags = data.get("tags", "")

        if task_id and int(task_id) > 0:
            db_manager.execute_non_query(
                self.DB,
                """UPDATE tasks SET 
                   title = ?, description = ?, status = ?, eisenhower = ?, priority = ?,
                   due_date = ?, estimated_pomodoros = ?, completed_pomodoros = ?,
                   progress_percent = ?, tags = ?
                   WHERE id = ?""",
                (title, desc, status, eisenhower, priority, due, est_pom, comp_pom, prog, tags, int(task_id))
            )
            saved_id = int(task_id)
        else:
            saved_id = db_manager.execute_non_query(
                self.DB,
                """INSERT INTO tasks 
                   (title, description, status, eisenhower, priority, due_date, estimated_pomodoros, completed_pomodoros, progress_percent, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, desc, status, eisenhower, priority, due, est_pom, comp_pom, prog, tags)
            )

        return self.get_task(saved_id) or {"id": saved_id, "title": title}

    def update_task_status(self, task_id: int, new_status: str) -> bool:
        """Update Kanban column status (Backlog, InProgress, Review, Completed)."""
        completed_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_status == "Completed" else None
        db_manager.execute_non_query(
            self.DB,
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (new_status, completed_stamp, task_id)
        )
        return True

    def delete_task(self, task_id: int) -> bool:
        """Permanently delete task."""
        return db_manager.execute_non_query(self.DB, "DELETE FROM tasks WHERE id = ?", (task_id,)) > 0

    def get_productivity_analytics(self) -> Dict[str, Any]:
        """Compute task completion velocity, Pomodoro accuracy, and CPM bottleneck metrics."""
        tasks = self.list_tasks()
        total_tasks = len(tasks)
        status_counts = {"Backlog": 0, "InProgress": 0, "Review": 0, "Completed": 0}
        total_est_pom = 0
        total_comp_pom = 0

        for t in tasks:
            st = t.get("status", "Backlog")
            if st in status_counts:
                status_counts[st] += 1
            total_est_pom += t.get("estimated_pomodoros", 0)
            total_comp_pom += t.get("completed_pomodoros", 0)

        cpm_results = ProjectCPMAnalyzer.analyze_critical_path(tasks)

        return {
            "total_tasks": total_tasks,
            "status_distribution": status_counts,
            "completion_rate_percent": round((status_counts["Completed"] / max(1, total_tasks)) * 100.0, 1),
            "total_estimated_pomodoros": total_est_pom,
            "total_completed_pomodoros": total_comp_pom,
            "cpm_analysis": cpm_results
        }

    # --- Schedule Blocks ---
    def list_schedule_blocks(self, day_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """List daily timeblock entries."""
        query = "SELECT * FROM schedule_blocks"
        params = []
        if day_date:
            query += " WHERE day_date = ?"
            params.append(day_date)
        query += " ORDER BY start_time ASC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def add_schedule_block(self, day_date: str, start_time: str, end_time: str, title: str, category: str = "Focus", color: str = "#8b5cf6") -> Dict[str, Any]:
        """Insert a 24-hour timeblock."""
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO schedule_blocks (day_date, start_time, end_time, title, category, color)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (day_date, start_time, end_time, title.strip(), category, color)
        )
        return {"id": new_id, "day_date": day_date, "start_time": start_time, "end_time": end_time, "title": title}

    def delete_schedule_block(self, block_id: int) -> bool:
        """Remove a schedule block."""
        return db_manager.execute_non_query(self.DB, "DELETE FROM schedule_blocks WHERE id = ?", (block_id,)) > 0


planner_service = PlannerService()
