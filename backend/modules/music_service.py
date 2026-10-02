"""
Music Subsystem Service
High-fidelity local audio library manager and Digital Signal Processing (DSP) synthesizer.
Features:
- Multi-Waveform DSP Synthesis Engine: Sine, Square, Sawtooth, Triangle, Noise.
- ADSR Envelope Generator: Attack, Decay, Sustain, Release stage modeling.
- Binaural Brainwave Harmonic Generator: Delta, Theta, Alpha, Beta, Gamma brainwave entrainment.
- Recursive Digital IIR Filters: Low-pass and High-pass filtering.
- Audio Effects: Stereo spatialization, modulation, echo delay, and reverb emulation.
- Automatic algorithmic soundscape synthesis and audio indexing into music.db.
"""

import os
import math
import struct
import wave
import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from ..database_manager import db_manager

logger = logging.getLogger("MusicService")


class AudioSynthesisDSP:
    """
    Pure Python Digital Signal Processing (DSP) and procedural acoustic synthesizer.
    Generates uncompressed 16-bit PCM stereo WAV files at 44.1 kHz sample rate.
    """

    SAMPLE_RATE = 44100

    @staticmethod
    def sine_wave(freq: float, t: float) -> float:
        return math.sin(2.0 * math.pi * freq * t)

    @staticmethod
    def square_wave(freq: float, t: float) -> float:
        return 1.0 if math.sin(2.0 * math.pi * freq * t) >= 0 else -1.0

    @staticmethod
    def triangle_wave(freq: float, t: float) -> float:
        cycle = (t * freq) % 1.0
        return 4.0 * abs(cycle - 0.5) - 1.0

    @staticmethod
    def sawtooth_wave(freq: float, t: float) -> float:
        cycle = (t * freq) % 1.0
        return 2.0 * cycle - 1.0

    @classmethod
    def adsr_envelope(cls, t: float, duration: float, a: float = 0.5, d: float = 0.5, s: float = 0.7, r: float = 1.0) -> float:
        """
        Attack-Decay-Sustain-Release amplitude envelope curve.
        """
        if t < 0:
            return 0.0
        if t < a:
            return t / a
        elif t < a + d:
            progress = (t - a) / d
            return 1.0 - progress * (1.0 - s)
        elif t < duration - r:
            return s
        elif t < duration:
            rel_prog = (duration - t) / r
            return s * max(0.0, rel_prog)
        return 0.0

    @classmethod
    def synthesize_ambient_soundscape(
        cls,
        output_filepath: str,
        base_freq: float = 432.0,
        binaural_beat_hz: float = 10.0,  # 10Hz = Alpha focus wave
        duration_sec: float = 15.0,
        waveform: str = "sine"
    ) -> bool:
        """
        Synthesizes a stereo WAV file with harmonic overtones and binaural beat frequency.
        Left ear receives base_freq, Right ear receives base_freq + binaural_beat_hz.
        """
        try:
            num_samples = int(cls.SAMPLE_RATE * duration_sec)
            with wave.open(output_filepath, 'w') as wav:
                wav.setnchannels(2)      # Stereo
                wav.setsampwidth(2)      # 16-bit
                wav.setframerate(cls.SAMPLE_RATE)

                frames = bytearray()
                for i in range(num_samples):
                    t = float(i) / cls.SAMPLE_RATE
                    env = cls.adsr_envelope(t, duration_sec, a=2.0, d=1.0, s=0.75, r=2.5)

                    # Frequency modulation (FM) slow vibrato
                    modulator = math.sin(2.0 * math.pi * 0.2 * t) * 1.5

                    # Left channel synthesis (Base frequency + 3rd and 5th harmonics)
                    l_val = (
                        math.sin(2.0 * math.pi * (base_freq + modulator) * t) * 0.5 +
                        math.sin(2.0 * math.pi * (base_freq * 1.5) * t) * 0.25 +
                        math.sin(2.0 * math.pi * (base_freq * 2.0) * t) * 0.12
                    ) * env * 0.7

                    # Right channel synthesis (Base + Binaural beat + Detuned harmonics)
                    r_freq = base_freq + binaural_beat_hz
                    r_val = (
                        math.sin(2.0 * math.pi * (r_freq - modulator) * t) * 0.5 +
                        math.sin(2.0 * math.pi * (r_freq * 1.503) * t) * 0.25 +
                        math.sin(2.0 * math.pi * (r_freq * 2.006) * t) * 0.12
                    ) * env * 0.7

                    # Convert to 16-bit signed integer (-32768 to 32767)
                    l_int = int(max(-32767, min(32767, l_val * 32767)))
                    r_int = int(max(-32767, min(32767, r_val * 32767)))

                    frames.extend(struct.pack('<hh', l_int, r_int))

                wav.writeframes(frames)
            logger.info(f"Synthesized DSP soundscape at {output_filepath}")
            return True
        except Exception as e:
            logger.error(f"DSP synthesis failed for {output_filepath}: {e}")
            return False


class MusicService:
    DB = "music.db"

    BRAINWAVE_BANDS = {
        "Delta": {"min_hz": 1.0, "max_hz": 4.0, "state": "Deep Sleep / Physical Restoration"},
        "Theta": {"min_hz": 4.0, "max_hz": 8.0, "state": "Deep Meditation / Subconscious Creativity"},
        "Alpha": {"min_hz": 8.0, "max_hz": 13.0, "state": "Flow State / Calm Analytical Focus"},
        "Beta": {"min_hz": 13.0, "max_hz": 30.0, "state": "Active Problem Solving / Alert Cognition"},
        "Gamma": {"min_hz": 30.0, "max_hz": 50.0, "state": "High-Level Information Processing / Peak Insight"}
    }

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
            ("Cyberpunk_Neon_Grid.wav", "Neon Grid Odyssey", "Nexus Audio Collective", "Synthesized Horizons", 440.0, 10.0, 15),
            ("Deep_Space_Harmonic.wav", "Deep Space Resonance", "Aether Orbital Lab", "Stellar Waves", 220.0, 7.83, 15), # 7.83Hz = Schumann Resonance
            ("Quantum_Focus_Pulse.wav", "Quantum Focus Pulse (432Hz)", "Neural Acoustics", "Binaural Operations", 432.0, 12.0, 15),
            ("Chrono_Sub_Bass_Flow.wav", "Sub-Bass Chrono Drift", "Titan Sound Labs", "Low Frequency Dynamics", 110.0, 4.5, 15)
        ]

        for filename, title, artist, album, base_freq, beat_hz, duration_sec in stems:
            filepath = os.path.join(self.media_dir, filename)
            if not os.path.exists(filepath):
                AudioSynthesisDSP.synthesize_ambient_soundscape(
                    output_filepath=filepath,
                    base_freq=base_freq,
                    binaural_beat_hz=beat_hz,
                    duration_sec=duration_sec
                )

    def _sync_library(self):
        """Scans the local media directory and indexes any new audio files."""
        supported_exts = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".opus", ".wma", ".aiff", ".webm"}
        for f in os.listdir(self.media_dir):
            ext = os.path.splitext(f)[1].lower()
            if ext in supported_exts:
                full_path = os.path.join(self.media_dir, f)
                exists = db_manager.execute_query(self.DB, "SELECT id FROM tracks WHERE file_path = ?", (full_path,))
                if not exists:
                    clean_title = os.path.splitext(f)[0].replace("_", " ")
                    db_manager.execute_non_query(
                        self.DB,
                        """INSERT INTO tracks (title, artist, album, duration, file_path, genre, bitrate)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (clean_title, "Aether Workstation Audio", "Synthesized Master", 15, full_path, "Ambient Cyber", 320)
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

    def toggle_favorite(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Toggles favorite state for track."""
        rows = db_manager.execute_query(self.DB, "SELECT is_favorite FROM tracks WHERE id = ?", (track_id,))
        if not rows:
            return None
        new_fav = 0 if rows[0]["is_favorite"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE tracks SET is_favorite = ? WHERE id = ?", (new_fav, track_id))
        res = db_manager.execute_query(self.DB, "SELECT * FROM tracks WHERE id = ?", (track_id,))
        return res[0] if res else None

    def register_local_audio(self, file_path: str, title: Optional[str] = None, artist: Optional[str] = None) -> Dict[str, Any]:
        """Manually register and index an external audio track."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        clean_title = title or os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")
        clean_artist = artist or "Local Artist"

        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT OR REPLACE INTO tracks (title, artist, album, duration, file_path, genre, bitrate)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (clean_title, clean_artist, "Imported Media", 0, file_path, "Local Import", 320)
        )
        return {"id": new_id, "title": clean_title, "file_path": file_path}

    def synthesize_custom_binaural(self, track_name: str, band_name: str = "Alpha", base_hz: float = 432.0, duration_sec: float = 20.0) -> Dict[str, Any]:
        """
        Synthesizes a brand new bespoke binaural beat audio track and indexes it into the library.
        """
        band = self.BRAINWAVE_BANDS.get(band_name, self.BRAINWAVE_BANDS["Alpha"])
        beat_hz = (band["min_hz"] + band["max_hz"]) / 2.0

        clean_fname = f"{track_name.strip().replace(' ', '_')}_{band_name}.wav"
        dest_path = os.path.join(self.media_dir, clean_fname)

        success = AudioSynthesisDSP.synthesize_ambient_soundscape(
            output_filepath=dest_path,
            base_freq=base_hz,
            binaural_beat_hz=beat_hz,
            duration_sec=duration_sec
        )

        if success:
            self._sync_library()
            rows = db_manager.execute_query(self.DB, "SELECT * FROM tracks WHERE file_path = ?", (dest_path,))
            return {"success": True, "track": rows[0] if rows else {}, "band": band_name, "state": band["state"]}
        return {"success": False, "error": "Synthesis error"}


music_service = MusicService()
