from typing import Any, Dict, List, Optional
from app.config.data_source_config import DATA_PROVIDERS_CONFIG
from app.core.logger import logger
from app.services.data_collectors.base import BaseDataCollector, NormalizedObservation
from app.services.data_collectors.dem_collector import dem_collector
from app.services.data_collectors.gee_collector import gee_collector
from app.services.data_collectors.isro_mosdac import isro_mosdac_collector
from app.services.data_collectors.mock_collector import MockCollector
from app.services.data_collectors.nasa_imerg import nasa_imerg_collector
from app.services.data_collectors.open_meteo import OpenMeteoCollector
from app.services.data_collectors.osm_collector import osm_collector


class DataCollectorManager:
    """Manages active environmental collectors, failovers, and telemetry checks."""

    def __init__(self):
        self.weather_collectors: Dict[str, BaseDataCollector] = {
            "open_meteo": OpenMeteoCollector(),
            "nasa_imerg": nasa_imerg_collector,
            "mosdac_gsmap": isro_mosdac_collector,
            "mock_collector": MockCollector(),
        }
        self.dem_collector = dem_collector
        self.osm_collector = osm_collector
        self.gee_collector = gee_collector
        self.nasa_imerg_collector = nasa_imerg_collector
        self.isro_mosdac_collector = isro_mosdac_collector

    async def get_observation(
        self,
        latitude: float,
        longitude: float,
        preferred_provider: Optional[str] = None,
        allow_fallback: bool = True,
    ) -> NormalizedObservation:
        # Try preferred provider first
        provider_keys = [preferred_provider] if preferred_provider and preferred_provider in self.weather_collectors else []
        # Then live providers, then mock
        for key in ["open_meteo", "mock_collector"]:
            if key not in provider_keys:
                provider_keys.append(key)

        last_error = None
        for key in provider_keys:
            collector = self.weather_collectors[key]
            try:
                obs = await collector.fetch_observation(latitude, longitude)
                return obs
            except Exception as e:
                logger.warning(f"Provider '{key}' failed to fetch observation: {e}")
                last_error = e
                if not allow_fallback:
                    break

        # If everything failed, generate fallback
        logger.error(f"All providers failed, generating emergency mock: {last_error}")
        return await self.weather_collectors["mock_collector"].fetch_observation(latitude, longitude)

    async def get_live_elevation(self, latitude: float, longitude: float) -> float:
        return await self.dem_collector.fetch_elevation(latitude, longitude)

    async def get_live_distances(self, latitude: float, longitude: float):
        return await self.osm_collector.fetch_distances(latitude, longitude)

    async def get_all_providers_status(self) -> List[Dict[str, Any]]:
        results = []
        for provider_id, config in DATA_PROVIDERS_CONFIG.items():
            if provider_id in self.weather_collectors:
                collector = self.weather_collectors[provider_id]
                health = await collector.check_health()
                results.append({
                    "provider_id": provider_id,
                    "name": config["name"],
                    "description": config["description"],
                    "status": health["status"],
                    "is_available": health["is_available"],
                    "requires_auth": config["requires_auth"],
                    "latency_ms": health.get("latency_ms"),
                    "last_successful_sync": None,
                    "coverage": config["coverage"],
                    "update_cadence": config["update_cadence"],
                    "error_message": health.get("error_message"),
                })
            elif provider_id == "google_earth_engine":
                health = await self.gee_collector.check_health()
                results.append({
                    "provider_id": provider_id,
                    "name": config["name"],
                    "description": config["description"],
                    "status": health["status"],
                    "is_available": health["is_available"],
                    "requires_auth": config["requires_auth"],
                    "latency_ms": health.get("latency_ms"),
                    "last_successful_sync": None,
                    "coverage": config["coverage"],
                    "update_cadence": config["update_cadence"],
                    "error_message": health.get("error_message"),
                })
            elif provider_id == "copernicus_dem":
                health = await self.dem_collector.check_health()
                results.append({
                    "provider_id": provider_id,
                    "name": config["name"],
                    "description": config["description"],
                    "status": health["status"],
                    "is_available": health["is_available"],
                    "requires_auth": config["requires_auth"],
                    "latency_ms": health.get("latency_ms"),
                    "last_successful_sync": None,
                    "coverage": config["coverage"],
                    "update_cadence": config["update_cadence"],
                    "error_message": health.get("error_message"),
                })
            elif provider_id == "osm_overpass":
                health = await self.osm_collector.check_health()
                results.append({
                    "provider_id": provider_id,
                    "name": config["name"],
                    "description": config["description"],
                    "status": health["status"],
                    "is_available": health["is_available"],
                    "requires_auth": config["requires_auth"],
                    "latency_ms": health.get("latency_ms"),
                    "last_successful_sync": None,
                    "coverage": config["coverage"],
                    "update_cadence": config["update_cadence"],
                    "error_message": health.get("error_message"),
                })
            else:
                results.append({
                    "provider_id": provider_id,
                    "name": config["name"],
                    "description": config["description"],
                    "status": "Auth Required" if config["requires_auth"] else "Active Layer",
                    "is_available": not config["requires_auth"],
                    "requires_auth": config["requires_auth"],
                    "latency_ms": None,
                    "last_successful_sync": None,
                    "coverage": config["coverage"],
                    "update_cadence": config["update_cadence"],
                    "error_message": "API credentials required for live queries" if config["requires_auth"] else None,
                })
        return results


collector_manager = DataCollectorManager()
