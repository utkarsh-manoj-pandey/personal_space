"""
Weather Subsystem Service
Retrieves real-time atmospheric conditions and 7-day forecasts without proprietary API keys.
Leverages the Open-Meteo open scientific models, IP-based auto-location detection,
and persistent SQLite caching for offline resilience.
"""

import json
import urllib.request
import urllib.parse
import logging
from typing import Dict, Any, Optional
from ..database_manager import db_manager

logger = logging.getLogger("WeatherService")


class WeatherService:
    DB = "weather.db"

    # WMO Weather interpretation codes (WW)
    WMO_CODES = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Slight Snow Fall",
        73: "Moderate Snow Fall",
        75: "Heavy Snow Fall",
        77: "Snow Grains",
        80: "Slight Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",
        85: "Slight Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Slight Hail",
        99: "Thunderstorm with Heavy Hail"
    }

    def __init__(self):
        self._seed_default_locations()

    def _seed_default_locations(self):
        """Seed fallback locations if database is empty."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM saved_locations")
        if count and count[0]["count"] == 0:
            locations = [
                ("New York", 40.7128, -74.0060, 0),
                ("London", 51.5074, -0.1278, 0),
                ("Tokyo", 35.6762, 139.6503, 0),
                ("Zurich", 47.3769, 8.5417, 0),
                ("Singapore", 1.3521, 103.8198, 1)
            ]
            for loc in locations:
                db_manager.execute_non_query(
                    self.DB,
                    "INSERT OR IGNORE INTO saved_locations (city_name, latitude, longitude, is_default) VALUES (?, ?, ?, ?)",
                    loc
                )

    def detect_ip_location(self) -> Dict[str, Any]:
        """Detect current user approximate coordinates via keyless IP geolocator."""
        try:
            req = urllib.request.Request(
                "https://ipapi.co/json/",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode())
                return {
                    "city": data.get("city", "Current Location"),
                    "country": data.get("country_name", ""),
                    "latitude": float(data.get("latitude", 40.7128)),
                    "longitude": float(data.get("longitude", -74.0060))
                }
        except Exception as e:
            logger.warning(f"IP Geolocation fallback triggered: {e}")
            return {"city": "New York", "country": "USA", "latitude": 40.7128, "longitude": -74.0060}

    def geocode_city(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Resolve city name into latitude/longitude using Open-Meteo keyless geocoding service."""
        try:
            encoded = urllib.parse.quote_plus(city_name.strip())
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded}&count=1&language=en&format=json"
            req = urllib.request.Request(url, headers={"User-Agent": "NexusWorkstation/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                payload = json.loads(response.read().decode())
                results = payload.get("results")
                if results and len(results) > 0:
                    first = results[0]
                    return {
                        "city": first.get("name"),
                        "country": first.get("country", ""),
                        "latitude": float(first.get("latitude")),
                        "longitude": float(first.get("longitude"))
                    }
        except Exception as e:
            logger.error(f"Geocoding error for {city_name}: {e}")
        return None

    def get_weather(self, city_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch live weather data from Open-Meteo with caching.
        Returns real-time temperatures, humidity, wind speed, pressure, UV index, and 7-day forecast.
        """
        location = None
        if city_name and city_name.strip():
            location = self.geocode_city(city_name)
        
        if not location:
            # Check default saved location
            saved = db_manager.execute_query(self.DB, "SELECT * FROM saved_locations WHERE is_default = 1 LIMIT 1")
            if saved:
                location = {
                    "city": saved[0]["city_name"],
                    "country": "Primary",
                    "latitude": saved[0]["latitude"],
                    "longitude": saved[0]["longitude"]
                }
            else:
                location = self.detect_ip_location()

        lat = location["latitude"]
        lon = location["longitude"]
        city = location["city"]
        country = location.get("country", "")

        # Attempt remote live fetch
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&"
                f"current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m&"
                f"hourly=temperature_2m,weather_code&"
                f"daily=weather_code,temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_probability_max&"
                f"timezone=auto"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "NexusWorkstation/1.0"})
            with urllib.request.urlopen(req, timeout=6) as response:
                raw_data = json.loads(response.read().decode())

                current = raw_data.get("current", {})
                wmo_code = current.get("weather_code", 0)
                condition_text = self.WMO_CODES.get(wmo_code, "Clear")

                # Format hourly graph points (next 24 hours)
                hourly_temps = raw_data.get("hourly", {}).get("temperature_2m", [])[:24]
                hourly_times = raw_data.get("hourly", {}).get("time", [])[:24]
                formatted_hourly = [
                    {"time": t.split("T")[-1][:5], "temp": round(temp, 1)}
                    for t, temp in zip(hourly_times, hourly_temps)
                ]

                # Format 7-day forecast cards
                daily_raw = raw_data.get("daily", {})
                daily_times = daily_raw.get("time", [])
                daily_max = daily_raw.get("temperature_2m_max", [])
                daily_min = daily_raw.get("temperature_2m_min", [])
                daily_codes = daily_raw.get("weather_code", [])
                daily_uv = daily_raw.get("uv_index_max", [])
                daily_rain = daily_raw.get("precipitation_probability_max", [])

                daily_forecast = []
                for i in range(min(7, len(daily_times))):
                    daily_forecast.append({
                        "date": daily_times[i],
                        "max_temp": round(daily_max[i], 1) if i < len(daily_max) else 0.0,
                        "min_temp": round(daily_min[i], 1) if i < len(daily_min) else 0.0,
                        "condition": self.WMO_CODES.get(daily_codes[i] if i < len(daily_codes) else 0, "Clear"),
                        "uv": round(daily_uv[i], 1) if i < len(daily_uv) else 0.0,
                        "rain_chance": daily_rain[i] if i < len(daily_rain) else 0
                    })

                weather_payload = {
                    "city": city,
                    "country": country,
                    "latitude": lat,
                    "longitude": lon,
                    "temperature": round(current.get("temperature_2m", 21.0), 1),
                    "feels_like": round(current.get("apparent_temperature", 21.0), 1),
                    "humidity": current.get("relative_humidity_2m", 50),
                    "wind_speed": round(current.get("wind_speed_10m", 12.0), 1),
                    "wind_direction": current.get("wind_direction_10m", 180),
                    "pressure": round(current.get("surface_pressure", 1013.25), 1),
                    "condition": condition_text,
                    "condition_code": wmo_code,
                    "is_day": current.get("is_day", 1),
                    "hourly": formatted_hourly,
                    "daily": daily_forecast
                }

                # Update SQLite Cache
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT INTO weather_cache 
                       (city, country, latitude, longitude, temp, feels_like, humidity, wind_speed, condition_text, condition_code, forecast_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (city, country, lat, lon, weather_payload["temperature"], weather_payload["feels_like"],
                     weather_payload["humidity"], weather_payload["wind_speed"], condition_text, wmo_code, json.dumps(weather_payload))
                )

                return weather_payload

        except Exception as e:
            logger.error(f"Live weather fetch failed: {e}. Falling back to cached data.")
            # Retrieve latest cached reading
            cached = db_manager.execute_query(
                self.DB,
                "SELECT forecast_json FROM weather_cache ORDER BY fetched_at DESC LIMIT 1"
            )
            if cached and cached[0].get("forecast_json"):
                return json.loads(cached[0]["forecast_json"])

            # Fallback mock telemetry if completely disconnected with zero previous cache
            return {
                "city": city or "Local Workstation",
                "country": "Offline Cache",
                "latitude": lat,
                "longitude": lon,
                "temperature": 21.5,
                "feels_like": 21.0,
                "humidity": 48,
                "wind_speed": 14.2,
                "wind_direction": 220,
                "pressure": 1014.2,
                "condition": "Mainly Clear",
                "condition_code": 1,
                "is_day": 1,
                "hourly": [{"time": f"{h:02d}:00", "temp": 20.0 + (h % 5)} for h in range(24)],
                "daily": [{"date": f"Day +{i}", "max_temp": 23.0, "min_temp": 16.0, "condition": "Clear Sky", "uv": 5.0, "rain_chance": 10} for i in range(7)]
            }


weather_service = WeatherService()
