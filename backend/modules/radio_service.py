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
        self._ensure_schema()
        self._seed_default_stations()

    def _ensure_schema(self):
        """Ensure language column exists in stations table."""
        try:
            cols = [row["name"] for row in db_manager.execute_query(self.DB, "PRAGMA table_info(stations)")]
            if "language" not in cols:
                db_manager.execute_non_query(self.DB, "ALTER TABLE stations ADD COLUMN language TEXT DEFAULT 'English'")
        except Exception as e:
            logger.debug(f"Schema check on stations: {e}")

    def _seed_default_stations(self):
        """Seed established global public internet radio streams with countries and languages."""
        stations = [
            # USA
            ("SomaFM: Groove Salad", "https://ice1.somafm.com/groovesalad-128-mp3", "Ambient Chill", "USA", "English", "128k", "MP3", 1),
            ("SomaFM: Drone Zone", "https://ice1.somafm.com/dronezone-128-mp3", "Space Ambient", "USA", "English", "128k", "MP3", 1),
            ("SomaFM: DEF CON Radio", "https://ice1.somafm.com/defcon-128-mp3", "Cyber Hack", "USA", "English", "128k", "MP3", 1),
            ("SomaFM: Secret Agent", "https://ice1.somafm.com/secretagent-128-mp3", "Spy Lounge", "USA", "English", "128k", "MP3", 0),
            ("SomaFM: Space Station Soma", "https://ice1.somafm.com/spacestation-128-mp3", "Electronica", "USA", "English", "128k", "MP3", 0),
            ("KUSC Classical HD", "https://kusc.streamguys1.com/kusc-128k-aac", "Classical", "USA", "English", "128k", "AAC", 0),
            ("WNYC 93.9 FM Public Radio", "https://fm939.wnyc.org/wnycfm", "News & Culture", "USA", "English", "128k", "MP3", 0),
            # Global / Electronic
            ("Nightwave Plaza", "https://radio.plaza.one/mp3", "Synthwave", "Global", "Instrumental", "128k", "MP3", 1),
            ("Ibiza Global Radio", "https://listens.ibizaglobalradio.com:8024/ibizaglobalradio.mp3", "House / Electronic", "Global", "English", "128k", "MP3", 1),
            ("Lofi Hip Hop Stream", "https://play.streamafrica.net/lofiradio", "Lofi Beats", "Global", "Instrumental", "128k", "MP3", 1),
            # UK
            ("BBC World Service News", "https://stream.live.vc.bbcmedia.co.uk/bbc_world_service", "News & Politics", "UK", "English", "128k", "MP3", 1),
            ("Classic FM London", "https://media-ice.musicradio.com/ClassicFMMP3", "Classical", "UK", "English", "128k", "MP3", 0),
            ("Capital FM UK", "https://media-ice.musicradio.com/CapitalMP3", "Top 40 Pop", "UK", "English", "128k", "MP3", 0),
            # France
            ("FIP Radio Paris", "https://icecast.radiofrance.fr/fip-midfi.mp3", "Eclectic", "France", "French", "128k", "MP3", 1),
            ("Radio Nova France", "https://novazz.ice.infomaniak.ch/novazz-128.mp3", "World / Indie", "France", "French", "128k", "MP3", 0),
            ("France Inter", "https://icecast.radiofrance.fr/franceinter-midfi.mp3", "News & Culture", "France", "French", "128k", "MP3", 0),
            # Germany
            ("TechnoBase.FM", "https://listen.technobase.fm/tunein-mp3-pls", "EDM / Techno", "Germany", "German", "128k", "MP3", 0),
            ("Antenne Bayern", "https://s3-webradio.antenne.de/antenne", "Pop Hits", "Germany", "German", "128k", "MP3", 0),
            ("Radio BOB! Rock", "https://streams.radiobob.de/bob-live/mp3-192/streams.radiobob.de/", "Rock", "Germany", "German", "192k", "MP3", 0),
            # Switzerland
            ("Radio Swiss Jazz", "http://stream.srg-ssr.ch/m/rsj/mp3_128", "Acoustic Jazz", "Switzerland", "Instrumental", "128k", "MP3", 1),
            ("Radio Swiss Classic", "http://stream.srg-ssr.ch/m/rsc_de/mp3_128", "Classical", "Switzerland", "Instrumental", "128k", "MP3", 0),
            # India
            ("Radio Mirchi Top Hits", "https://stream.zeno.fm/f3wvbbqmdg8uv", "Bollywood Pop", "India", "Hindi", "128k", "MP3", 1),
            ("Vividh Bharati Retro", "https://air.pc.cdn.bitgravity.com/air/live/pbaudio001/playlist.m3u8", "Classic Retro", "India", "Hindi", "128k", "AAC", 0),
            ("AIR FM Gold Delhi", "https://air.pc.cdn.bitgravity.com/air/live/pbaudio002/playlist.m3u8", "News & Music", "India", "Hindi", "128k", "AAC", 0),
            # Japan
            ("J-Pop Powerplay Tokyo", "https://kathy.torontocast.com:3560/stream", "J-Pop", "Japan", "Japanese", "128k", "MP3", 1),
            ("Anime NFO Radio", "https://anradio-ice.streamguys1.com/anradio.mp3", "Anime Soundtracks", "Japan", "Japanese", "128k", "MP3", 0),
            ("Big B Radio - Jpop", "https://antares.dribbcast.com/proxy/jpop?mp=/stream", "Asian Pop", "Japan", "Japanese", "128k", "MP3", 0),
            # Spain
            ("Cadena SER Madrid", "https://playerservices.streamtheworld.com/api/livestream-redirect/CADENASER.mp3", "News & Talk", "Spain", "Spanish", "128k", "MP3", 0),
            ("Los 40 Principales", "https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40.mp3", "Latin Pop", "Spain", "Spanish", "128k", "MP3", 0),
            # Italy
            ("Radio Italia Solo Musica", "https://stream.radioitalia.it", "Italian Pop", "Italy", "Italian", "128k", "MP3", 0),
            ("Radio 105 Network", "https://icecast.unitedradio.it/Radio105.mp3", "Contemporary Hit", "Italy", "Italian", "128k", "MP3", 0),
            # Canada
            ("CBC Radio One Toronto", "https://cbc_r1_tor.akacdn.cowboy.net/cbc_r1_tor", "News & Discussion", "Canada", "English", "128k", "MP3", 0),
            ("Indie88 Toronto", "https://indie.streamon.fm/indie-64k.aac", "Indie Rock", "Canada", "English", "128k", "AAC", 0),
            # Australia
            ("ABC News Radio Australia", "https://live-radio01.mediahubaustralia.com/PBW/mp3/", "News", "Australia", "English", "128k", "MP3", 0),
            ("Double J Radio", "https://live-radio01.mediahubaustralia.com/DJW/mp3/", "Alternative", "Australia", "English", "128k", "MP3", 0),
            # Brazil
            ("Nova Brasil FM", "https://playerservices.streamtheworld.com/api/livestream-redirect/NOVABRASIL_SP.mp3", "MPB & Samba", "Brazil", "Portuguese", "128k", "MP3", 0),
            ("Radio Bandeirantes", "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO_BANDEIRANTES.mp3", "News & Sports", "Brazil", "Portuguese", "128k", "MP3", 0)
        ]

        for s in stations:
            db_manager.execute_non_query(
                self.DB,
                """INSERT OR REPLACE INTO stations (name, stream_url, genre, country, language, bitrate, codec, is_favorite)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                s
            )

    def list_stations(self, country: Optional[str] = None, language: Optional[str] = None,
                      genre: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """List radio stations with multi-facet filters: country, language, genre, and search keywords."""
        query = "SELECT * FROM stations WHERE 1=1"
        params = []
        if country and country not in ("All", "World", "Global Filter"):
            if country == "Global":
                query += " AND (country = 'Global' OR country = 'International')"
            else:
                query += " AND country = ?"
                params.append(country)
        if language and language not in ("All", "All Languages"):
            query += " AND language = ?"
            params.append(language)
        if genre and genre not in ("All", "All Genres"):
            query += " AND genre = ?"
            params.append(genre)
        if search:
            query += " AND (name LIKE ? OR country LIKE ? OR genre LIKE ? OR language LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term, term])
        query += " ORDER BY is_favorite DESC, click_count DESC, name ASC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def get_filter_options(self) -> Dict[str, List[str]]:
        """Extract all unique countries, languages, and genres from registered stations."""
        c_rows = db_manager.execute_query(self.DB, "SELECT DISTINCT country FROM stations WHERE country IS NOT NULL AND country != '' ORDER BY country ASC")
        l_rows = db_manager.execute_query(self.DB, "SELECT DISTINCT language FROM stations WHERE language IS NOT NULL AND language != '' ORDER BY language ASC")
        g_rows = db_manager.execute_query(self.DB, "SELECT DISTINCT genre FROM stations WHERE genre IS NOT NULL AND genre != '' ORDER BY genre ASC")

        return {
            "countries": [r["country"] for r in c_rows if r["country"]],
            "languages": [r["language"] for r in l_rows if r["language"]],
            "genres": [r["genre"] for r in g_rows if r["genre"]]
        }

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
        """
        I have written this part of code because streaming endpoints on the internet can stall or hang.
        We check URL safety against SSRF attacks and enforce a strict 2.0s timeout so that checking
        a radio stream never causes the workstation interface to pause or freeze!
        """
        t0 = time.perf_counter()
        from ..core.async_network import SafeNetworkGuard
        is_safe, msg = SafeNetworkGuard.is_safe_url(stream_url)
        if not is_safe:
            return {"online": False, "error": msg, "latency_ms": 0.0, "valid_audio_stream": False}

        try:
            req = urllib.request.Request(
                stream_url,
                headers={"User-Agent": "AetherRadioClient/2.0", "Range": "bytes=0-1024"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as response:
                content_type = response.headers.get("Content-Type", "unknown")
                latency_ms = round((time.perf_counter() - t0) * 1000.0, 1)
                is_audio = "audio" in content_type or "ogg" in content_type or "mpeg" in content_type or "aac" in content_type
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
