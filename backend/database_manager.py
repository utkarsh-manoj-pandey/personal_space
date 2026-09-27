"""
Database Manager - Multi-SQLite Isolated Persistence Architecture
Production-grade SQLite manager maintaining 17 isolated local databases for the workstation.
Zero external server dependencies, full ACID compliance, WAL-enabled for concurrent read/write performance.
"""

import os
import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator, Any, Dict, List, Optional

# Configure module logging with clear, professional telemetry formatting
logger = logging.getLogger("DatabaseManager")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class DatabaseManager:
    """
    Central database coordinator.
    Ensures absolute data isolation by maintaining dedicated, purpose-built SQLite databases
    for each subsystem in the local workstation storage directory.
    """

    DATABASE_NAMES = [
        "calendar.db",
        "browser.db",
        "notepad.db",
        "music.db",
        "video.db",
        "documents.db",
        "radio.db",
        "weather.db",
        "news.db",
        "calculator.db",
        "images.db",
        "clocks.db",
        "maps.db",
        "world_monitor.db",
        "planner.db",
        "contacts.db",
        "games.db"
    ]

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the database coordinator.
        
        Args:
            base_dir: Optional path to data storage directory. Defaults to ./data relative to workspace.
        """
        if base_dir:
            self.storage_dir = os.path.abspath(base_dir)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.storage_dir = os.path.abspath(os.path.join(current_dir, "..", "data"))
        
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info(f"DatabaseManager initialized. Dedicated storage path: {self.storage_dir}")
        self._initialize_all_schemas()

    def get_db_path(self, db_name: str) -> str:
        """Returns the absolute file path for a specific subsystem database."""
        if not db_name.endswith(".db"):
            db_name = f"{db_name}.db"
        return os.path.join(self.storage_dir, db_name)

    @contextmanager
    def get_connection(self, db_name: str) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager providing safe SQLite connections with:
        - WAL (Write-Ahead Logging) mode enabled for high-speed concurrent reads
        - Row factory set to sqlite3.Row for dictionary-like column access
        - Automatic commit on clean exit and automatic rollback on exception
        """
        db_path = self.get_db_path(db_name)
        conn = sqlite3.connect(db_path, timeout=15.0)
        conn.row_factory = sqlite3.Row
        
        # Optimize SQLite performance & integrity
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()

        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction failed for {db_name}: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    def execute_query(self, db_name: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns a list of dictionaries."""
        with self.get_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def execute_non_query(self, db_name: str, query: str, params: tuple = ()) -> int:
        """Executes an INSERT, UPDATE, or DELETE query and returns the lastrowid or rowcount."""
        with self.get_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def execute_script(self, db_name: str, script: str) -> None:
        """Executes a multi-statement DDL/DML script."""
        with self.get_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.executescript(script)

    def _initialize_all_schemas(self) -> None:
        """Runs the DDL schema initialization for each of the 17 isolated databases."""
        schemas = {
            # 1. Personal Calendar Database
            "calendar.db": """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    location TEXT,
                    category TEXT DEFAULT 'General',
                    color TEXT DEFAULT '#3b82f6',
                    recurrence TEXT DEFAULT 'none',
                    priority TEXT DEFAULT 'Medium',
                    remind_minutes_before INTEGER DEFAULT 15,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_calendar_time ON events(start_time, end_time);
            """,

            # 2. Privacy Focused Web Browser Database
            "browser.db": """
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    category TEXT DEFAULT 'General',
                    icon_svg TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS privacy_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS search_engines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    search_url TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS blocked_domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL UNIQUE,
                    category TEXT DEFAULT 'Tracker'
                );
            """,

            # 3. Inbuilt Notepad Database
            "notepad.db": """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    is_pinned INTEGER DEFAULT 0,
                    is_archived INTEGER DEFAULT 0,
                    word_count INTEGER DEFAULT 0,
                    char_count INTEGER DEFAULT 0,
                    reading_time_mins REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(updated_at DESC);
            """,

            # 4. Inbuilt Music Player Database
            "music.db": """
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT DEFAULT 'Unknown Artist',
                    album TEXT DEFAULT 'Unknown Album',
                    duration INTEGER DEFAULT 0,
                    file_path TEXT NOT NULL UNIQUE,
                    genre TEXT DEFAULT 'General',
                    bitrate INTEGER DEFAULT 320,
                    play_count INTEGER DEFAULT 0,
                    is_favorite INTEGER DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS playlist_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER,
                    track_id INTEGER,
                    position INTEGER,
                    FOREIGN KEY(playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                    FOREIGN KEY(track_id) REFERENCES tracks(id) ON DELETE CASCADE
                );
            """,

            # 5. Inbuilt Video Player Database
            "video.db": """
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    duration REAL DEFAULT 0.0,
                    last_position REAL DEFAULT 0.0,
                    resolution TEXT DEFAULT 'Unknown',
                    playback_speed REAL DEFAULT 1.0,
                    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS video_bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER,
                    timestamp REAL NOT NULL,
                    label TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
                );
            """,

            # 6. Inbuilt Document Viewer Database
            "documents.db": """
                CREATE TABLE IF NOT EXISTS recent_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    file_type TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    last_page INTEGER DEFAULT 1,
                    total_pages INTEGER DEFAULT 1,
                    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS annotations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    page_number INTEGER,
                    note_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(document_id) REFERENCES recent_documents(id) ON DELETE CASCADE
                );
            """,

            # 7. Inbuilt Internet Radio Player Database
            "radio.db": """
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    stream_url TEXT NOT NULL UNIQUE,
                    genre TEXT DEFAULT 'Eclectic',
                    country TEXT DEFAULT 'Global',
                    bitrate TEXT DEFAULT '128k',
                    codec TEXT DEFAULT 'MP3',
                    is_favorite INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0
                );
            """,

            # 8. Inbuilt Weather Updates Database
            "weather.db": """
                CREATE TABLE IF NOT EXISTS weather_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    country TEXT,
                    latitude REAL,
                    longitude REAL,
                    temp REAL,
                    feels_like REAL,
                    humidity REAL,
                    wind_speed REAL,
                    condition_text TEXT,
                    condition_code INTEGER,
                    uv_index REAL,
                    forecast_json TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS saved_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT NOT NULL UNIQUE,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    is_default INTEGER DEFAULT 0
                );
            """,

            # 9. Inbuilt News Viewer Database
            "news.db": """
                CREATE TABLE IF NOT EXISTS news_feeds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    feed_url TEXT NOT NULL UNIQUE,
                    category TEXT DEFAULT 'Geopolitics',
                    is_active INTEGER DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_id INTEGER,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL UNIQUE,
                    summary TEXT,
                    published_date TEXT,
                    is_read INTEGER DEFAULT 0,
                    is_bookmarked INTEGER DEFAULT 0,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(feed_id) REFERENCES news_feeds(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_date DESC);
            """,

            # 10. Inbuilt Calculator Database
            "calculator.db": """
                CREATE TABLE IF NOT EXISTS calc_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expression TEXT NOT NULL,
                    result TEXT NOT NULL,
                    mode TEXT DEFAULT 'Scientific',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS stored_variables (
                    name TEXT PRIMARY KEY,
                    value REAL NOT NULL,
                    description TEXT
                );
            """,

            # 11. Inbuilt Image Viewer Database
            "images.db": """
                CREATE TABLE IF NOT EXISTS image_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    file_size INTEGER DEFAULT 0,
                    width INTEGER DEFAULT 0,
                    height INTEGER DEFAULT 0,
                    color_space TEXT DEFAULT 'RGB',
                    format TEXT DEFAULT 'JPEG',
                    tags TEXT DEFAULT '',
                    is_favorite INTEGER DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,

            # 12. Inbuilt Clock and Timers Database
            "clocks.db": """
                CREATE TABLE IF NOT EXISTS world_cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT NOT NULL UNIQUE,
                    timezone TEXT NOT NULL,
                    country TEXT NOT NULL,
                    display_order INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS stopwatch_laps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    lap_number INTEGER NOT NULL,
                    lap_time_ms INTEGER NOT NULL,
                    total_time_ms INTEGER NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS preset_timers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    color TEXT DEFAULT '#06b6d4'
                );
            """,

            # 13. Inbuilt Maps and Navigation Database
            "maps.db": """
                CREATE TABLE IF NOT EXISTS saved_waypoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    category TEXT DEFAULT 'Favorite',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS saved_routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    start_coords TEXT NOT NULL,
                    end_coords TEXT NOT NULL,
                    distance_km REAL DEFAULT 0.0,
                    duration_mins REAL DEFAULT 0.0,
                    route_geojson TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,

            # 14. Inbuilt World Monitor Database
            "world_monitor.db": """
                CREATE TABLE IF NOT EXISTS seismic_events (
                    event_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    magnitude REAL NOT NULL,
                    place TEXT NOT NULL,
                    depth_km REAL DEFAULT 0.0,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    event_time TEXT NOT NULL,
                    alert_level TEXT DEFAULT 'green',
                    tsunami_flag INTEGER DEFAULT 0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS orbital_telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    satellite_name TEXT NOT NULL,
                    norad_id INTEGER NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    altitude_km REAL NOT NULL,
                    velocity_kmh REAL NOT NULL,
                    timestamp TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS global_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    latitude REAL,
                    longitude REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,

            # 15. Inbuilt Day/Task/Schedule Planner Database
            "planner.db": """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'Backlog', -- Backlog, InProgress, Review, Completed
                    eisenhower TEXT DEFAULT 'NotUrgent_Important', -- Urgent_Important, NotUrgent_Important, Urgent_NotImportant, Neither
                    priority TEXT DEFAULT 'Medium', -- Low, Medium, High, Critical
                    due_date TEXT,
                    estimated_pomodoros INTEGER DEFAULT 1,
                    completed_pomodoros INTEGER DEFAULT 0,
                    progress_percent INTEGER DEFAULT 0,
                    tags TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS schedule_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day_date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT DEFAULT 'Focus',
                    color TEXT DEFAULT '#8b5cf6',
                    task_id INTEGER,
                    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE SET NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_schedule_day ON schedule_blocks(day_date);
            """,

            # 16. Inbuilt Contact Manager Database
            "contacts.db": """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT DEFAULT '',
                    organization TEXT DEFAULT '',
                    job_title TEXT DEFAULT '',
                    phone_primary TEXT DEFAULT '',
                    phone_secondary TEXT DEFAULT '',
                    email_primary TEXT DEFAULT '',
                    email_secondary TEXT DEFAULT '',
                    address TEXT DEFAULT '',
                    website TEXT DEFAULT '',
                    relationship_category TEXT DEFAULT 'Personal', -- Personal, Family, Professional, Emergency, VIP
                    notes TEXT DEFAULT '',
                    birthday TEXT,
                    is_favorite INTEGER DEFAULT 0,
                    avatar_svg TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS contact_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    log_type TEXT NOT NULL, -- Call, Meeting, Note, Email
                    summary TEXT NOT NULL,
                    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(last_name, first_name);
            """,

            # 17. Inbuilt Games Database
            "games.db": """
                CREATE TABLE IF NOT EXISTS match_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_title TEXT NOT NULL, -- Chess, SpaceDefender, Connect4, Cyber2048, Minesweeper
                    game_mode TEXT NOT NULL, -- SinglePlayer, ComputerVsPlayer, TwoPlayerLocal
                    result TEXT NOT NULL, -- Win, Loss, Draw
                    player_score INTEGER DEFAULT 0,
                    opponent_score INTEGER DEFAULT 0,
                    difficulty TEXT DEFAULT 'Master',
                    duration_seconds INTEGER DEFAULT 0,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_title TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    level INTEGER DEFAULT 1,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_high_scores ON high_scores(game_title, score DESC);
            """
        }

        for db_name, ddl in schemas.items():
            try:
                self.execute_script(db_name, ddl)
            except Exception as e:
                logger.error(f"Failed to initialize schema for {db_name}: {e}", exc_info=True)

        logger.info("All 17 isolated subsystem databases initialized successfully with production indexes.")


# Singleton instance accessible across backend services
db_manager = DatabaseManager()
