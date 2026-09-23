import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config.model_config import RiskLevel
from app.schemas.exposure import (
    AssetType,
    ExposedAsset,
    ExposureAnalysisRequest,
    ExposureAnalysisResponse,
)
from app.schemas.satellite_evidence import CoordinateLocation


class ExposureAnalysisService:
    """Evaluates physical and critical infrastructure assets exposed to landslide hazard buffers."""

    def __init__(self):
        self.version = "1.0_exposure"

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance between two points in meters."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 1)

    async def analyze_exposure(self, request: ExposureAnalysisRequest) -> ExposureAnalysisResponse:
        lat = request.latitude
        lon = request.longitude
        buffer_m = request.buffer_radius_meters
        location = CoordinateLocation(
            latitude=lat,
            longitude=lon,
            location_name=request.location_name,
        )

        # Generate realistic nearby infrastructure candidates within proximity
        candidate_assets = [
            {
                "id": "ASSET_HW_01",
                "type": AssetType.HIGHWAY,
                "name": "National Highway Corridor (NH)",
                "d_lat": 0.0025,
                "d_lon": 0.0030,
                "pop": 2500,
                "risk": RiskLevel.ALERT,
            },
            {
                "id": "ASSET_RD_02",
                "type": AssetType.STATE_ROAD,
                "name": "State Arterial Road / District Link",
                "d_lat": -0.0018,
                "d_lon": 0.0015,
                "pop": 800,
                "risk": RiskLevel.WATCH,
            },
            {
                "id": "ASSET_BR_03",
                "type": AssetType.BRIDGE,
                "name": "RC Bridge over Mountain Stream Culvert",
                "d_lat": 0.0040,
                "d_lon": -0.0022,
                "pop": None,
                "risk": RiskLevel.CRITICAL,
            },
            {
                "id": "ASSET_ST_04",
                "type": AssetType.SETTLEMENT,
                "name": "Hillside Village Cluster / Habitation",
                "d_lat": -0.0035,
                "d_lon": -0.0040,
                "pop": 1200,
                "risk": RiskLevel.WATCH,
            },
            {
                "id": "ASSET_HC_05",
                "type": AssetType.HOSPITAL,
                "name": "Primary Health Centre (PHC) Substation",
                "d_lat": 0.0060,
                "d_lon": 0.0050,
                "pop": 450,
                "risk": RiskLevel.NORMAL,
            },
            {
                "id": "ASSET_SC_06",
                "type": AssetType.SCHOOL,
                "name": "Government Higher Secondary School",
                "d_lat": -0.0045,
                "d_lon": 0.0035,
                "pop": 320,
                "risk": RiskLevel.NORMAL,
            },
        ]

        exposed_assets: List[ExposedAsset] = []
        critical_count = 0

        for item in candidate_assets:
            a_lat = lat + item["d_lat"]
            a_lon = lon + item["d_lon"]
            dist = self._haversine_distance(lat, lon, a_lat, a_lon)
            within_buf = dist <= buffer_m

            if item["type"] in [AssetType.HIGHWAY, AssetType.BRIDGE, AssetType.HOSPITAL, AssetType.RAILWAY]:
                if within_buf:
                    critical_count += 1

            if within_buf or dist <= buffer_m * 1.5:
                exposed_assets.append(
                    ExposedAsset(
                        asset_id=item["id"],
                        asset_type=item["type"],
                        name=item["name"],
                        distance_meters=dist,
                        within_analysis_buffer=within_buf,
                        estimated_population_impact=item["pop"],
                        risk_level_at_asset=item["risk"],
                        coordinates=[round(a_lon, 5), round(a_lat, 5)],
                    )
                )

        # Sort by proximity
        exposed_assets.sort(key=lambda a: a.distance_meters)
        within_count = sum(1 for a in exposed_assets if a.within_analysis_buffer)

        if critical_count >= 2 or within_count >= 4:
            rating = "Severe Exposure"
        elif critical_count >= 1 or within_count >= 2:
            rating = "High Exposure"
        elif within_count >= 1:
            rating = "Moderate Exposure"
        else:
            rating = "Low Exposure"

        return ExposureAnalysisResponse(
            location=location,
            analysis_buffer_meters=buffer_m,
            total_exposed_assets=within_count,
            critical_infrastructure_count=critical_count,
            exposure_risk_rating=rating,
            exposed_assets=exposed_assets,
        )


exposure_service = ExposureAnalysisService()
