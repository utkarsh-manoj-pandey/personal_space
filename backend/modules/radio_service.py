"""
Internet Radio Subsystem Service
Maintains high-definition international internet radio streaming links,
genre taxonomy, station health status, and favorite lists.
"""

from typing import List, Dict, Any, Optional
from ..database_manager import db_manager


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
                    "Darksynth Industrial Radio",
                    "https://synthwave.stream/stream",
                    "Darksynth",
                    "Cyber",
                    "192k",
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
        """List stations with optional genre or search terms."""
        query = "SELECT * FROM stations WHERE 1=1"
        params = []
        if genre and genre != "All":
            query += " AND genre = ?"
            params.append(genre)
        if search:
            query += " AND (name LIKE ? OR genre LIKE ? OR country LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])
        query += " ORDER BY is_favorite DESC, click_count DESC, name ASC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def get_station(self, station_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve station record by ID."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM stations WHERE id = ?", (station_id,))
        return rows[0] if rows else None

    def toggle_favorite(self, station_id: int) -> Optional[Dict[str, Any]]:
        """Toggle favorite marker on station."""
        st = self.get_station(station_id)
        if not st:
            return None
        new_fav = 0 if st["is_favorite"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE stations SET is_favorite = ? WHERE id = ?", (new_fav, station_id))
        return self.get_station(station_id)

    def record_listen(self, station_id: int) -> None:
        """Increment popularity counter."""
        db_manager.execute_non_query(self.DB, "UPDATE stations SET click_count = click_count + 1 WHERE id = ?", (station_id,))

    def add_custom_station(self, name: str, stream_url: str, genre: str = "Custom", country: str = "User") -> Dict[str, Any]:
        """Allow user to register custom streaming stations."""
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO stations (name, stream_url, genre, country, bitrate, codec, is_favorite)
               VALUES (?, ?, ?, ?, '128k', 'Auto', 1)""",
            (name.strip(), stream_url.strip(), genre.strip(), country.strip())
        )
        return self.get_station(new_id) or {}


radio_service = RadioService()
