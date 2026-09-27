"""
Notepad Subsystem Service
High-throughput, offline notes engine featuring markdown parsing, auto-save tracking,
word/character/reading-time telemetry, tag hierarchies, and multi-format exports.
"""

import math
import re
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager


class NotepadService:
    DB = "notepad.db"

    def __init__(self):
        self._seed_default_notes()

    def _seed_default_notes(self):
        """Seed initial high-value workstation documentation and operational guides."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM notes")
        if count and count[0]["count"] == 0:
            notes = [
                (
                    "Workstation Operational Directives",
                    """# NEXUS WORKSTATION DIRECTIVES

## Core Architectural Pillars
1. **Zero External AI Telemetry**: All decision engines, solvers, and parsers execute strictly through deterministic local algorithms. No copilot leaks, no cloud dependency.
2. **Dedicated Subsystem Databases**: Every single module possesses its own isolated SQLite database in WAL mode with enforced foreign keys.
3. **High Security Posture**: Data never leaves the host machine unless explicitly requested by network streaming services (Radio/Weather/Maps).

## System Hotkeys & Shortcuts
- `Ctrl + K`: Universal Command Palette
- `Ctrl + S`: Instant Document & Schedule Sync
- `F11`: Fullscreen Immersion Mode

*System Status: Optimal. Ready for advanced operations.*""",
                    "Core,Architecture,Security",
                    1
                ),
                (
                    "Algorithmic Game Engines & Minimax Theory",
                    """# Chess & Decision Tree Heuristics

The Chess Engine utilizes an iterative deepening **Minimax** tree with **Alpha-Beta Pruning**:

$$\\alpha = \\max(\\alpha, \\text{score})$$
$$\\beta = \\min(\\beta, \\text{score})$$

### Positional Evaluation Weights
- **Pawns**: 100 centipawns + center advancement bonus
- **Knights/Bishops**: 320/330 centipawns + mobility bonus
- **Rooks**: 500 centipawns + open file incentive
- **Queens**: 900 centipawns + late game mobilization
- **King**: 20000 centipawns + safety shelter in opening/middle game

The Connect4 engine similarly models 7-column gravity physics with a 42-cell bitboard evaluator.""",
                    "Engineering,Algorithms,Chess",
                    0
                ),
                (
                    "Cryptographic Keychain & Local Vault Notes",
                    """# Local Vault Security Checklist

- [x] SQLite databases configured with WAL mode (`PRAGMA journal_mode=WAL`)
- [x] Prepared statements utilized exclusively to eliminate SQL injection vectors
- [x] Input sanitation on mathematical evaluator using Abstract Syntax Trees (`ast.parse`)
- [x] Browser sandbox user-agent spoofing enabled to neutralize canvas fingerprinting
- [x] Network requests restricted to open, keyless endpoints (USGS, Open-Meteo, OSRM)

*All integrity checks passed.*""",
                    "Security,Checklist",
                    0
                )
            ]

            for title, content, tags, is_pinned in notes:
                wc = len(re.findall(r'\w+', content))
                cc = len(content)
                rt = round(wc / 200.0, 1)
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT INTO notes (title, content, tags, is_pinned, word_count, char_count, reading_time_mins)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (title, content, tags, is_pinned, wc, cc, rt)
                )

    def list_notes(self, search: str = "", tag: str = "") -> List[Dict[str, Any]]:
        """List all notes sorted by pinned status and last updated timestamp."""
        query = "SELECT * FROM notes WHERE is_archived = 0"
        params = []

        if search:
            query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")

        query += " ORDER BY is_pinned DESC, updated_at DESC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific note by ID."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM notes WHERE id = ?", (note_id,))
        return rows[0] if rows else None

    def save_note(self, note_id: Optional[int], title: str, content: str, tags: str = "", is_pinned: int = 0) -> Dict[str, Any]:
        """Create or update a note with automatic word count and reading time calculation."""
        title = title.strip() or "Untitled Document"
        words = len(re.findall(r'\w+', content))
        chars = len(content)
        reading_time = round(words / 200.0, 1)

        if note_id:
            db_manager.execute_non_query(
                self.DB,
                """UPDATE notes 
                   SET title = ?, content = ?, tags = ?, is_pinned = ?, 
                       word_count = ?, char_count = ?, reading_time_mins = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (title, content, tags, is_pinned, words, chars, reading_time, note_id)
            )
            return self.get_note(note_id) or {}
        else:
            new_id = db_manager.execute_non_query(
                self.DB,
                """INSERT INTO notes (title, content, tags, is_pinned, word_count, char_count, reading_time_mins)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, content, tags, is_pinned, words, chars, reading_time)
            )
            return self.get_note(new_id) or {}

    def delete_note(self, note_id: int) -> bool:
        """Permanently delete a note."""
        count = db_manager.execute_non_query(self.DB, "DELETE FROM notes WHERE id = ?", (note_id,))
        return count > 0

    def toggle_pin(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Toggle pinned status for a note."""
        note = self.get_note(note_id)
        if not note:
            return None
        new_val = 0 if note["is_pinned"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE notes SET is_pinned = ? WHERE id = ?", (new_val, note_id))
        return self.get_note(note_id)


notepad_service = NotepadService()
