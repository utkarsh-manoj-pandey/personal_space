"""
Maps and Navigation Subsystem Service
100% Free and open-source geospatial engine.
Integrates Leaflet vector mapping, OpenStreetMap & CartoDB Dark Matter tile layers,
OpenStreetMap Nominatim geocoding, and OSRM turn-by-turn navigation without proprietary API keys.
"""

import json
import urllib.request
import urllib.parse
import logging
from typing import List, Dict, Any, Optional
from ..database_manager import db_manager

logger = logging.getLogger("MapsService")


class MapsService:
    DB = "maps.db"

    def __init__(self):
        self._seed_default_waypoints()

    def _seed_default_waypoints(self):
        """Seed strategic global landmarks into maps database."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM saved_waypoints")
        if count and count[0]["count"] == 0:
            waypoints = [
                ("Svalbard Global Seed Vault", 78.2358, 15.4913, "Strategic Vault", "High security subterranean arctic vault."),
                ("CERN Large Hadron Collider", 46.2330, 6.0557, "Research Facility", "Particle physics research center."),
                ("KSC Launch Complex 39A", 28.6083, -80.6043, "Spaceport", "Primary orbital launch facility."),
                ("Strait of Gibraltar", 35.9647, -5.6022, "Maritime Choke", "Critical intercontinental shipping corridor."),
                ("Panama Canal Miraflores", 8.9972, -79.5916, "Maritime Choke", "Pacific-Atlantic transit lock system.")
            ]
            for name, lat, lon, cat, notes in waypoints:
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT OR IGNORE INTO saved_waypoints (name, latitude, longitude, category, notes)
                       VALUES (?, ?, ?, ?, ?)""",
                    (name, lat, lon, cat, notes)
                )

    def geocode(self, query: str) -> List[Dict[str, Any]]:
        """
        Geocodes query string using OpenStreetMap Nominatim free endpoint.
        Returns coordinates, display name, and bounding box.
        """
        try:
            encoded = urllib.parse.quote_plus(query.strip())
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded}&limit=5"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NexusWorkstationMaps/1.0 (offline-first-geospatial)"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                return [
                    {
                        "name": item.get("display_name"),
                        "latitude": float(item.get("lat")),
                        "longitude": float(item.get("lon")),
                        "type": item.get("type", "location")
                    }
                    for item in data
                ]
        except Exception as e:
            logger.error(f"Geocoding error for {query}: {e}")
            return []

    def calculate_route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Dict[str, Any]:
        """
        Computes driving route using Open Source Routing Machine (OSRM) public demo server.
        No API keys required. Returns distance (km), duration (mins), and full GeoJSON line geometry.
        """
        try:
            url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&steps=true"
            req = urllib.request.Request(url, headers={"User-Agent": "NexusWorkstationRouting/1.0"})
            with urllib.request.urlopen(req, timeout=8) as response:
                payload = json.loads(response.read().decode())
                if payload.get("code") == "Ok" and payload.get("routes"):
                    route = payload["routes"][0]
                    dist_km = round(route.get("distance", 0.0) / 1000.0, 2)
                    dur_mins = round(route.get("duration", 0.0) / 60.0, 1)
                    geojson = route.get("geometry", {})

                    steps = []
                    for leg in route.get("legs", []):
                        for step in leg.get("steps", []):
                            maneuver = step.get("maneuver", {})
                            instr = step.get("name", "") or maneuver.get("type", "Proceed")
                            steps.append({
                                "instruction": f"{maneuver.get('type', 'Proceed').capitalize()}: {instr}",
                                "distance_m": round(step.get("distance", 0)),
                                "duration_s": round(step.get("duration", 0))
                            })

                    return {
                        "success": True,
                        "distance_km": dist_km,
                        "duration_mins": dur_mins,
                        "geometry": geojson,
                        "steps": steps[:15]
                    }
        except Exception as e:
            logger.error(f"Routing computation error: {e}")

        # Fallback great-circle estimation if network is offline
        import math
        dlat = math.radians(end_lat - start_lat)
        dlon = math.radians(end_lon - start_lon)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        est_dist = round(6371 * c, 2)
        est_mins = round((est_dist / 80.0) * 60, 1)

        return {
            "success": True,
            "distance_km": est_dist,
            "duration_mins": est_mins,
            "geometry": {
                "type": "LineString",
                "coordinates": [[start_lon, start_lat], [end_lon, end_lat]]
            },
            "steps": [{"instruction": f"Direct route vector towards destination ({est_dist} km)", "distance_m": int(est_dist*1000), "duration_s": int(est_mins*60)}]
        }

    def list_waypoints(self) -> List[Dict[str, Any]]:
        """List all saved waypoints."""
        return db_manager.execute_query(self.DB, "SELECT * FROM saved_waypoints ORDER BY created_at DESC")

    def add_waypoint(self, name: str, latitude: float, longitude: float, category: str = "Waypoint", notes: str = "") -> Dict[str, Any]:
        """Save a new waypoint to the map database."""
        new_id = db_manager.execute_non_query(
            self.DB,
            "INSERT INTO saved_waypoints (name, latitude, longitude, category, notes) VALUES (?, ?, ?, ?, ?)",
            (name.strip(), latitude, longitude, category.strip(), notes.strip())
        )
        rows = db_manager.execute_query(self.DB, "SELECT * FROM saved_waypoints WHERE id = ?", (new_id,))
        return rows[0] if rows else {}


maps_service = MapsService()
