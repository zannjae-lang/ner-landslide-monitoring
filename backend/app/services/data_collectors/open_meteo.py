import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List
import httpx

from app.core.logger import logger
from app.services.data_collectors.base import BaseDataCollector, NormalizedObservation


class OpenMeteoCollector(BaseDataCollector):
    """Real environmental weather and soil moisture collector using Open-Meteo API."""

    def __init__(self, timeout: float = 10.0):
        self._provider_id = "open_meteo"
        self._name = "Open-Meteo Weather & Soil Moisture API"
        self.timeout = timeout
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def name(self) -> str:
        return self._name

    async def check_health(self) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    self.base_url,
                    params={
                        "latitude": 26.2006,
                        "longitude": 92.9376,
                        "hourly": "precipitation",
                        "past_days": 1,
                        "forecast_days": 1,
                    },
                )
            latency = (time.perf_counter() - start) * 1000.0
            if res.status_code == 200:
                return {
                    "is_available": True,
                    "status": "Operational",
                    "latency_ms": round(latency, 2),
                    "error_message": None,
                }
            return {
                "is_available": False,
                "status": f"HTTP {res.status_code}",
                "latency_ms": round(latency, 2),
                "error_message": res.text,
            }
        except Exception as e:
            return {
                "is_available": False,
                "status": "Unreachable",
                "latency_ms": None,
                "error_message": str(e),
            }

    async def fetch_observation(self, latitude: float, longitude: float) -> NormalizedObservation:
        now_utc = datetime.now(timezone.utc)
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": [
                "precipitation",
                "soil_moisture_0_to_7cm",
                "soil_moisture_7_to_28cm",
                "temperature_2m",
                "relative_humidity_2m",
            ],
            "past_days": 7,
            "forecast_days": 1,
            "timezone": "UTC",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(self.base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

        hourly = data.get("hourly", {})
        precip_list: List[float] = hourly.get("precipitation", []) or []
        sm1_list: List[float] = hourly.get("soil_moisture_0_to_7cm", []) or []
        sm2_list: List[float] = hourly.get("soil_moisture_7_to_28cm", []) or []
        temp_list: List[float] = hourly.get("temperature_2m", []) or []
        hum_list: List[float] = hourly.get("relative_humidity_2m", []) or []

        # Current/past index is typically the 7 days * 24 hours = ~168th index
        curr_idx = min(len(precip_list) - 1, 7 * 24)

        def sum_window(hours: int) -> float:
            if not precip_list or curr_idx < 0:
                return 0.0
            start_i = max(0, curr_idx - hours + 1)
            slice_vals = [v for v in precip_list[start_i : curr_idx + 1] if v is not None]
            return float(sum(slice_vals))

        rain_1h = round(sum_window(1), 2)
        rain_3h = round(sum_window(3), 2)
        rain_6h = round(sum_window(6), 2)
        rain_12h = round(sum_window(12), 2)
        rain_24h = round(sum_window(24), 2)
        rain_3d = round(sum_window(72), 2)
        rain_7d = round(sum_window(168), 2)

        def safe_last(lst: List[float], default: float) -> float:
            for v in reversed(lst[: curr_idx + 1]):
                if v is not None:
                    return float(v)
            return default

        sm1 = round(safe_last(sm1_list, 0.30), 4)
        sm2 = round(safe_last(sm2_list, 0.35), 4)
        temp = safe_last(temp_list, 24.0)
        hum = safe_last(hum_list, 75.0)

        return NormalizedObservation(
            provider_id=self.provider_id,
            latitude=latitude,
            longitude=longitude,
            observed_at=now_utc,
            retrieved_at=now_utc,
            rainfall_1h_mm=rain_1h,
            rainfall_3h_mm=rain_3h,
            rainfall_6h_mm=rain_6h,
            rainfall_12h_mm=rain_12h,
            rainfall_24h_mm=rain_24h,
            rainfall_3day_mm=rain_3d,
            rainfall_7day_mm=rain_7d,
            soil_moisture_layer_1=sm1,
            soil_moisture_layer_2=sm2,
            temperature_c=temp,
            humidity_percent=hum,
            quality_status="Fresh",
            raw_payload={"source": "open_meteo_live", "elevation": data.get("elevation")},
        )
