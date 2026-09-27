"""
Video Subsystem Service
Cinema-grade video management engine supporting MP4, WebM, MKV, OGG.
Maintains frame-accurate timestamp bookmarking, playback position preservation,
and local disk directory indexing.
"""

import os
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager


class VideoService:
    DB = "video.db"

    def __init__(self):
        self._seed_default_videos()

    def _seed_default_videos(self):
        """Seed high-definition cinematic open-source tech demos for immediate test playback."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM videos")
        if count and count[0]["count"] == 0:
            default_videos = [
                (
                    "Tears of Steel (Sci-Fi Cyberpunk VFX)",
                    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
                    734.0,
                    0.0,
                    "1080p Ultra HD",
                    1.0
                ),
                (
                    "Big Buck Bunny (Blender Animation Studio)",
                    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                    596.0,
                    0.0,
                    "1080p Full HD",
                    1.0
                ),
                (
                    "Cosmos Laundromat (First Cycle Open Movie)",
                    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
                    120.0,
                    0.0,
                    "720p HD",
                    1.0
                )
            ]
            for v in default_videos:
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT OR IGNORE INTO videos (title, file_path, duration, last_position, resolution, playback_speed)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    v
                )

    def list_videos(self) -> List[Dict[str, Any]]:
        """List all cataloged videos ordered by last played."""
        return db_manager.execute_query(self.DB, "SELECT * FROM videos ORDER BY last_played DESC")

    def get_video(self, video_id: int) -> Optional[Dict[str, Any]]:
        """Fetch video record by ID."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM videos WHERE id = ?", (video_id,))
        return rows[0] if rows else None

    def update_position(self, video_id: int, current_time: float) -> bool:
        """Save playback resume position."""
        db_manager.execute_non_query(
            self.DB,
            "UPDATE videos SET last_position = ?, last_played = CURRENT_TIMESTAMP WHERE id = ?",
            (current_time, video_id)
        )
        return True

    def add_bookmark(self, video_id: int, timestamp: float, label: str) -> Dict[str, Any]:
        """Save a frame timestamp bookmark."""
        new_id = db_manager.execute_non_query(
            self.DB,
            "INSERT INTO video_bookmarks (video_id, timestamp, label) VALUES (?, ?, ?)",
            (video_id, timestamp, label.strip() or f"Marker @ {int(timestamp)}s")
        )
        rows = db_manager.execute_query(self.DB, "SELECT * FROM video_bookmarks WHERE id = ?", (new_id,))
        return rows[0] if rows else {}

    def get_bookmarks(self, video_id: int) -> List[Dict[str, Any]]:
        """Retrieve all bookmarks for a video."""
        return db_manager.execute_query(
            self.DB,
            "SELECT * FROM video_bookmarks WHERE video_id = ? ORDER BY timestamp ASC",
            (video_id,)
        )

    def register_local_video(self, file_path: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Register a new local video file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")
        clean_title = title or os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO videos (title, file_path, duration, last_position, resolution)
               VALUES (?, ?, 0.0, 0.0, 'Local Source')
               ON CONFLICT(file_path) DO UPDATE SET last_played = CURRENT_TIMESTAMP""",
            (clean_title, file_path)
        )
        return self.get_video(new_id) or {}


video_service = VideoService()
