"""
Internet Radio Subsystem Service
Maintains high-definition international internet radio streaming links,
genre taxonomy, station health status, stream latency diagnostics, and M3U/PLS playlist synchronization.
Features:
- Live HTTP audio stream handshake and latency analyzer.
- Equalizer Profile Engine: 10-Band frequency gain models for acoustic, electronic, and vocal listening.
- M3U and PLS playlist format generators and parsers.
- Persistent stations, codecs, and favorite lists in radio.db.
"""

import time
import urllib.request
import logging
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager

logger = logging.getLogger("RadioService")


class RadioEqualizerEngine:
    """
    Standardized 10-band graphic audio equalizer curves.
    Frequencies: [32Hz, 64Hz, 125Hz, 250Hz, 500Hz, 1kHz, 2kHz, 4kHz, 8kHz, 16kHz].
    Gains in decibels (dB) in range [-12.0, +12.0].
    """

    PRESETS = {
        "Flat": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Bass Boost": [6.0, 5.5, 4.0, 2.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Electronic / Synth": [4.5, 4.0, 2.0, 0.0, -1.0, 1.5, 2.5, 3.5, 4.0, 4.5],
        "Acoustic / Vocal": [0.0, 1.0, 2.0, 3.0, 3.5, 3.0, 2.0, 1.5, 1.0, 0.5],
        "Classical Symphonic": [4.0, 3.5, 3.0, 2.5, -0.5, -0.5, 0.0, 2.0, 3.5, 4.0],
        "Cyberpunk Sub-Bass": [8.0, 7.0, 5.0, 2.0, -1.0, 0.0, 1.0, 3.0, 5.0, 6.0],
        "Speech / News Radio": [-3.0, -2.0, 0.0, 2.5, 4.0, 4.0, 3.0, 1.5, 0.0, -2.0]
    }

    @classmethod
    def get_presets(cls) -> Dict[str, List[float]]:
        return cls.PRESETS


class RadioService:
    DB = "radio.db"

    def __init__(self):
        self._seed_default_stations()

    def _seed_default_stations(self):
        """Seed established global public internet radio streams."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM stations")
        if count and count[0]["count"] == 0:
            stations = [
                (
                    "SomaFM: Groove Salad",
                    "https://ice1.somafm.com/groovesalad-128-mp3",
                    "Ambient Chill",
                    "USA",
                    "128k",
                    "MP3",
                    1
                ),
                (
                    "SomaFM: Drone Zone",
                    "https://ice1.somafm.com/dronezone-128-mp3",
                    "Space Ambient",
                    "USA",
                    "128k",
                    "MP3",
                    1
                ),
                (
                    "Nightwave Plaza (Vaporwave/Synth)",
                    "https://radio.plaza.one/mp3",
                    "Synthwave",
                    "Global",
                    "128k",
                    "MP3",
                    1
                ),
                (
                    "SomaFM: Secret Agent",
                    "https://ice1.somafm.com/secretagent-128-mp3",
                    "Spy Lounge",
                    "USA",
                    "128k",
                    "MP3",
                    0
                ),
                (
                    "SomaFM: Space Station Soma",
                    "https://ice1.somafm.com/spacestation-128-mp3",
                    "Electronica",
                    "USA",
                    "128k",
                    "MP3",
                    0
                ),
                (
                    "SomaFM: DEF CON Radio",
                    "https://ice1.somafm.com/defcon-128-mp3",
                    "Cyber Hack",
                    "USA",
                    "128k",
                    "MP3",
                    1
                ),
                (
                    "BBC World Service News",
                    "https://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
                    "News & Politics",
                    "UK",
                    "128k",
                    "MP3",
                    0
                ),
                (
                    "KUSC Classical HD",
                    "https://kusc.streamguys1.com/kusc-128k-aac",
                    "Classical",
                    "USA",
                    "128k",
                    "AAC",
                    0
                ),
                (
                    "Radio Swiss Jazz",
                    "http://stream.srg-ssr.ch/m/rsj/mp3_128",
                    "Acoustic Jazz",
                    "Switzerland",
                    "128k",
                    "MP3",
                    0
                ),
                (
                    "FIP Radio Paris",
                    "https://icecast.radiofrance.fr/fip-midfi.mp3",
                    "Eclectic",
                    "France",
                    "128k",
                    "MP3",
                    0
                )
            ]

            for s in stations:
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT OR IGNORE INTO stations (name, stream_url, genre, country, bitrate, codec, is_favorite)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    s
                )

    def list_stations(self, genre: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """List radio stations with optional genre or search terms."""
        query = "SELECT * FROM stations WHERE 1=1"
        params = []
        if genre and genre != "All":
            query += " AND genre = ?"
            params.append(genre)
        if search:
            query += " AND (name LIKE ? OR country LIKE ? OR genre LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])
        query += " ORDER BY is_favorite DESC, click_count DESC, name ASC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def toggle_favorite(self, station_id: int) -> Optional[Dict[str, Any]]:
        """Toggle favorite status for stream."""
        rows = db_manager.execute_query(self.DB, "SELECT is_favorite FROM stations WHERE id = ?", (station_id,))
        if not rows:
            return None
        new_fav = 0 if rows[0]["is_favorite"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE stations SET is_favorite = ? WHERE id = ?", (new_fav, station_id))
        res = db_manager.execute_query(self.DB, "SELECT * FROM stations WHERE id = ?", (station_id,))
        return res[0] if res else None

    def test_stream_health(self, stream_url: str) -> Dict[str, Any]:
        """Performs HTTP HEAD/GET probe to verify stream availability and response latency."""
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(
                stream_url,
                headers={"User-Agent": "AetherRadioClient/2.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                content_type = response.headers.get("Content-Type", "unknown")
                latency_ms = round((time.perf_counter() - t0) * 1000.0, 1)
                is_audio = "audio" in content_type or "ogg" in content_type or "mpeg" in content_type
                return {
                    "online": True,
                    "status_code": response.status,
                    "content_type": content_type,
                    "latency_ms": latency_ms,
                    "valid_audio_stream": is_audio
                }
        except Exception as e:
            return {
                "online": False,
                "error": str(e),
                "latency_ms": round((time.perf_counter() - t0) * 1000.0, 1),
                "valid_audio_stream": False
            }

    def add_custom_station(self, name: str, stream_url: str, genre: str = "Custom", country: str = "Global") -> Dict[str, Any]:
        """Registers a user-defined internet radio station."""
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT OR REPLACE INTO stations (name, stream_url, genre, country, bitrate, codec)
               VALUES (?, ?, ?, ?, '128k', 'MP3')""",
            (name.strip(), stream_url.strip(), genre.strip() or "Custom", country.strip() or "Global")
        )
        return {"id": new_id, "name": name, "stream_url": stream_url, "genre": genre}

    def delete_station(self, station_id: int) -> bool:
        """Removes station."""
        return db_manager.execute_non_query(self.DB, "DELETE FROM stations WHERE id = ?", (station_id,)) > 0

    def export_m3u_playlist(self) -> str:
        """Exports all stations to standard Extended M3U playlist format."""
        stations = self.list_stations()
        lines = ["#EXTM3U"]
        for s in stations:
            name = s.get("name", "Radio Station")
            url = s.get("stream_url", "")
            lines.append(f"#EXTINF:-1,{name}")
            lines.append(url)
        return "\n".join(lines)

    def export_pls_playlist(self) -> str:
        """Exports all stations to standard PLS playlist format."""
        stations = self.list_stations()
        lines = ["[playlist]", f"NumberOfEntries={len(stations)}"]
        for idx, s in enumerate(stations, start=1):
            name = s.get("name", "Radio Station")
            url = s.get("stream_url", "")
            lines.append(f"File{idx}={url}")
            lines.append(f"Title{idx}={name}")
            lines.append(f"Length{idx}=-1")
        lines.append("Version=2")
        return "\n".join(lines)

    def get_equalizer_presets(self) -> Dict[str, List[float]]:
        """Return 10-band equalizer presets."""
        return RadioEqualizerEngine.get_presets()


radio_service = RadioService()
