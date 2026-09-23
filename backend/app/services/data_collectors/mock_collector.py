import math
import random
from datetime import datetime, timezone
from typing import Any, Dict

from app.services.data_collectors.base import BaseDataCollector, NormalizedObservation


class MockCollector(BaseDataCollector):
    """Simulated/Demonstration collector for offline testing with clearly tagged demo data."""

    def __init__(self):
        self._provider_id = "mock_collector"
        self._name = "NER Simulated Telemetry Feed"

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def name(self) -> str:
        return self._name

    async def check_health(self) -> Dict[str, Any]:
        return {
            "is_available": True,
            "status": "Operational (Demo)",
            "latency_ms": 1.2,
            "error_message": None,
        }

    async def fetch_observation(self, latitude: float, longitude: float) -> NormalizedObservation:
        now_utc = datetime.now(timezone.utc)

        # Generate realistic spatial variation using geographic coordinates
        seed_val = int(abs(latitude * 1000 + longitude * 100)) % 100
        base_rain = (seed_val % 40) * 1.5

        rain_1h = round(max(0.0, (base_rain * 0.15) + random.uniform(0.0, 5.0)), 2)
        rain_3h = round(rain_1h + max(0.0, (base_rain * 0.3) + random.uniform(0.0, 8.0)), 2)
        rain_6h = round(rain_3h + max(0.0, (base_rain * 0.5) + random.uniform(0.0, 12.0)), 2)
        rain_12h = round(rain_6h + max(0.0, base_rain + random.uniform(0.0, 15.0)), 2)
        rain_24h = round(rain_12h + max(0.0, (base_rain * 1.2) + random.uniform(0.0, 20.0)), 2)
        rain_3d = round(rain_24h + max(0.0, (base_rain * 1.8) + random.uniform(5.0, 35.0)), 2)
        rain_7d = round(rain_3d + max(0.0, (base_rain * 2.2) + random.uniform(10.0, 50.0)), 2)

        sm1 = round(min(0.65, 0.25 + (rain_24h / 200.0) + random.uniform(0.0, 0.05)), 4)
        sm2 = round(min(0.60, 0.30 + (rain_3d / 300.0) + random.uniform(0.0, 0.04)), 4)

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
            temperature_c=round(22.0 + (seed_val % 8) - (latitude - 24.0) * 1.2, 1),
            humidity_percent=round(min(98.0, 65.0 + (rain_24h * 0.4)), 1),
            quality_status="Provisional/Demo",
            raw_payload={"source": "simulated_ner_feed", "is_synthetic": True},
        )
