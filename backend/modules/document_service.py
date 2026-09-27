"""
Document Viewer Subsystem Service
Multi-format document reader engine supporting PDF, Markdown, Plain Text, CSV, JSON, and Source Code.
Integrates pypdf for local parsing, full-text extraction, page enumeration, and marginal annotations.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager

logger = logging.getLogger("DocumentService")


class DocumentService:
    DB = "documents.db"

    def __init__(self):
        self.docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "documents"))
        os.makedirs(self.docs_dir, exist_ok=True)
        self._seed_sample_documents()

    def _seed_sample_documents(self):
        """Seed sample high-tech documentation for out-of-the-box preview."""
        sample_path = os.path.join(self.docs_dir, "SYSTEM_SPECIFICATIONS.md")
        if not os.path.exists(sample_path):
            sample_content = """# NEXUS SYSTEM ARCHITECTURE & PROTOCOLS

## 1. Executive Overview
The Nexus Personal Workstation represents an elite, offline-first personal operating environment. 
Engineered with absolute privacy, zero cloud telemetry, and strict deterministic behavior.

### 2. Multi-Database Topology
The persistence layer utilizes 17 completely isolated SQLite databases located in `./data`:
- `calendar.db`: Temporal scheduling and recurrence engine.
- `browser.db`: Anti-fingerprint profiles, encrypted bookmarks, and proxy routing.
- `notepad.db`: Markdown repository with real-time reading metrics.
- `music.db`: Procedural ambient soundscapes and audio metadata.
- `video.db`: Frame-accurate playback coordinates and chapter markers.
- `documents.db`: Multi-format document parser and marginalia notes.
- `radio.db`: High-definition international radio streams.
- `weather.db`: Keyless Open-Meteo telemetry and forecast models.
- `news.db`: Global RSS/Atom intelligence aggregator.
- `calculator.db`: AST mathematical expressions and multi-base registers.
- `images.db`: Image catalogs, EXIF telemetry, and color matrices.
- `clocks.db`: World clock timezones, countdown chronometers, and Pomodoro timers.
- `maps.db`: OpenStreetMap vector tiles and OSRM turn-by-turn routing.
- `world_monitor.db`: USGS real-time seismic feeds, ISS orbital tracks, and GDACS alerts.
- `planner.db`: 4-stage Kanban matrices and 24-hour timeblocking schedules.
- `contacts.db`: Address book, vCard 3.0 import/export, and interaction logs.
- `games.db`: Chess minimax engine, Connect 4, and retro arcade leaderboards.

### 3. Security Guarantee
No data is ever dispatched to external machine learning vendors or cloud copilots. 
Your machine remains entirely yours.
"""
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write(sample_content)

            self.open_document(sample_path)

    def list_recent(self) -> List[Dict[str, Any]]:
        """Fetch list of recently inspected documents."""
        return db_manager.execute_query(self.DB, "SELECT * FROM recent_documents ORDER BY opened_at DESC LIMIT 20")

    def open_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parses and reads document contents.
        Handles PDF, Markdown, TXT, JSON, CSV, and Source Code formats cleanly.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        size_bytes = os.path.getsize(file_path)
        content = ""
        total_pages = 1
        pages_content = []

        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                total_pages = len(reader.pages)
                for idx, page in enumerate(reader.pages):
                    extracted = page.extract_text() or f"[Page {idx + 1} - No extractable text]"
                    pages_content.append({"page": idx + 1, "text": extracted})
                content = pages_content[0]["text"] if pages_content else ""
            except Exception as e:
                logger.error(f"Error parsing PDF {file_path}: {e}")
                content = f"Error reading PDF content: {str(e)}"
                pages_content = [{"page": 1, "text": content}]
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                pages_content = [{"page": 1, "text": content}]
            except Exception as e:
                content = f"Error reading file: {str(e)}"
                pages_content = [{"page": 1, "text": content}]

        # Register in database
        doc_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO recent_documents (file_name, file_path, file_type, file_size, total_pages)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(file_path) DO UPDATE SET opened_at = CURRENT_TIMESTAMP, total_pages = excluded.total_pages""",
            (file_name, file_path, ext or "txt", size_bytes, total_pages)
        )

        rows = db_manager.execute_query(self.DB, "SELECT * FROM recent_documents WHERE file_path = ?", (file_path,))
        doc_info = rows[0] if rows else {}

        return {
            "id": doc_info.get("id"),
            "file_name": file_name,
            "file_path": file_path,
            "file_type": ext,
            "file_size": size_bytes,
            "total_pages": total_pages,
            "pages": pages_content,
            "content": content
        }

    def add_annotation(self, doc_id: int, page_number: int, note_text: str) -> Dict[str, Any]:
        """Save a marginal annotation to a document page."""
        new_id = db_manager.execute_non_query(
            self.DB,
            "INSERT INTO annotations (document_id, page_number, note_text) VALUES (?, ?, ?)",
            (doc_id, page_number, note_text.strip())
        )
        rows = db_manager.execute_query(self.DB, "SELECT * FROM annotations WHERE id = ?", (new_id,))
        return rows[0] if rows else {}

    def get_annotations(self, doc_id: int) -> List[Dict[str, Any]]:
        """Retrieve all annotations for a document."""
        return db_manager.execute_query(
            self.DB,
            "SELECT * FROM annotations WHERE document_id = ? ORDER BY page_number ASC, created_at ASC",
            (doc_id,)
        )


document_service = DocumentService()
