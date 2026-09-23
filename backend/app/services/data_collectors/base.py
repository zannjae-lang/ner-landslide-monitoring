from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class NormalizedObservation(BaseModel):
    provider_id: str
    latitude: float
    longitude: float
    observed_at: datetime
    retrieved_at: datetime
    rainfall_1h_mm: float
    rainfall_3h_mm: float
    rainfall_6h_mm: float
    rainfall_12h_mm: float
    rainfall_24h_mm: float
    rainfall_3day_mm: float
    rainfall_7day_mm: float
    soil_moisture_layer_1: float
    soil_moisture_layer_2: float
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    quality_status: str = "Fresh"
    raw_payload: Optional[Dict[str, Any]] = None


class BaseDataCollector(ABC):
    """Abstract base class for all environmental data collectors."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def fetch_observation(self, latitude: float, longitude: float) -> NormalizedObservation:
        """Fetch and return a normalized observation for the given coordinates."""
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Perform a lightweight health/connectivity check."""
        pass
