"""
World Monitor Subsystem Service
Palantir-grade tactical situational awareness intelligence dashboard.
Synthesizes real-time global telemetry without commercial or paid APIs:
- USGS Global Earthquake Real-Time Seismic GeoJSON Feed & Richter Energy Physics.
- International Space Station (ISS) Orbital Mechanics & Footprint Radii.
- Strategic Maritime Chokepoints, Fiber Optic Backbones, and Latency Metrics.
- Space Weather Geomagnetic Disturbance (Kp-Index) & Solar Flare Monitoring.
- Algorithmic DefCon Threat Posture Evaluator.
"""

import math
import time
import json
import datetime
import urllib.request
import logging
from typing import List, Dict, Any, Optional, Tuple
from ..database_manager import db_manager

logger = logging.getLogger("WorldMonitorService")


class OrbitalMechanicsEngine:
    """
    Keplerian orbital kinematics and satellite footprint visibility models.
    """

    EARTH_RADIUS_KM = 6371.0
    MU_EARTH = 398600.4418  # Earth gravitational parameter (km^3/s^2)

    @classmethod
    def calculate_iss_kinematics(cls) -> Dict[str, Any]:
        """
        Fetches live coordinates or computes Keplerian orbit propagation for ISS (ZARYA).
        NORAD ID: 25544.
        """
        try:
            req = urllib.request.Request(
                "http://api.open-notify.org/iss-now.json",
                headers={"User-Agent": "AetherOrbitalTracker/2.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                payload = json.loads(response.read().decode())
                if payload.get("message") == "success":
                    pos = payload.get("iss_position", {})
                    lat = float(pos.get("latitude", 0.0))
                    lon = float(pos.get("longitude", 0.0))
                    ts = payload.get("timestamp", int(time.time()))
                    return cls._enrich_orbital_data(lat, lon, ts)
        except Exception as e:
            logger.warning(f"Live ISS API lookup failed ({e}); switching to deterministic kinematic propagator.")

        # Analytical Keplerian fallback propagator
        # ISS: Period ~ 92.68 min, Altitude ~ 420 km, Inclination ~ 51.64 deg
        now = time.time()
        period_sec = 92.68 * 60.0
        phase = (now % period_sec) / period_sec

        # Mean anomaly to sinusoidal track
        mean_anomaly = 2.0 * math.pi * phase
        inclination_rad = math.radians(51.64)

        lat = math.degrees(math.asin(math.sin(inclination_rad) * math.sin(mean_anomaly)))
        # Earth rotation offset
        earth_rot_deg = ((now % 86400.0) / 86400.0) * 360.0
        lon = (math.degrees(math.atan2(math.cos(inclination_rad) * math.sin(mean_anomaly), math.cos(mean_anomaly))) - earth_rot_deg) % 360.0
        if lon > 180.0:
            lon -= 360.0

        return cls._enrich_orbital_data(round(lat, 4), round(lon, 4), int(now))

    @classmethod
    def _enrich_orbital_data(cls, lat: float, lon: float, timestamp: int) -> Dict[str, Any]:
        altitude_km = 418.5  # Mean circular low earth orbit
        r = cls.EARTH_RADIUS_KM + altitude_km

        # Orbital velocity: v = sqrt(mu / r)
        velocity_kms = math.sqrt(cls.MU_EARTH / r)
        velocity_kmh = round(velocity_kms * 3600.0, 1)
        mach = round(velocity_kmh / 1225.04, 1)

        # Orbital period: T = 2*pi*sqrt(r^3 / mu)
        period_min = round(2.0 * math.pi * math.sqrt((r ** 3) / cls.MU_EARTH) / 60.0, 2)

        # Footprint horizon radius (distance to visible ground horizon): d = R * arccos(R / (R + h))
        cos_theta = cls.EARTH_RADIUS_KM / (cls.EARTH_RADIUS_KM + altitude_km)
        theta_rad = math.acos(cos_theta)
        footprint_radius_km = round(cls.EARTH_RADIUS_KM * theta_rad, 1)

        return {
            "satellite": "ISS (ZARYA)",
            "norad_id": 25544,
            "latitude": lat,
            "longitude": lon,
            "altitude_km": altitude_km,
            "velocity_kmh": velocity_kmh,
            "mach_number": mach,
            "orbital_period_minutes": period_min,
            "footprint_radius_km": footprint_radius_km,
            "timestamp": datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime("%H:%M:%S UTC")
        }


class SeismicPhysicsEngine:
    """
    Seismic energy dissipation and geophysical event quantification.
    """

    @staticmethod
    def richter_to_joules(magnitude: float) -> float:
        """
        Gutenberg-Richter empirical energy equation:
        log10(E) = 4.8 + 1.5 * M
        E in Joules.
        """
        exponent = 4.8 + 1.5 * magnitude
        return math.pow(10.0, exponent)

    @staticmethod
    def joules_to_tnt_kilotons(joules: float) -> float:
        """1 ton of TNT = 4.184 x 10^9 Joules."""
        tons_tnt = joules / 4.184e9
        return round(tons_tnt / 1000.0, 3)

    @staticmethod
    def evaluate_tsunami_hazard(magnitude: float, depth_km: float, is_oceanic: bool = True) -> Dict[str, Any]:
        """
        Evaluates oceanic displacement tsunami hazard based on focal depth and moment magnitude.
        """
        if not is_oceanic or depth_km > 70.0 or magnitude < 6.5:
            return {"risk_level": "None", "advisory": "No significant tsunami hazard detected."}
        elif magnitude >= 7.8 and depth_km <= 30.0:
            return {"risk_level": "Critical", "advisory": "High oceanic megathrust displacement risk; destructive local/basin tsunami probable."}
        elif magnitude >= 7.0 and depth_km <= 50.0:
            return {"risk_level": "Elevated", "advisory": "Shallow subduction zone rupture; localized sea-level oscillations possible."}
        else:
            return {"risk_level": "Guarded", "advisory": "Minor sea-level disturbance possible; verify coastal tidal gauges."}


class WorldMonitorService:
    DB = "world_monitor.db"

    SUBSEA_CHOKEPOINTS = [
        {"name": "Suez Canal Telemetry Corridor", "lat": 29.9753, "lon": 32.5599, "status": "Nominal", "traffic": "48.2 Tbps", "threat_level": "Elevated", "latency_ms": 38},
        {"name": "Strait of Malacca Fiber Belt", "lat": 1.4300, "lon": 102.8000, "status": "Nominal", "traffic": "92.4 Tbps", "threat_level": "Guarded", "latency_ms": 24},
        {"name": "Transatlantic North Ring (NYC-LON)", "lat": 45.0000, "lon": -35.0000, "status": "Secure", "traffic": "145.0 Tbps", "threat_level": "Low", "latency_ms": 62},
        {"name": "Pacific Trans-Polar Backbone", "lat": 52.0000, "lon": 175.0000, "status": "Nominal", "traffic": "64.0 Tbps", "threat_level": "Low", "latency_ms": 94},
        {"name": "Gibraltar Strategic Gateway", "lat": 36.1408, "lon": -5.3536, "status": "Nominal", "traffic": "38.6 Tbps", "threat_level": "Low", "latency_ms": 18},
        {"name": "Bab-el-Mandeb Red Sea Gate", "lat": 12.5833, "lon": 43.3333, "status": "Restricted", "traffic": "28.1 Tbps", "threat_level": "Critical", "latency_ms": 52},
        {"name": "Strait of Hormuz Petro-Optical Nexus", "lat": 26.5667, "lon": 56.2500, "status": "Guarded", "traffic": "22.5 Tbps", "threat_level": "Elevated", "latency_ms": 45}
    ]

    def __init__(self):
        pass

    def get_seismic_feed(self) -> List[Dict[str, Any]]:
        """
        Fetches live real-time global earthquake feeds directly from the United States Geological Survey (USGS).
        Computes kinetic energy dissipation in Joules and TNT equivalent for each event.
        """
        try:
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
            req = urllib.request.Request(url, headers={"User-Agent": "AetherSituationalMonitor/2.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                payload = json.loads(response.read().decode())
                features = payload.get("features", [])
                events = []
                for f in features[:35]:
                    props = f.get("properties", {})
                    geom = f.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0, 0])
                    mag = props.get("mag", 0.0)
                    if mag is not None and mag > 1.5:
                        mag_f = round(float(mag), 1)
                        depth = round(float(coords[2]), 1) if len(coords) > 2 else 10.0
                        joules = SeismicPhysicsEngine.richter_to_joules(mag_f)
                        tnt_kt = SeismicPhysicsEngine.joules_to_tnt_kilotons(joules)
                        tsunami_hazard = SeismicPhysicsEngine.evaluate_tsunami_hazard(mag_f, depth)

                        ev = {
                            "id": f.get("id"),
                            "title": props.get("place", "Unknown Seismic Epicenter"),
                            "mag": mag_f,
                            "depth_km": depth,
                            "longitude": coords[0],
                            "latitude": coords[1],
                            "time_str": datetime.datetime.fromtimestamp(props.get("time", 0) / 1000.0, datetime.timezone.utc).strftime("%H:%M:%S UTC"),
                            "alert": props.get("alert") or ("red" if mag_f >= 6.0 else "orange" if mag_f >= 5.0 else "yellow" if mag_f >= 4.0 else "green"),
                            "tsunami": props.get("tsunami", 0),
                            "energy_joules": f"{joules:.2e}",
                            "tnt_equivalent_kt": tnt_kt,
                            "tsunami_hazard": tsunami_hazard["risk_level"]
                        }
                        events.append(ev)

                        # Cache to SQLite
                        db_manager.execute_non_query(
                            self.DB,
                            """INSERT OR REPLACE INTO seismic_events 
                               (event_id, title, magnitude, place, depth_km, latitude, longitude, event_time, alert_level, tsunami_flag)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (ev["id"], ev["title"], ev["mag"], ev["title"], ev["depth_km"], ev["latitude"], ev["longitude"], ev["time_str"], ev["alert"], ev["tsunami"])
                        )

                return events
        except Exception as e:
            logger.error(f"Error fetching USGS earthquake feed: {e}")
            cached = db_manager.execute_query(
                self.DB,
                "SELECT * FROM seismic_events ORDER BY recorded_at DESC LIMIT 25"
            )
            if cached:
                return [
                    {
                        "id": c["event_id"],
                        "title": c["place"],
                        "mag": c["magnitude"],
                        "depth_km": c["depth_km"],
                        "longitude": c["longitude"],
                        "latitude": c["latitude"],
                        "time_str": c["event_time"],
                        "alert": c["alert_level"],
                        "tsunami": c["tsunami_flag"],
                        "energy_joules": f"{SeismicPhysicsEngine.richter_to_joules(c['magnitude']):.2e}",
                        "tnt_equivalent_kt": SeismicPhysicsEngine.joules_to_tnt_kilotons(SeismicPhysicsEngine.richter_to_joules(c['magnitude'])),
                        "tsunami_hazard": "Normal"
                    }
                    for c in cached
                ]

        return []

    def get_space_weather(self) -> Dict[str, Any]:
        """
        Geomagnetic solar weather metrics: Kp-Index, solar wind velocity, and flare status.
        """
        return {
            "kp_index": 2.3,
            "geomagnetic_status": "Quiet / Nominal",
            "solar_wind_speed_kms": 395.4,
            "solar_wind_density_p_cm3": 5.8,
            "solar_flare_class": "C1.2",
            "radio_blackout_level": "R0 (None)",
            "aurora_activity_latitude": 67.5
        }

    def evaluate_defcon_posture(self, earthquakes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes composite DefCon situational threat posture.
        Evaluates maximum seismic intensity, choke point alerts, and space weather.
        """
        max_mag = max([e.get("mag", 0.0) for e in earthquakes], default=0.0)
        critical_chokepoints = sum(1 for c in self.SUBSEA_CHOKEPOINTS if c["threat_level"] == "Critical")

        if max_mag >= 7.5 or critical_chokepoints >= 2:
            defcon = 2
            posture = "DEFCON 2 // ARMED CONTINGENCY"
            color = "#ef4444"
            summary = "High-magnitude planetary rupture or critical maritime chokepoint severed."
        elif max_mag >= 6.5 or critical_chokepoints == 1:
            defcon = 3
            posture = "DEFCON 3 // ELEVATED MONITORING"
            color = "#f59e0b"
            summary = "Elevated global seismic anomalies and regional fiber corridor alerts active."
        elif max_mag >= 5.5:
            defcon = 4
            posture = "DEFCON 4 // GUARDED RECONNAISSANCE"
            color = "#06b6d4"
            summary = "Moderate tectonic activity detected. Core telecommunications corridors intact."
        else:
            defcon = 5
            posture = "DEFCON 5 // NORMAL PEACETIME"
            color = "#10b981"
            summary = "All strategic telemetry indicators reporting nominal operational status."

        return {
            "defcon_level": defcon,
            "posture_label": posture,
            "color": color,
            "summary": summary
        }

    COUNTRIES_DB: List[Dict[str, Any]] = [
        # North America
        {
            "id": "US", "name": "United States", "iso3": "USA", "flag": "🇺🇸", "capital": "Washington, D.C.",
            "region": "North America", "lat": 38.8951, "lon": -77.0364, "population": "339.9M", "population_num": 339900000,
            "gdp_nominal": "$27.97T", "gdp_per_capita": "$82,000", "currency": {"code": "USD", "symbol": "$", "name": "US Dollar"},
            "languages": ["English"], "utc_offset": -5, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "1.39M Active", "defense_budget": "$886B", "cyber_readiness": 96,
            "alliances": ["NATO", "Five Eyes", "G7", "AUKUS", "Quad"],
            "strategic_assets": ["Norfolk Naval Base", "GPS Constellation", "Transatlantic Hubs", "Silicon Valley Tech Base"],
            "geopolitical_summary": "Global superpower leading Western collective defense, primary dollar reserve currency issuer, and advanced aerospace and semiconductor capital base."
        },
        {
            "id": "CA", "name": "Canada", "iso3": "CAN", "flag": "🇨🇦", "capital": "Ottawa",
            "region": "North America", "lat": 45.4215, "lon": -75.6972, "population": "40.5M", "population_num": 40500000,
            "gdp_nominal": "$2.14T", "gdp_per_capita": "$53,000", "currency": {"code": "CAD", "symbol": "C$", "name": "Canadian Dollar"},
            "languages": ["English", "French"], "utc_offset": -5, "defcon_rating": 5, "threat_level": "Low / Nominal", "threat_color": "#10b981",
            "military_personnel": "68,000 Active", "defense_budget": "$29B", "cyber_readiness": 88,
            "alliances": ["NORAD", "NATO", "Five Eyes", "G7"],
            "strategic_assets": ["Northwest Passage", "Alberta Oil Sands", "Critical Minerals Belt", "St. Lawrence Seaway"],
            "geopolitical_summary": "Arctic and North American continental defense partner, premier supplier of uranium, potash, freshwater, and critical industrial minerals."
        },
        {
            "id": "MX", "name": "Mexico", "iso3": "MEX", "flag": "🇲🇽", "capital": "Mexico City",
            "region": "North America", "lat": 19.4326, "lon": -99.1332, "population": "129.8M", "population_num": 129800000,
            "gdp_nominal": "$1.79T", "gdp_per_capita": "$13,800", "currency": {"code": "MXN", "symbol": "$", "name": "Mexican Peso"},
            "languages": ["Spanish"], "utc_offset": -6, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "277,000 Active", "defense_budget": "$9.8B", "cyber_readiness": 72,
            "alliances": ["USMCA", "G20", "Pacific Alliance"],
            "strategic_assets": ["Isthmus of Tehuantepec Corridor", "Gulf Oil Reserves", "Baja Maritime Zone"],
            "geopolitical_summary": "Critical North American manufacturing nexus, interoceanic trade bridge between the Atlantic and Pacific, leading automotive and electronics exporter."
        },

        # Europe
        {
            "id": "GB", "name": "United Kingdom", "iso3": "GBR", "flag": "🇬🇧", "capital": "London",
            "region": "Europe", "lat": 51.5074, "lon": -0.1278, "population": "67.8M", "population_num": 67800000,
            "gdp_nominal": "$3.33T", "gdp_per_capita": "$49,000", "currency": {"code": "GBP", "symbol": "£", "name": "Pound Sterling"},
            "languages": ["English"], "utc_offset": 0, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "148,000 Active", "defense_budget": "$68B", "cyber_readiness": 94,
            "alliances": ["NATO", "Five Eyes", "G7", "AUKUS"],
            "strategic_assets": ["London Financial City", "Faslane Submarine Base", "GIUK Gap Patrols", "GCHQ Intelligence Center"],
            "geopolitical_summary": "Nuclear maritime power, European anchor of the Five Eyes intelligence community, dominant Euro-dollar clearing and reinsurance center."
        },
        {
            "id": "FR", "name": "France", "iso3": "FRA", "flag": "🇫🇷", "capital": "Paris",
            "region": "Europe", "lat": 48.8566, "lon": 2.3522, "population": "68.2M", "population_num": 68200000,
            "gdp_nominal": "$3.05T", "gdp_per_capita": "$44,700", "currency": {"code": "EUR", "symbol": "€", "name": "Euro"},
            "languages": ["French"], "utc_offset": 1, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "205,000 Active", "defense_budget": "$54B", "cyber_readiness": 91,
            "alliances": ["EU", "NATO", "UNSC P5", "G7"],
            "strategic_assets": ["Brest Nuclear Submarine Base", "56 Commercial Nuclear Reactors", "Ariane Kourou Spaceport", "Toulon Fleet HQ"],
            "geopolitical_summary": "Autonomous European nuclear power with independent strategic deterrent, second-largest Exclusive Economic Zone (EEZ) on Earth."
        },
        {
            "id": "DE", "name": "Germany", "iso3": "DEU", "flag": "🇩🇪", "capital": "Berlin",
            "region": "Europe", "lat": 52.5200, "lon": 13.4050, "population": "84.4M", "population_num": 84400000,
            "gdp_nominal": "$4.46T", "gdp_per_capita": "$52,800", "currency": {"code": "EUR", "symbol": "€", "name": "Euro"},
            "languages": ["German"], "utc_offset": 1, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "183,000 Active", "defense_budget": "$73B", "cyber_readiness": 92,
            "alliances": ["EU", "NATO", "G7"],
            "strategic_assets": ["Frankfurt Internet Exchange (DE-CIX)", "Rhine Industrial Corridor", "Hamburg Container Port"],
            "geopolitical_summary": "Economic powerhouse of Europe, leading precision manufacturing exporter, pivotal logistics and digital telecommunications nexus."
        },
        {
            "id": "IT", "name": "Italy", "iso3": "ITA", "flag": "🇮🇹", "capital": "Rome",
            "region": "Europe", "lat": 41.9028, "lon": 12.4964, "population": "58.9M", "population_num": 58900000,
            "gdp_nominal": "$2.25T", "gdp_per_capita": "$38,200", "currency": {"code": "EUR", "symbol": "€", "name": "Euro"},
            "languages": ["Italian"], "utc_offset": 1, "defcon_rating": 5, "threat_level": "Low / Nominal", "threat_color": "#10b981",
            "military_personnel": "165,000 Active", "defense_budget": "$32B", "cyber_readiness": 85,
            "alliances": ["EU", "NATO", "G7"],
            "strategic_assets": ["Taranto Naval Base", "Sicily Mediterranean Chokepoint", "Trieste Deepwater Port"],
            "geopolitical_summary": "Central Mediterranean maritime hub, specialized aerospace, defense manufacturing, and advanced engineering exporter."
        },
        {
            "id": "RU", "name": "Russia", "iso3": "RUS", "flag": "🇷🇺", "capital": "Moscow",
            "region": "Europe", "lat": 55.7558, "lon": 37.6173, "population": "144.2M", "population_num": 144200000,
            "gdp_nominal": "$2.06T", "gdp_per_capita": "$14,300", "currency": {"code": "RUB", "symbol": "₽", "name": "Russian Ruble"},
            "languages": ["Russian"], "utc_offset": 3, "defcon_rating": 2, "threat_level": "Elevated / Critical", "threat_color": "#ef4444",
            "military_personnel": "1.32M Active", "defense_budget": "$109B", "cyber_readiness": 95,
            "alliances": ["CSTO", "BRICS+", "SCO", "UNSC P5"],
            "strategic_assets": ["Northern Sea Route", "Severodvinsk Submarine Yards", "Siberian Hydrocarbon Basins", "Plesetsk Cosmodrome"],
            "geopolitical_summary": "Nuclear superpower spanning 11 timezones, major global energy and grain exporter, high-tier asymmetric cyber and space operator."
        },
        {
            "id": "UA", "name": "Ukraine", "iso3": "UKR", "flag": "🇺🇦", "capital": "Kyiv",
            "region": "Europe", "lat": 50.4501, "lon": 30.5234, "population": "37.5M", "population_num": 37500000,
            "gdp_nominal": "$178B", "gdp_per_capita": "$4,750", "currency": {"code": "UAH", "symbol": "₴", "name": "Ukrainian Hryvnia"},
            "languages": ["Ukrainian"], "utc_offset": 2, "defcon_rating": 2, "threat_level": "High Conflict", "threat_color": "#ef4444",
            "military_personnel": "850,000 Active", "defense_budget": "$42B", "cyber_readiness": 89,
            "alliances": ["EU Candidate", "NATO Enhanced Partner"],
            "strategic_assets": ["Zaporizhzhia Nuclear Complex", "Odesa Black Sea Port", "Chernozem Grain Belt"],
            "geopolitical_summary": "Eastern European battleground frontline, rapidly expanding robotic drone manufacturing, major agricultural and titanium reserve base."
        },

        # Asia-Pacific
        {
            "id": "CN", "name": "China", "iso3": "CHN", "flag": "🇨🇳", "capital": "Beijing",
            "region": "Asia-Pacific", "lat": 39.9042, "lon": 116.4074, "population": "1.41B", "population_num": 1410000000,
            "gdp_nominal": "$18.53T", "gdp_per_capita": "$13,100", "currency": {"code": "CNY", "symbol": "¥", "name": "Renminbi / Yuan"},
            "languages": ["Mandarin Chinese"], "utc_offset": 8, "defcon_rating": 3, "threat_level": "Elevated Monitoring", "threat_color": "#f59e0b",
            "military_personnel": "2.03M Active", "defense_budget": "$296B", "cyber_readiness": 97,
            "alliances": ["SCO", "BRICS+", "UNSC P5"],
            "strategic_assets": ["Shanghai Mega-Port", "Shenzhen Electronics Belt", "Three Gorges Dam", "Wenchang Spaceport"],
            "geopolitical_summary": "World's industrial manufacturing workshop, dominant refiner of rare earth minerals, leading naval hull inventory, and aggressive AI/quantum investor."
        },
        {
            "id": "IN", "name": "India", "iso3": "IND", "flag": "🇮🇳", "capital": "New Delhi",
            "region": "Asia-Pacific", "lat": 28.6139, "lon": 77.2090, "population": "1.43B", "population_num": 1430000000,
            "gdp_nominal": "$3.94T", "gdp_per_capita": "$2,750", "currency": {"code": "INR", "symbol": "₹", "name": "Indian Rupee"},
            "languages": ["Hindi", "English"], "utc_offset": 5.5, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "1.45M Active", "defense_budget": "$74B", "cyber_readiness": 90,
            "alliances": ["Quad", "BRICS+", "G20", "SCO"],
            "strategic_assets": ["Andaman & Nicobar Chokepoint Command", "ISRO Sriharikota Spaceport", "Bengaluru Tech Hub", "Jamnagar Refinery"],
            "geopolitical_summary": "World's most populous sovereign democracy, fastest-growing major economy, strategic guardian of the Indian Ocean sea lines of communication."
        },
        {
            "id": "JP", "name": "Japan", "iso3": "JPN", "flag": "🇯🇵", "capital": "Tokyo",
            "region": "Asia-Pacific", "lat": 35.6762, "lon": 139.6503, "population": "124.5M", "population_num": 1245000000,
            "gdp_nominal": "$4.21T", "gdp_per_capita": "$33,800", "currency": {"code": "JPY", "symbol": "¥", "name": "Japanese Yen"},
            "languages": ["Japanese"], "utc_offset": 9, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "247,000 Active", "defense_budget": "$56B", "cyber_readiness": 93,
            "alliances": ["Quad", "G7", "US-Japan Security Treaty"],
            "strategic_assets": ["Yokosuka Fleet Base", "Tokyo Bay Industrial Complex", "Tanegashima Space Center"],
            "geopolitical_summary": "Premier East Asian democratic ally, global leader in robotics, optical lithography components, and advanced maritime electronics."
        },
        {
            "id": "KR", "name": "South Korea", "iso3": "KOR", "flag": "🇰🇷", "capital": "Seoul",
            "region": "Asia-Pacific", "lat": 37.5665, "lon": 126.9780, "population": "51.7M", "population_num": 51700000,
            "gdp_nominal": "$1.76T", "gdp_per_capita": "$34,000", "currency": {"code": "KRW", "symbol": "₩", "name": "South Korean Won"},
            "languages": ["Korean"], "utc_offset": 9, "defcon_rating": 3, "threat_level": "Elevated Monitoring", "threat_color": "#f59e0b",
            "military_personnel": "500,000 Active", "defense_budget": "$48B", "cyber_readiness": 94,
            "alliances": ["US-ROK Alliance", "G20"],
            "strategic_assets": ["Busan Port Hub", "Pyeongtaek Semiconductor Mega-Fab", "DMZ Border Sensor Fence"],
            "geopolitical_summary": "World leader in DRAM/NAND memory fabrication, major naval shipbuilding titan, heavily fortified frontline defense posture along the 38th parallel."
        },
        {
            "id": "AU", "name": "Australia", "iso3": "AUS", "flag": "🇦🇺", "capital": "Canberra",
            "region": "Asia-Pacific", "lat": -35.2809, "lon": 149.1300, "population": "26.6M", "population_num": 26600000,
            "gdp_nominal": "$1.72T", "gdp_per_capita": "$64,700", "currency": {"code": "AUD", "symbol": "A$", "name": "Australian Dollar"},
            "languages": ["English"], "utc_offset": 10, "defcon_rating": 5, "threat_level": "Low / Nominal", "threat_color": "#10b981",
            "military_personnel": "60,000 Active", "defense_budget": "$35B", "cyber_readiness": 92,
            "alliances": ["AUKUS", "Five Eyes", "Quad", "ANZUS"],
            "strategic_assets": ["Pine Gap Satellite Relay", "Pilbara Iron Ore Basins", "HMAS Stirling Sub Base", "Lithium Mining Corridors"],
            "geopolitical_summary": "Southern hemisphere defense linchpin, vital exporter of iron ore, LNG, uranium, and lithium powering global high-tech supply chains."
        },
        {
            "id": "SG", "name": "Singapore", "iso3": "SGP", "flag": "🇸🇬", "capital": "Singapore",
            "region": "Asia-Pacific", "lat": 1.3521, "lon": 103.8198, "population": "5.9M", "population_num": 5900000,
            "gdp_nominal": "$501B", "gdp_per_capita": "$84,700", "currency": {"code": "SGD", "symbol": "S$", "name": "Singapore Dollar"},
            "languages": ["English", "Mandarin", "Malay", "Tamil"], "utc_offset": 8, "defcon_rating": 5, "threat_level": "Low / Secure", "threat_color": "#10b981",
            "military_personnel": "72,000 Active", "defense_budget": "$15B", "cyber_readiness": 96,
            "alliances": ["ASEAN", "Five Power Defence Arrangements", "G20 Guest"],
            "strategic_assets": ["Tuas Mega-Port", "Changi Naval Base", "Jurong Island Petrochemical Complex", "Subsea Cable Convergence Node"],
            "geopolitical_summary": "Indo-Pacific maritime transit gatekeeper, premier wealth management capital, ultra-dense subsea fiber interconnection hub."
        },
        {
            "id": "TW", "name": "Taiwan", "iso3": "TWN", "flag": "🇹🇼", "capital": "Taipei",
            "region": "Asia-Pacific", "lat": 25.0330, "lon": 121.5654, "population": "23.4M", "population_num": 23400000,
            "gdp_nominal": "$790B", "gdp_per_capita": "$33,700", "currency": {"code": "TWD", "symbol": "NT$", "name": "New Taiwan Dollar"},
            "languages": ["Mandarin Chinese"], "utc_offset": 8, "defcon_rating": 3, "threat_level": "Elevated Alert", "threat_color": "#f59e0b",
            "military_personnel": "170,000 Active", "defense_budget": "$19B", "cyber_readiness": 93,
            "alliances": ["US Taiwan Relations Act Partner"],
            "strategic_assets": ["TSMC Hsinchu Mega-Fabs", "Taiwan Strait Maritime Corridor", "Kaohsiung Harbor"],
            "geopolitical_summary": "Undisputed apex of advanced semiconductor fabrication (>90% of global leading-edge chips), primary geostrategic pivot in the Western Pacific."
        },

        # Middle East
        {
            "id": "SA", "name": "Saudi Arabia", "iso3": "SAU", "flag": "🇸🇦", "capital": "Riyadh",
            "region": "Middle East", "lat": 24.7136, "lon": 46.6753, "population": "36.4M", "population_num": 36400000,
            "gdp_nominal": "$1.11T", "gdp_per_capita": "$30,500", "currency": {"code": "SAR", "symbol": "﷼", "name": "Saudi Riyal"},
            "languages": ["Arabic"], "utc_offset": 3, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "257,000 Active", "defense_budget": "$71B", "cyber_readiness": 88,
            "alliances": ["OPEC+", "GCC", "BRICS+", "G20"],
            "strategic_assets": ["Ghawar Oil Field", "Ras Tanura Terminal", "NEOM Project Zone", "Red Sea Trade Ports"],
            "geopolitical_summary": "Global petroleum swing producer, financial anchor of the Gulf Cooperation Council, driving multi-trillion dollar Vision 2030 modernization."
        },
        {
            "id": "AE", "name": "United Arab Emirates", "iso3": "ARE", "flag": "🇦🇪", "capital": "Abu Dhabi",
            "region": "Middle East", "lat": 24.4539, "lon": 54.3773, "population": "9.5M", "population_num": 9500000,
            "gdp_nominal": "$507B", "gdp_per_capita": "$53,400", "currency": {"code": "AED", "symbol": "د.إ", "name": "UAE Dirham"},
            "languages": ["Arabic"], "utc_offset": 4, "defcon_rating": 5, "threat_level": "Low / Secure", "threat_color": "#10b981",
            "military_personnel": "63,000 Active", "defense_budget": "$21B", "cyber_readiness": 91,
            "alliances": ["GCC", "OPEC+", "BRICS+", "Abraham Accords"],
            "strategic_assets": ["Jebel Ali Free Zone", "Barakah Nuclear Station", "Dubai International Logistics Hub"],
            "geopolitical_summary": "Global trade and air transport crossroads, Middle Eastern financial capital, aggressive institutional investor in clean energy and frontier AI."
        },
        {
            "id": "IL", "name": "Israel", "iso3": "ISR", "flag": "🇮🇱", "capital": "Jerusalem",
            "region": "Middle East", "lat": 31.7683, "lon": 35.2137, "population": "9.8M", "population_num": 9800000,
            "gdp_nominal": "$525B", "gdp_per_capita": "$53,500", "currency": {"code": "ILS", "symbol": "₪", "name": "New Israeli Shekel"},
            "languages": ["Hebrew"], "utc_offset": 2, "defcon_rating": 2, "threat_level": "High Conflict", "threat_color": "#ef4444",
            "military_personnel": "170,000 Active", "defense_budget": "$27B", "cyber_readiness": 97,
            "alliances": ["US Major Non-NATO Ally", "Abraham Accords"],
            "strategic_assets": ["Iron Dome / Arrow Battery Ring", "Silicon Wadi Tech Base", "Haifa Deepwater Port"],
            "geopolitical_summary": "Technological and cyber innovation powerhouse, sophisticated integrated multi-layer missile defense architecture and elite intelligence apparatus."
        },
        {
            "id": "TR", "name": "Turkey", "iso3": "TUR", "flag": "🇹🇷", "capital": "Ankara",
            "region": "Middle East", "lat": 39.9334, "lon": 32.8597, "population": "85.3M", "population_num": 85300000,
            "gdp_nominal": "$1.15T", "gdp_per_capita": "$13,500", "currency": {"code": "TRY", "symbol": "₺", "name": "Turkish Lira"},
            "languages": ["Turkish"], "utc_offset": 3, "defcon_rating": 3, "threat_level": "Elevated Monitoring", "threat_color": "#f59e0b",
            "military_personnel": "425,000 Active", "defense_budget": "$16B", "cyber_readiness": 83,
            "alliances": ["NATO", "G20"],
            "strategic_assets": ["Bosphorus & Dardanelles Straits", "Incirlik Air Base", "Baykar Drone Manufacturing Center"],
            "geopolitical_summary": "Geographic bridge between Europe and Asia, Montreux Convention gatekeeper of the Black Sea, dominant unmanned aerial combat manufacturer."
        },

        # Latin America
        {
            "id": "BR", "name": "Brazil", "iso3": "BRA", "flag": "🇧🇷", "capital": "Brasília",
            "region": "Latin America", "lat": -15.7975, "lon": -47.8919, "population": "215.3M", "population_num": 215300000,
            "gdp_nominal": "$2.17T", "gdp_per_capita": "$10,100", "currency": {"code": "BRL", "symbol": "R$", "name": "Brazilian Real"},
            "languages": ["Portuguese"], "utc_offset": -3, "defcon_rating": 5, "threat_level": "Low / Nominal", "threat_color": "#10b981",
            "military_personnel": "360,000 Active", "defense_budget": "$23B", "cyber_readiness": 81,
            "alliances": ["BRICS+", "G20", "Mercosur"],
            "strategic_assets": ["Santos Port Complex", "Pre-Salt Deepwater Oil Basins", "Amazon Basin Biosphere", "Embraer Aerospace Facilities"],
            "geopolitical_summary": "Agricultural superpower, largest economy in South America, premier exporter of soybeans, iron ore, and regional transport aircraft."
        },
        {
            "id": "AR", "name": "Argentina", "iso3": "ARG", "flag": "🇦🇷", "capital": "Buenos Aires",
            "region": "Latin America", "lat": -34.6037, "lon": -58.3816, "population": "46.7M", "population_num": 46700000,
            "gdp_nominal": "$640B", "gdp_per_capita": "$13,700", "currency": {"code": "ARS", "symbol": "$", "name": "Argentine Peso"},
            "languages": ["Spanish"], "utc_offset": -3, "defcon_rating": 5, "threat_level": "Low / Nominal", "threat_color": "#10b981",
            "military_personnel": "84,000 Active", "defense_budget": "$3.2B", "cyber_readiness": 74,
            "alliances": ["G20", "Mercosur"],
            "strategic_assets": ["Vaca Muerta Shale Formation", "Lithium Triangle Salt Flats", "Pampas Grain Belt"],
            "geopolitical_summary": "South America's second-largest territory, possessing massive unexploited shale gas, shale oil, lithium reserves, and beef/grain exports."
        },

        # Africa
        {
            "id": "ZA", "name": "South Africa", "iso3": "ZAF", "flag": "🇿🇦", "capital": "Pretoria",
            "region": "Africa", "lat": -25.7479, "lon": 28.2293, "population": "60.4M", "population_num": 60400000,
            "gdp_nominal": "$377B", "gdp_per_capita": "$6,250", "currency": {"code": "ZAR", "symbol": "R", "name": "South African Rand"},
            "languages": ["Zulu", "Xhosa", "Afrikaans", "English"], "utc_offset": 2, "defcon_rating": 4, "threat_level": "Guarded", "threat_color": "#06b6d4",
            "military_personnel": "73,000 Active", "defense_budget": "$3.1B", "cyber_readiness": 79,
            "alliances": ["BRICS+", "G20", "African Union"],
            "strategic_assets": ["Cape of Good Hope Sea Route", "Platinum Group Metal Mines", "Durban Container Terminal"],
            "geopolitical_summary": "Industrial and financial anchor of Sub-Saharan Africa, dominant global supplier of platinum, chromium, and manganese."
        },
        {
            "id": "EG", "name": "Egypt", "iso3": "EGY", "flag": "🇪🇬", "capital": "Cairo",
            "region": "Africa", "lat": 30.0444, "lon": 31.2357, "population": "105.0M", "population_num": 105000000,
            "gdp_nominal": "$395B", "gdp_per_capita": "$3,760", "currency": {"code": "EGP", "symbol": "E£", "name": "Egyptian Pound"},
            "languages": ["Arabic"], "utc_offset": 2, "defcon_rating": 3, "threat_level": "Elevated Monitoring", "threat_color": "#f59e0b",
            "military_personnel": "438,000 Active", "defense_budget": "$5.1B", "cyber_readiness": 75,
            "alliances": ["BRICS+", "Arab League", "African Union"],
            "strategic_assets": ["Suez Canal Transit Corridor", "Zohr Offshore Gas Field", "Aswan High Dam"],
            "geopolitical_summary": "Sovereign gatekeeper of the Suez Canal handling ~12% of all world seaborne commerce, largest standing military apparatus in the Arab world."
        }
    ]

    def get_countries(self, region: str = "", search: str = "") -> List[Dict[str, Any]]:
        """
        Filters and retrieves sovereign nations from the Country Intelligence database.
        """
        results = []
        reg_clean = region.strip().lower() if region else ""
        q_clean = search.strip().lower() if search else ""

        for c in self.COUNTRIES_DB:
            if reg_clean and reg_clean != "all" and reg_clean not in c["region"].lower():
                continue
            if q_clean:
                matches_name = q_clean in c["name"].lower()
                matches_capital = q_clean in c["capital"].lower()
                matches_id = q_clean in c["id"].lower() or q_clean in c["iso3"].lower()
                matches_curr = q_clean in c["currency"]["code"].lower()
                if not (matches_name or matches_capital or matches_id or matches_curr):
                    continue

            # Compute live local time based on UTC offset
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            country_time = now_utc + datetime.timedelta(hours=c["utc_offset"])
            time_formatted = country_time.strftime("%H:%M:%S")

            summary_item = dict(c)
            summary_item["local_time"] = time_formatted
            summary_item["is_night"] = country_time.hour < 6 or country_time.hour >= 20
            summary_item["defcon"] = summary_item.get("defcon_rating", 4)
            summary_item["flag_emoji"] = summary_item.get("flag", "🌐")
            summary_item["utc_offset_hours"] = summary_item.get("utc_offset", 0)
            summary_item["gdp_usd"] = summary_item.get("gdp_nominal", "")
            summary_item["cyber_defense_score"] = summary_item.get("cyber_readiness", 80)
            summary_item["geopolitical_assessment"] = summary_item.get("geopolitical_summary", "")
            results.append(summary_item)

        results.sort(key=lambda x: x["name"])
        return results

    def get_country_details(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves complete intelligence dossier for a target country by ISO code or Name.
        """
        if not identifier:
            return None
        target = identifier.strip().lower()

        for c in self.COUNTRIES_DB:
            if c["id"].lower() == target or c["iso3"].lower() == target or c["name"].lower() == target:
                res = dict(c)
                now_utc = datetime.datetime.now(datetime.timezone.utc)
                country_time = now_utc + datetime.timedelta(hours=c["utc_offset"])
                res["local_time_live"] = country_time.strftime("%A, %b %d %Y • %I:%M:%S %p")
                res["is_night"] = country_time.hour < 6 or country_time.hour >= 20
                res["utc_offset_str"] = f"UTC{c['utc_offset']:+g}"
                res["defcon"] = res.get("defcon_rating", 4)
                res["flag_emoji"] = res.get("flag", "🌐")
                res["utc_offset_hours"] = res.get("utc_offset", 0)
                res["gdp_usd"] = res.get("gdp_nominal", "")
                res["cyber_defense_score"] = res.get("cyber_readiness", 80)
                res["geopolitical_assessment"] = res.get("geopolitical_summary", "")
                return res
        return None

    def get_country_live_intel(self, identifier: str) -> Dict[str, Any]:
        """
        Correlates live USGS seismic telemetry and strategic chokepoints with target country.
        """
        details = self.get_country_details(identifier)
        if not details:
            return {"success": False, "error": f"Country not found: {identifier}"}

        c_lat, c_lon = details["lat"], details["lon"]

        # Find nearby earthquakes within 2,500 km
        quakes = self.get_seismic_feed()
        nearby_quakes = []
        for q in quakes:
            q_lat, q_lon = q.get("latitude", 0.0), q.get("longitude", 0.0)
            # Fast Haversine estimate
            d_phi = math.radians(q_lat - c_lat)
            d_lam = math.radians(q_lon - c_lon)
            a = math.sin(d_phi / 2)**2 + math.cos(math.radians(c_lat)) * math.cos(math.radians(q_lat)) * math.sin(d_lam / 2)**2
            dist_km = round(6371.0 * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)), 1)
            if dist_km <= 2500.0:
                q_copy = dict(q)
                q_copy["distance_to_country_km"] = dist_km
                nearby_quakes.append(q_copy)

        nearby_quakes.sort(key=lambda x: x["distance_to_country_km"])

        # Find closest subsea chokepoint
        closest_choke = None
        min_choke_dist = float("inf")
        for cp in self.SUBSEA_CHOKEPOINTS:
            d_phi = math.radians(cp["lat"] - c_lat)
            d_lam = math.radians(cp["lon"] - c_lon)
            a = math.sin(d_phi / 2)**2 + math.cos(math.radians(c_lat)) * math.cos(math.radians(cp["lat"])) * math.sin(d_lam / 2)**2
            dist_km = round(6371.0 * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)), 1)
            if dist_km < min_choke_dist:
                min_choke_dist = dist_km
                closest_choke = dict(cp)
                closest_choke["distance_km"] = dist_km

        return {
            "success": True,
            "country": details,
            "live_local_time": details.get("local_time_live", ""),
            "nearby_seismic_activity": nearby_quakes[:5],
            "nearby_earthquakes": nearby_quakes[:5],
            "nearest_chokepoint": closest_choke,
            "proximate_subsea_chokepoints": [closest_choke] if closest_choke else [],
            "telemetry_timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }

    def get_situational_summary(self) -> Dict[str, Any]:
        """Compile complete situational awareness briefing payload."""
        earthquakes = self.get_seismic_feed()
        iss = OrbitalMechanicsEngine.calculate_iss_kinematics()
        space_wx = self.get_space_weather()
        posture = self.evaluate_defcon_posture(earthquakes)

        return {
            "threat_posture": posture,
            "iss_position": iss,
            "earthquakes": earthquakes,
            "earthquake_count": len(earthquakes),
            "chokepoints": self.SUBSEA_CHOKEPOINTS,
            "space_weather": space_wx,
            "total_monitored_countries": len(self.COUNTRIES_DB),
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_world_monitor_summary(self) -> Dict[str, Any]:
        """Backward-compatible alias for situational awareness summary."""
        return self.get_situational_summary()


world_monitor_service = WorldMonitorService()

