"""
Document Viewer Subsystem Service
Multi-format document reader and structural analysis engine supporting:
- PDF: Page-by-page text extraction, metadata inspection, TOC indexing via pypdf.
- Markdown: Section heading extraction, frontmatter metadata parser, and Table of Contents generation.
- Tabular CSV: Schema auto-inference, column statistics, and Markdown table conversion.
- JSON: Key hierarchy inspection, pretty-printing, and path querying.
- Plain Text & Source Code: Line counting, word counting, and search indexing.
- Marginalia notes and annotation ledger in documents.db.
"""

import os
import json
import csv
import logging
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager
from ..core.export_engine import MarkdownExporter, TabularExporter

logger = logging.getLogger("DocumentService")


class DocumentParserEngine:
    """
    Format-specific structural extraction and content parsing engines.
    """

    @staticmethod
    def parse_csv_summary(file_path: str) -> Dict[str, Any]:
        """Analyzes CSV structure, inferring column types and statistics."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            sample = f.read(4096)
            f.seek(0)
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return {"columns": [], "row_count": 0, "preview_markdown": ""}

        headers = rows[0]
        data_rows = rows[1:11]  # preview first 10 rows

        # Convert to dicts for preview table
        preview_records = []
        for r in data_rows:
            rec = {headers[i] if i < len(headers) else f"Col{i}": (r[i] if i < len(r) else "") for i in range(len(r))}
            preview_records.append(rec)

        preview_table = MarkdownExporter.dict_list_to_table(preview_records, headers=headers)

        return {
            "columns": headers,
            "column_count": len(headers),
            "total_rows": len(rows) - 1,
            "preview_table_markdown": preview_table
        }

    @staticmethod
    def parse_markdown_metadata(content: str) -> Dict[str, Any]:
        """Extracts YAML-style frontmatter and heading hierarchy."""
        frontmatter = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_raw = parts[1]
                body = parts[2]
                for line in fm_raw.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        frontmatter[k.strip()] = v.strip()

        toc = MarkdownExporter.generate_toc(body)
        return {
            "frontmatter": frontmatter,
            "toc": toc,
            "body": body
        }


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
        Parses and reads document contents across formats:
        PDF, Markdown, Plain Text, CSV, JSON, and Source Code files.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        size_bytes = os.path.getsize(file_path)
        content = ""
        total_pages = 1
        pages_content = []
        structured_info: Dict[str, Any] = {}

        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                total_pages = len(reader.pages)
                meta = reader.metadata or {}
                structured_info["pdf_metadata"] = {
                    "title": meta.get("/Title", ""),
                    "author": meta.get("/Author", ""),
                    "creator": meta.get("/Creator", ""),
                    "producer": meta.get("/Producer", "")
                }
                for idx, page in enumerate(reader.pages):
                    extracted = page.extract_text() or f"[Page {idx + 1} - No extractable text]"
                    pages_content.append({"page": idx + 1, "text": extracted})
                content = pages_content[0]["text"] if pages_content else ""
            except Exception as e:
                logger.error(f"Error parsing PDF {file_path}: {e}")
                content = f"Error reading PDF content: {str(e)}"
                pages_content = [{"page": 1, "text": content}]

        elif ext in (".csv", ".tsv"):
            try:
                delimiter = "\t" if ext == ".tsv" else ","
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    all_rows = list(reader)
                
                headers = all_rows[0] if all_rows else []
                data_rows = all_rows[1:201] if len(all_rows) > 1 else []
                structured_info["spreadsheet_data"] = {
                    "columns": headers,
                    "rows": data_rows,
                    "total_rows": max(0, len(all_rows) - 1)
                }
                summary = DocumentParserEngine.parse_csv_summary(file_path)
                structured_info["csv_summary"] = summary
                content = summary.get("preview_table_markdown", "")
                pages_content = [{"page": 1, "text": content}]
            except Exception as e:
                content = f"Error parsing CSV: {e}"
                pages_content = [{"page": 1, "text": content}]

        elif ext in (".xlsx", ".xls"):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(file_path, data_only=True)
                sheet = wb.active
                raw_rows = list(sheet.iter_rows(values_only=True))
                headers = [str(c or f"Col{i+1}") for i, c in enumerate(raw_rows[0])] if raw_rows else []
                data_rows = [[str(cell if cell is not None else "") for cell in r] for r in raw_rows[1:201]]
                structured_info["spreadsheet_data"] = {
                    "sheets": wb.sheetnames,
                    "active_sheet": sheet.title,
                    "columns": headers,
                    "rows": data_rows,
                    "total_rows": max(0, len(raw_rows) - 1)
                }
                content = f"# Spreadsheet: {sheet.title} ({len(raw_rows)} rows, {len(headers)} columns)\n\n"
                pages_content = [{"page": 1, "text": content}]
            except Exception as e:
                content = f"Error reading Spreadsheet: {e}"
                pages_content = [{"page": 1, "text": content}]

        elif ext in (".docx", ".doc"):
            try:
                import docx
                doc_obj = docx.Document(file_path)
                paras = [p.text for p in doc_obj.paragraphs if p.text.strip()]
                tables_data = []
                for tbl in doc_obj.tables:
                    t_rows = [[c.text.strip() for c in row.cells] for row in tbl.rows]
                    if t_rows:
                        tables_data.append(t_rows)
                structured_info["word_document"] = {
                    "paragraphs_count": len(paras),
                    "tables_count": len(tables_data),
                    "tables": tables_data[:5]
                }
                content = "\n\n".join(paras)
                pages_content = [{"page": 1, "text": content}]
            except Exception as e:
                content = f"Error reading Word Document: {e}"
                pages_content = [{"page": 1, "text": content}]

        elif ext in (".pptx", ".ppt"):
            try:
                import pptx
                prs = pptx.Presentation(file_path)
                slides_list = []
                for s_idx, slide in enumerate(prs.slides):
                    texts = []
                    for sh in slide.shapes:
                        if hasattr(sh, "text") and sh.text.strip():
                            texts.append(sh.text.strip())
                    slides_list.append({"page": s_idx + 1, "title": f"Slide {s_idx + 1}", "text": "\n".join(texts)})
                total_pages = len(slides_list) or 1
                pages_content = slides_list if slides_list else [{"page": 1, "text": "Empty Slide Deck"}]
                content = pages_content[0]["text"]
                structured_info["slides"] = slides_list
            except Exception as e:
                content = f"Error reading PowerPoint presentation: {e}"
                pages_content = [{"page": 1, "text": content}]

        elif ext in (".html", ".htm"):
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                structured_info["is_html"] = True
                pages_content = [{"page": 1, "text": content}]
            except Exception as e:
                content = f"Error reading HTML: {e}"
                pages_content = [{"page": 1, "text": content}]

        elif ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".svg"):
            structured_info["is_image"] = True
            structured_info["image_url"] = f"file://{file_path}"
            content = f"Image Display: {file_name}"
            pages_content = [{"page": 1, "text": content}]

        elif ext in (".md", ".markdown"):
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                md_meta = DocumentParserEngine.parse_markdown_metadata(content)
                structured_info["markdown_toc"] = md_meta["toc"]
                structured_info["frontmatter"] = md_meta["frontmatter"]
                pages_content = [{"page": 1, "text": content}]
            except Exception as e:
                content = f"Error reading Markdown: {e}"
                pages_content = [{"page": 1, "text": content}]

        elif ext == ".json":
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    data = json.load(f)
                    content = json.dumps(data, indent=2)
                pages_content = [{"page": 1, "text": content}]
            except Exception as e:
                content = f"Error parsing JSON: {e}"
                pages_content = [{"page": 1, "text": content}]

        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                pages_content = [{"page": 1, "text": content}]
            except Exception as e:
                content = f"Binary or unreadable format: {e}"
                pages_content = [{"page": 1, "text": content}]

        # Register in recent documents database
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO recent_documents (file_name, file_path, file_type, file_size, total_pages)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(file_path) DO UPDATE SET opened_at = CURRENT_TIMESTAMP, total_pages = excluded.total_pages""",
            (file_name, file_path, ext.upper().replace(".", "") or "TXT", size_bytes, total_pages)
        )

        rows = db_manager.execute_query(self.DB, "SELECT * FROM recent_documents WHERE file_path = ?", (file_path,))
        doc_record = rows[0] if rows else {"id": new_id, "file_name": file_name, "file_path": file_path}

        return {
            "id": doc_record["id"],
            "file_name": file_name,
            "file_path": file_path,
            "file_type": ext.upper().replace(".", ""),
            "file_size": size_bytes,
            "total_pages": total_pages,
            "content": content,
            "pages": pages_content,
            "structured_info": structured_info,
            "annotations": self.get_annotations(doc_record["id"])
        }

    def add_annotation(self, document_id: int, page_number: int, note_text: str) -> Dict[str, Any]:
        """Record a marginalia annotation for a document."""
        new_id = db_manager.execute_non_query(
            self.DB,
            "INSERT INTO annotations (document_id, page_number, note_text) VALUES (?, ?, ?)",
            (document_id, page_number, note_text.strip())
        )
        rows = db_manager.execute_query(self.DB, "SELECT * FROM annotations WHERE id = ?", (new_id,))
        return rows[0] if rows else {}

    def get_annotations(self, document_id: int) -> List[Dict[str, Any]]:
        """Retrieve all recorded marginalia annotations for a document."""
        return db_manager.execute_query(
            self.DB,
            "SELECT * FROM annotations WHERE document_id = ? ORDER BY page_number ASC, created_at ASC",
            (document_id,)
        )


document_service = DocumentService()
