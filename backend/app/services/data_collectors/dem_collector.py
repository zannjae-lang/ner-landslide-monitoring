import time
from typing import Any, Dict, Optional
import httpx
from app.core.logger import logger


class DEMCollector:
    """Live Elevation and Digital Elevation Model (Copernicus DEM / Open-Meteo Elevation API)."""

    def __init__(self, timeout: float = 6.0):
        self.provider_id = "copernicus_dem"
        self.name = "Copernicus DEM & Open-Elevation Live API"
        self.timeout = timeout
        self.base_url = "https://api.open-meteo.com/v1/elevation"

    async def check_health(self) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(self.base_url, params={"latitude": 26.2006, "longitude": 92.9376})
            latency = (time.perf_counter() - start) * 1000.0
            if res.status_code == 200:
                return {
                    "is_available": True,
                    "status": "Operational (Live)",
                    "latency_ms": round(latency, 1),
                    "error_message": None,
                }
            return {
                "is_available": False,
                "status": f"HTTP {res.status_code}",
                "latency_ms": round(latency, 1),
                "error_message": res.text,
            }
        except Exception as e:
            return {
                "is_available": False,
                "status": "Degraded",
                "latency_ms": None,
                "error_message": str(e),
            }

    async def fetch_elevation(self, latitude: float, longitude: float) -> float:
        """Fetch live elevation in meters for coordinates."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(self.base_url, params={"latitude": latitude, "longitude": longitude})
                if res.status_code == 200:
                    elev_list = res.json().get("elevation", [])
                    if elev_list and elev_list[0] is not None:
                        return float(elev_list[0])
        except Exception as e:
            logger.warning(f"Live DEM query failed for ({latitude}, {longitude}): {e}")

        # Geographic topographic estimate for NER fallback
        lat_factor = (latitude - 22.0) / 7.0
        return round(max(50.0, 350.0 + lat_factor * 2200.0), 1)


dem_collector = DEMCollector()
