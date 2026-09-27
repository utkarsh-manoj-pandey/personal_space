"""
Music Subsystem Service
High-fidelity local audio library manager supporting MP3, WAV, FLAC, OGG, and AAC.
Includes automatic algorithmic procedural audio generator for instant out-of-the-box ambient soundscapes,
playlist hierarchy, and playback metadata tracking.
"""

import os
import math
import struct
import wave
import logging
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager

logger = logging.getLogger("MusicService")


class MusicService:
    DB = "music.db"

    def __init__(self):
        self.media_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "audio"))
        os.makedirs(self.media_dir, exist_ok=True)
        self._generate_default_soundscapes_if_empty()
        self._sync_library()

    def _generate_default_soundscapes_if_empty(self):
        """
        Procedurally synthesizes pristine binaural and electronic ambient soundscape WAV files
        directly into the local audio repository so the user enjoys immediate rich audio out of the box.
        """
        stems = [
            ("Cyberpunk_Neon_Grid.wav", "Neon Grid Odyssey", "Nexus Audio Collective", "Synthesized Horizons", 440.0, 15),
            ("Deep_Space_Harmonic.wav", "Deep Space Resonance", "Aether Orbital Lab", "Stellar Waves", 220.0, 15),
            ("Quantum_Focus_Pulse.wav", "Quantum Focus Pulse (432Hz)", "Neural Acoustics", "Binaural Operations", 432.0, 15),
            ("Chrono_Sub_Bass_Flow.wav", "Sub-Bass Chrono Drift", "Titan Sound Labs", "Low Frequency Dynamics", 110.0, 15)
        ]

        sample_rate = 44100

        for filename, title, artist, album, base_freq, duration_sec in stems:
            filepath = os.path.join(self.media_dir, filename)
            if not os.path.exists(filepath):
                try:
                    num_samples = int(sample_rate * duration_sec)
                    with wave.open(filepath, 'w') as wav_file:
                        wav_file.setnchannels(2)  # Stereo
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(sample_rate)

                        frames = bytearray()
                        for i in range(num_samples):
                            t = float(i) / sample_rate
                            # Rich harmonic additive synthesis with subtle frequency modulation
                            envelope = min(1.0, t / 1.5) * min(1.0, (duration_sec - t) / 1.5)
                            modulator = math.sin(2.0 * math.pi * 0.25 * t)
                            left_val = (
                                math.sin(2.0 * math.pi * base_freq * t + modulator) * 0.4 +
                                math.sin(2.0 * math.pi * (base_freq * 1.5) * t) * 0.2 +
                                math.sin(2.0 * math.pi * (base_freq * 2.0) * t) * 0.1
                            ) * envelope * 0.6

                            right_val = (
                                math.sin(2.0 * math.pi * (base_freq + 2.5) * t - modulator) * 0.4 +
                                math.sin(2.0 * math.pi * (base_freq * 1.505) * t) * 0.2 +
                                math.sin(2.0 * math.pi * (base_freq * 2.01) * t) * 0.1
                            ) * envelope * 0.6

                            left_int = int(max(-32767, min(32767, left_val * 32767)))
                            right_int = int(max(-32767, min(32767, right_val * 32767)))
                            frames.extend(struct.pack('<hh', left_int, right_int))

                        wav_file.writeframes(frames)
                    logger.info(f"Synthesized ambient master track: {filename}")
                except Exception as e:
                    logger.error(f"Failed to synthesize soundscape {filename}: {e}")

    def _sync_library(self):
        """Scans the local media directory and indexes any new audio files."""
        supported_exts = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a"}
        for f in os.listdir(self.media_dir):
            ext = os.path.splitext(f)[1].lower()
            if ext in supported_exts:
                full_path = os.path.join(self.media_dir, f)
                # Check if already indexed
                exists = db_manager.execute_query(self.DB, "SELECT id FROM tracks WHERE file_path = ?", (full_path,))
                if not exists:
                    clean_title = os.path.splitext(f)[0].replace("_", " ")
                    db_manager.execute_non_query(
                        self.DB,
                        """INSERT INTO tracks (title, artist, album, duration, file_path, genre, bitrate)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (clean_title, "Personal Workstation Audio", "Synthesized Master", 15, full_path, "Ambient Cyber", 320)
                    )

    def list_tracks(self, search: str = "") -> List[Dict[str, Any]]:
        """List all tracks in the workstation library."""
        self._sync_library()
        query = "SELECT * FROM tracks"
        params = []
        if search:
            query += " WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?"
            term = f"%{search}%"
            params.extend([term, term, term])
        query += " ORDER BY is_favorite DESC, title ASC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def get_track(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Fetch track details by ID."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM tracks WHERE id = ?", (track_id,))
        return rows[0] if rows else None

    def toggle_favorite(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Toggle favorite flag on track."""
        track = self.get_track(track_id)
        if not track:
            return None
        new_fav = 0 if track["is_favorite"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE tracks SET is_favorite = ? WHERE id = ?", (new_fav, track_id))
        return self.get_track(track_id)

    def increment_play_count(self, track_id: int) -> None:
        """Increment play statistics on track completion."""
        db_manager.execute_non_query(self.DB, "UPDATE tracks SET play_count = play_count + 1 WHERE id = ?", (track_id,))

    def scan_directory(self, folder_path: str) -> int:
        """Import tracks from an arbitrary user-selected directory."""
        if not os.path.exists(folder_path):
            return 0
        supported_exts = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a"}
        added = 0
        for root, _, files in os.walk(folder_path):
            for f in files:
                if os.path.splitext(f)[1].lower() in supported_exts:
                    full_path = os.path.join(root, f)
                    exists = db_manager.execute_query(self.DB, "SELECT id FROM tracks WHERE file_path = ?", (full_path,))
                    if not exists:
                        clean_title = os.path.splitext(f)[0].replace("_", " ")
                        db_manager.execute_non_query(
                            self.DB,
                            """INSERT INTO tracks (title, artist, album, duration, file_path, genre)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (clean_title, "Local User Media", "Imported Collection", 0, full_path, "Local Audio")
                        )
                        added += 1
        return added


music_service = MusicService()
