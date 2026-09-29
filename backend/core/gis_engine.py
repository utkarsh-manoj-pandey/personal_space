"""
Aether Core GIS & Map Geodesy Framework
Deterministic, pure Python spatial computations, coordinate transformations, and tile math:
- Slippy Map Tile Calculations: (latitude, longitude, zoom level) <-> Web Mercator tile (x, y) coordinates and pixel offsets.
- Universal Transverse Mercator (UTM) Projection Engine: WGS-84 ellipsoidal transformation to UTM zone, easting, and northing in meters.
- Spatial Clustering Engine: Distance-based proximity clustering for dense geographic markers (earthquakes, waypoints).
- Bounding Box & Viewport Enclosure Math.
"""

import math
from typing import List, Dict, Any, Tuple, Optional


class SlippyMapTileMath:
    """
    Standard Web Mercator (EPSG:3857) Slippy Map tile conversions.
    Compatible with OpenStreetMap, CartoDB, and Leaflet vector tile coordinate systems.
    """

    @staticmethod
    def deg2tile(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
        """Convert lat/lon coordinates to tile (x, y) at given zoom level."""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile

    @staticmethod
    def tile2deg(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
        """Convert tile (x, y) at zoom level to NW corner latitude and longitude."""
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return round(lat_deg, 6), round(lon_deg, 6)

    @classmethod
    def get_tile_bounds(cls, xtile: int, ytile: int, zoom: int) -> Dict[str, float]:
        """Calculates bounding box [north, south, east, west] for a specific tile."""
        nw_lat, nw_lon = cls.tile2deg(xtile, ytile, zoom)
        se_lat, se_lon = cls.tile2deg(xtile + 1, ytile + 1, zoom)
        return {
            "north": nw_lat,
            "south": se_lat,
            "west": nw_lon,
            "east": se_lon
        }


class UTMProjectionEngine:
    """
    Universal Transverse Mercator (UTM) Coordinate Converter.
    Transforms latitude/longitude on WGS-84 ellipsoid to Easting, Northing, and UTM Zone.
    """

    A = 6378137.0           # WGS-84 Semi-major axis
    F = 1.0 / 298.257223563 # Flattening
    K0 = 0.9996             # Scale factor on central meridian

    @classmethod
    def latlon_to_utm(cls, lat: float, lon: float) -> Dict[str, Any]:
        """
        Converts (lat, lon) to UTM Easting, Northing, Zone Number, and Zone Letter.
        """
        zone_number = int((lon + 180.0) / 6.0) + 1
        # Central meridian for zone
        lon_origin = (zone_number - 1) * 6 - 180 + 3
        lon_origin_rad = math.radians(lon_origin)

        # Ellipsoid parameters
        e_sq = cls.F * (2.0 - cls.F)
        e_prime_sq = e_sq / (1.0 - e_sq)

        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        n_rad = cls.A / math.sqrt(1.0 - e_sq * (math.sin(lat_rad) ** 2))
        t = math.tan(lat_rad) ** 2
        c = e_prime_sq * (math.cos(lat_rad) ** 2)
        a_param = math.cos(lat_rad) * (lon_rad - lon_origin_rad)

        # Meridional arc
        m = cls.A * (
            (1.0 - e_sq / 4.0 - 3.0 * (e_sq ** 2) / 64.0 - 5.0 * (e_sq ** 3) / 256.0) * lat_rad -
            (3.0 * e_sq / 8.0 + 3.0 * (e_sq ** 2) / 32.0 + 45.0 * (e_sq ** 3) / 1024.0) * math.sin(2.0 * lat_rad) +
            (15.0 * (e_sq ** 2) / 256.0 + 45.0 * (e_sq ** 3) / 1024.0) * math.sin(4.0 * lat_rad) -
            (35.0 * (e_sq ** 3) / 3072.0) * math.sin(6.0 * lat_rad)
        )

        easting = cls.K0 * n_rad * (
            a_param +
            (1.0 - t + c) * (a_param ** 3) / 6.0 +
            (5.0 - 18.0 * t + (t ** 2) + 72.0 * c - 58.0 * e_prime_sq) * (a_param ** 5) / 120.0
        ) + 500000.0  # False Easting

        northing = cls.K0 * (
            m +
            n_rad * math.tan(lat_rad) * (
                (a_param ** 2) / 2.0 +
                (5.0 - t + 9.0 * c + 4.0 * (c ** 2)) * (a_param ** 4) / 24.0 +
                (61.0 - 58.0 * t + (t ** 2) + 600.0 * c - 330.0 * e_prime_sq) * (a_param ** 6) / 720.0
            )
        )

        if lat < 0:
            northing += 10000000.0  # False Northing for Southern Hemisphere

        # Zone letter
        letters = "CDEFGHJKLMNPQRSTUVWXX"
        letter_idx = max(0, min(20, int((lat + 80.0) / 8.0)))
        zone_letter = letters[letter_idx]

        return {
            "easting": round(easting, 2),
            "northing": round(northing, 2),
            "zone_number": zone_number,
            "zone_letter": zone_letter,
            "is_northern_hemisphere": lat >= 0
        }


class SpatialClusterEngine:
    """
    Proximity clustering algorithm for grouping close geographic points.
    Prevents map UI saturation and computes cluster centroid centers.
    """

    @staticmethod
    def cluster_points(points: List[Dict[str, Any]], distance_threshold_km: float = 200.0) -> List[Dict[str, Any]]:
        """
        Groups points where distance <= threshold into clusters.
        Each point must have 'latitude' and 'longitude'.
        """
        if not points:
            return []

        clusters = []
        visited = set()

        def _dist(p1, p2):
            # Fast spherical approximation
            lat1, lon1 = math.radians(p1["latitude"]), math.radians(p1["longitude"])
            lat2, lon2 = math.radians(p2["latitude"]), math.radians(p2["longitude"])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
            return 6371.0 * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        for i in range(len(points)):
            if i in visited:
                continue

            current_cluster = [points[i]]
            visited.add(i)

            for j in range(i + 1, len(points)):
                if j in visited:
                    continue
                if _dist(points[i], points[j]) <= distance_threshold_km:
                    current_cluster.append(points[j])
                    visited.add(j)

            # Calculate centroid
            centroid_lat = sum(p["latitude"] for p in current_cluster) / len(current_cluster)
            centroid_lon = sum(p["longitude"] for p in current_cluster) / len(current_cluster)

            clusters.append({
                "centroid_latitude": round(centroid_lat, 4),
                "centroid_longitude": round(centroid_lon, 4),
                "point_count": len(current_cluster),
                "points": current_cluster
            })

        return clusters
