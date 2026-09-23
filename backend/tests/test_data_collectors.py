import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
import pytest

from app.services.data_collectors.open_meteo import OpenMeteoCollector
from app.services.data_collectors.nasa_imerg import NasaImergCollector
from app.services.data_collectors.isro_mosdac import IsroMosdacCollector
from app.services.data_collectors.collector_manager import collector_manager
from app.services.data_collectors.google_earth_engine import GoogleEarthEngineService


def test_open_meteo_health():
    async def run():
        collector = OpenMeteoCollector()
        health = await collector.check_health()
        assert "is_available" in health
        assert "status" in health
        assert health["is_available"] in [True, False]

    asyncio.run(run())


def test_nasa_imerg_missing_credentials(monkeypatch):
    """Verify that NASA IMERG cleanly reports 'Authentication Required' when no keys are set."""
    async def run():
        from app.config import settings
        monkeypatch.setattr(settings.settings, "NASA_EARTHDATA_TOKEN", "")
        monkeypatch.setattr(settings.settings, "NASA_IMERG_API_KEY", "")
        monkeypatch.setattr(settings.settings, "NASA_EARTHDATA_USERNAME", "")
        monkeypatch.setattr(settings.settings, "NASA_EARTHDATA_PASSWORD", "")

        with patch.object(GoogleEarthEngineService, "is_initialized", new_callable=PropertyMock, return_value=False):
            collector = NasaImergCollector()
            health = await collector.check_health()
            assert health["is_available"] is False
            assert health["status"] == "Authentication Required"
            assert "NASA_EARTHDATA_TOKEN" in health["error_message"]

    asyncio.run(run())


def test_nasa_imerg_invalid_token(monkeypatch):
    """Verify that invalid token returns Authentication Failed on 401."""
    async def run():
        from app.config import settings
        monkeypatch.setattr(settings.settings, "NASA_EARTHDATA_TOKEN", "invalid_test_token_12345")

        with patch.object(GoogleEarthEngineService, "is_initialized", new_callable=PropertyMock, return_value=False):
            collector = NasaImergCollector()
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_res = MagicMock()
                mock_res.status_code = 401
                mock_res.text = "Unauthorized: Invalid token"
                mock_get.return_value = mock_res

                health = await collector.check_health()
                assert health["is_available"] is False
                assert health["status"] == "Authentication Failed"
                assert "rejected credentials" in health["error_message"]

    asyncio.run(run())


def test_nasa_imerg_accumulation_windows(monkeypatch):
    """Verify 7-window rainfall calculation and negative nodata filtering."""
    async def run():
        from app.config import settings
        monkeypatch.setattr(settings.settings, "NASA_EARTHDATA_TOKEN", "valid_mock_token")

        collector = NasaImergCollector()

        synthetic_series = {}
        for h in range(200):
            key = f"20260901{h:02d}"
            synthetic_series[key] = -9999.0 if h % 25 == 0 else 1.5

        mock_resp_data = {
            "properties": {
                "parameter": {
                    "PRECTOTCORR": synthetic_series
                }
            }
        }

        with patch.object(GoogleEarthEngineService, "is_initialized", new_callable=PropertyMock, return_value=False):
            mock_client = AsyncMock()
            mock_res = MagicMock()
            mock_res.status_code = 200
            mock_res.json.return_value = mock_resp_data
            mock_res.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_res
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None

            with patch("httpx.AsyncClient", return_value=mock_client):
                obs = await collector.fetch_observation(latitude=27.1264, longitude=95.7337)

                assert obs.provider_id == "nasa_imerg"
                assert obs.rainfall_1h_mm == 1.5
                assert obs.rainfall_3h_mm == 4.5
                assert obs.rainfall_6h_mm == 9.0
                assert obs.rainfall_12h_mm == 18.0
                assert obs.rainfall_24h_mm > 0
                assert obs.rainfall_7day_mm >= obs.rainfall_24h_mm
                assert obs.quality_status == "Fresh"

    asyncio.run(run())


def test_isro_mosdac_missing_credentials(monkeypatch):
    """Verify that ISRO MOSDAC reports 'Authentication Required' when keys are missing."""
    async def run():
        from app.config import settings
        monkeypatch.setattr(settings.settings, "MOSDAC_USER_KEY", "")
        monkeypatch.setattr(settings.settings, "MOSDAC_API_KEY", "")

        collector = IsroMosdacCollector()
        health = await collector.check_health()
        assert health["is_available"] is False
        assert health["status"] == "Authentication Required"
        assert "MOSDAC_USER_KEY" in health["error_message"]

    asyncio.run(run())


def test_isro_mosdac_invalid_credentials(monkeypatch):
    """Verify that ISRO MOSDAC reports 'Authentication Failed' on 401."""
    async def run():
        from app.config import settings
        monkeypatch.setattr(settings.settings, "MOSDAC_USER_KEY", "invalid_mosdac_key")

        collector = IsroMosdacCollector()
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_res = MagicMock()
            mock_res.status_code = 401
            mock_get.return_value = mock_res

            health = await collector.check_health()
            assert health["is_available"] is False
            assert health["status"] == "Authentication Failed"

    asyncio.run(run())


def test_collector_manager_all_providers_status():
    """Verify DataCollectorManager queries all registered providers."""
    async def run():
        providers_status = await collector_manager.get_all_providers_status()
        provider_ids = [p["provider_id"] for p in providers_status]

        assert "open_meteo" in provider_ids
        assert "nasa_imerg" in provider_ids
        assert "mosdac_gsmap" in provider_ids
        assert "google_earth_engine" in provider_ids
        assert "copernicus_dem" in provider_ids
        assert "osm_overpass" in provider_ids

    asyncio.run(run())


def test_ner_states_coverage():
    """Verify coordinates for all 8 NER states are handled gracefully."""
    async def run():
        ner_capitals = [
            ("Arunachal Pradesh", 27.0844, 93.6053),
            ("Assam", 26.1664, 91.7058),
            ("Manipur", 24.8170, 93.9368),
            ("Meghalaya", 25.5788, 91.8933),
            ("Mizoram", 23.7271, 92.7176),
            ("Nagaland", 25.6751, 94.1086),
            ("Sikkim", 27.3389, 88.6065),
            ("Tripura", 23.8315, 91.2868),
        ]

        for state, lat, lon in ner_capitals:
            obs = await collector_manager.get_observation(lat, lon, preferred_provider="mock_collector")
            assert obs.latitude == lat
            assert obs.longitude == lon
            assert obs.rainfall_24h_mm >= 0.0

    asyncio.run(run())
