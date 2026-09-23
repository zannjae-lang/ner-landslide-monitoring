"""Data Source and Provider Registry Configurations."""
from typing import Dict, Any


DATA_PROVIDERS_CONFIG: Dict[str, Dict[str, Any]] = {
    "open_meteo": {
        "name": "Open-Meteo Weather & Soil Moisture API",
        "description": "Live real-time precipitation across 7 windows (1h-7d) and dual-layer volumetric soil moisture (0-7cm & 7-28cm)",
        "requires_auth": False,
        "coverage": "8 NER States & Global (0.05-0.1 deg spatial resolution)",
        "update_cadence": "Real-Time / Hourly",
        "status": "Active / Primary Live Stream",
    },
    "google_earth_engine": {
        "name": "Google Earth Engine (GEE)",
        "description": "Satellite cloud platform for planetary-scale geospatial analysis (Sentinel-1 SAR & Sentinel-2 10m Optical NDVI)",
        "requires_auth": True,
        "coverage": "Global & Pan-NER Bounding Box",
        "update_cadence": "Sentinel 5-day / Real-time on demand",
        "status": "Authentication Ready",
    },
    "copernicus_dem": {
        "name": "Copernicus DEM & Open-Elevation Live",
        "description": "High-resolution 30m Digital Elevation Model for terrain slope, curvature, TPI, TRI calculation",
        "requires_auth": False,
        "coverage": "8 NER States Topography",
        "update_cadence": "Static 30m Grid / Live Coordinate Query",
        "status": "Active Layer (Live)",
    },
    "osm_overpass": {
        "name": "OpenStreetMap Road & Drainage Vectors",
        "description": "Vector distance calculations to nearest highway infrastructure and stream drainage networks",
        "requires_auth": False,
        "coverage": "NER 8 States Vector Network",
        "update_cadence": "Live / Continuous Ingestion",
        "status": "Active Layer (Live)",
    },
    "nasa_imerg": {
        "name": "NASA IMERG GPM Precipitation",
        "description": "Integrated Multi-satellitE Retrievals for GPM (Global Precipitation Measurement) Early & Late Run half-hourly products",
        "requires_auth": True,
        "auth_env_vars": ["NASA_EARTHDATA_TOKEN", "NASA_IMERG_API_KEY", "NASA_EARTHDATA_USERNAME"],
        "coverage": "8 NER States & Global 60°N-60°S (0.1° spatial resolution)",
        "update_cadence": "30-min to 3-hourly",
        "agency": "NASA GES DISC / Earthdata",
        "status": "Authentication Required",
    },
    "mosdac_gsmap": {
        "name": "ISRO MOSDAC GSMaP & INSAT-3D",
        "description": "ISRO Space Applications Centre (SAC) Meteorological & Oceanographic Satellite Data Archival Centre",
        "requires_auth": True,
        "auth_env_vars": ["MOSDAC_USER_KEY", "MOSDAC_API_KEY", "MOSDAC_USER_ID"],
        "coverage": "Indian Subcontinent & 8 NER States (4km - 0.1° resolution)",
        "update_cadence": "Hourly / Half-hourly",
        "agency": "ISRO SAC (Space Applications Centre)",
        "status": "Authentication Required",
    },
    "esa_cci_soil": {
        "name": "ESA CCI Multi-Layer Soil Moisture",
        "description": "European Space Agency Climate Change Initiative Soil Moisture Sensor Ingestion",
        "requires_auth": False,
        "coverage": "Global 0.25 deg",
        "update_cadence": "Daily Ingestion",
        "status": "Active Layer",
    },
    "mock_collector": {
        "name": "NER Simulated Real-Time Station Feed",
        "description": "Synthetic real-time telemetry generator for offline test & emergency fallback scenarios",
        "requires_auth": False,
        "coverage": "8 NER States Station Network",
        "update_cadence": "Real-Time on Request",
        "status": "Active / Demo Fallback",
    },
}
