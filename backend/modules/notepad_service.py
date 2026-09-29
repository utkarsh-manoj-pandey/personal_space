"""
Notepad Subsystem Service
High-throughput, offline notes engine featuring markdown parsing, auto-save tracking,
word/character/reading-time telemetry, tag hierarchies, multi-index readability scoring,
and full-text lexical analytics.
Features:
- Standard Markdown parser with Table of Contents auto-assembly.
- Comprehensive Readability Engine: Flesch Reading Ease, Flesch-Kincaid Grade Level,
  Gunning Fog Index, Coleman-Liau Index, Automated Readability Index (ARI).
- Lexical frequency analyzer, syllable estimation, and keyword extraction.
- Markdown to HTML and Plain Text exporters.
- Persistent document ledger in notepad.db.
"""

import math
import re
from typing import List, Dict, Any, Optional, Tuple
from ..database_manager import db_manager
from ..core.export_engine import MarkdownExporter


class TextAnalyticsEngine:
    """
    Pure Python linguistic and readability analysis engine.
    Calculates readability indexes, lexical diversity, syllable counts, and keyword frequencies.
    """

    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
        "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
        "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
        "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
        "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
        "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
        "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
        "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
        "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
        "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
        "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's",
        "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom",
        "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
        "you're", "you've", "your", "yours", "yourself", "yourselves"
    }

    @staticmethod
    def count_syllables_word(word: str) -> int:
        """Heuristic English syllable counter based on vowel groupings."""
        w = word.lower().strip()
        if len(w) <= 3:
            return 1
        # Remove trailing silent e
        if w.endswith('e') and not w.endswith('le') and not w.endswith('ee'):
            w = w[:-1]
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        for char in w:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        return max(1, count)

    @classmethod
    def analyze_text(cls, text: str) -> Dict[str, Any]:
        """
        Computes word count, character count, sentence count, syllable count,
        and standardized readability indexes.
        """
        clean_text = text.strip()
        if not clean_text:
            return {
                "words": 0, "characters": 0, "sentences": 0, "syllables": 0,
                "reading_time_minutes": 0.0, "flesch_reading_ease": 100.0,
                "flesch_kincaid_grade": 0.0, "gunning_fog": 0.0,
                "coleman_liau_index": 0.0, "automated_readability_index": 0.0,
                "readability_tier": "Very Easy", "top_keywords": []
            }

        # Sentence segmentation
        sentences = re.split(r'[.!?]+(?:\s+|$)', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = max(1, len(sentences))

        # Words
        words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', clean_text)
        word_count = len(words)
        char_count = len(clean_text)

        if word_count == 0:
            return {
                "words": 0, "characters": char_count, "sentences": 0, "syllables": 0,
                "reading_time_minutes": 0.0, "flesch_reading_ease": 100.0,
                "flesch_kincaid_grade": 0.0, "gunning_fog": 0.0,
                "coleman_liau_index": 0.0, "automated_readability_index": 0.0,
                "readability_tier": "Very Easy", "top_keywords": []
            }

        total_syllables = sum(cls.count_syllables_word(w) for w in words)
        complex_words = sum(1 for w in words if cls.count_syllables_word(w) >= 3)

        # Average metrics
        words_per_sentence = word_count / sentence_count
        syllables_per_word = total_syllables / word_count
        letters_per_word = sum(len(w) for w in words) / word_count

        # 1. Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        flesch_ease = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
        flesch_ease = max(0.0, min(100.0, flesch_ease))

        # 2. Flesch-Kincaid Grade Level: 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
        fk_grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
        fk_grade = max(0.0, fk_grade)

        # 3. Gunning Fog Index: 0.4 * ((words / sentences) + 100 * (complex_words / words))
        gunning_fog = 0.4 * (words_per_sentence + 100.0 * (complex_words / word_count))

        # 4. Coleman-Liau Index: 0.0588*L - 0.296*S - 15.8 (L = letters/100 words, S = sentences/100 words)
        l_val = letters_per_word * 100.0
        s_val = (sentence_count / word_count) * 100.0
        coleman_liau = 0.0588 * l_val - 0.296 * s_val - 15.8

        # 5. Automated Readability Index (ARI): 4.71*(characters/words) + 0.5*(words/sentences) - 21.43
        letters_count = sum(len(w) for w in words)
        ari = 4.71 * (letters_count / word_count) + 0.5 * words_per_sentence - 21.43

        # Readability Tier
        if flesch_ease >= 90.0:
            tier = "Very Easy (5th grade)"
        elif flesch_ease >= 80.0:
            tier = "Easy (6th grade)"
        elif flesch_ease >= 70.0:
            tier = "Fairly Easy (7th grade)"
        elif flesch_ease >= 60.0:
            tier = "Standard (8th-9th grade)"
        elif flesch_ease >= 50.0:
            tier = "Fairly Difficult (10th-12th grade)"
        elif flesch_ease >= 30.0:
            tier = "Difficult (College level)"
        else:
            tier = "Very Difficult (Academic/Post-Graduate)"

        # Keyword frequency (filtering stopwords)
        freq_map: Dict[str, int] = {}
        for w in words:
            wl = w.lower()
            if wl not in cls.STOPWORDS and len(wl) > 2:
                freq_map[wl] = freq_map.get(wl, 0) + 1

        top_kw = sorted(freq_map.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "words": word_count,
            "characters": char_count,
            "sentences": sentence_count,
            "syllables": total_syllables,
            "complex_words": complex_words,
            "reading_time_minutes": round(word_count / 200.0, 1),
            "flesch_reading_ease": round(flesch_ease, 1),
            "flesch_kincaid_grade": round(fk_grade, 1),
            "gunning_fog": round(gunning_fog, 1),
            "coleman_liau_index": round(coleman_liau, 1),
            "automated_readability_index": round(ari, 1),
            "readability_tier": tier,
            "top_keywords": [{"word": k, "count": v} for k, v in top_kw]
        }


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
                metrics = TextAnalyticsEngine.analyze_text(content)
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT INTO notes (title, content, tags, is_pinned, word_count, char_count, reading_time_mins)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (title, content, tags, is_pinned, metrics["words"], metrics["characters"], metrics["reading_time_minutes"])
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
        """Fetch single note with full textual analytics and Table of Contents."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM notes WHERE id = ?", (note_id,))
        if not rows:
            return None
        note = dict(rows[0])
        content = note.get("content", "")
        note["analytics"] = TextAnalyticsEngine.analyze_text(content)
        note["toc"] = MarkdownExporter.generate_toc(content)
        return note

    def save_note(self, note_id: int, title: str, content: str, tags: str = "", is_pinned: int = 0) -> Dict[str, Any]:
        """
        Creates or updates a note record. Computes linguistic telemetry automatically.
        """
        metrics = TextAnalyticsEngine.analyze_text(content)
        wc = metrics["words"]
        cc = metrics["characters"]
        rt = metrics["reading_time_minutes"]

        clean_title = title.strip() or "Untitled Document"

        if note_id and note_id > 0:
            db_manager.execute_non_query(
                self.DB,
                """UPDATE notes SET 
                   title = ?, content = ?, tags = ?, is_pinned = ?,
                   word_count = ?, char_count = ?, reading_time_mins = ?,
                   updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (clean_title, content, tags, is_pinned, wc, cc, rt, note_id)
            )
            saved_id = note_id
        else:
            saved_id = db_manager.execute_non_query(
                self.DB,
                """INSERT INTO notes 
                   (title, content, tags, is_pinned, word_count, char_count, reading_time_mins)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (clean_title, content, tags, is_pinned, wc, cc, rt)
            )

        saved = self.get_note(saved_id)
        return saved or {"id": saved_id, "title": clean_title, "word_count": wc}

    def delete_note(self, note_id: int) -> bool:
        """Permanently deletes a note."""
        return db_manager.execute_non_query(self.DB, "DELETE FROM notes WHERE id = ?", (note_id,)) > 0

    def toggle_pin(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Toggles pinned status."""
        note = self.get_note(note_id)
        if not note:
            return None
        new_pin = 0 if note.get("is_pinned") else 1
        db_manager.execute_non_query(self.DB, "UPDATE notes SET is_pinned = ? WHERE id = ?", (new_pin, note_id))
        return self.get_note(note_id)

    def export_note_html(self, note_id: int) -> Optional[str]:
        """Renders note content to formatted HTML with Table of Contents."""
        note = self.get_note(note_id)
        if not note:
            return None
        content = note.get("content", "")
        toc = MarkdownExporter.generate_toc(content)
        body_html = MarkdownExporter.to_clean_html(content)
        toc_html = MarkdownExporter.to_clean_html(toc)
        return f"<div class='aether-note-toc'>{toc_html}</div><div class='aether-note-body'>{body_html}</div>"


notepad_service = NotepadService()
