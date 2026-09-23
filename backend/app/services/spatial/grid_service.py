import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.config.model_config import NER_STATES, RiskLevel, classify_susceptibility
from app.core.logger import logger
from app.schemas.grid import (
    DistrictRankingItem,
    DistrictRankingResponse,
    GridCell,
    GridHotspotResponse,
    StateRiskSummary,
    StateSummaryResponse,
)
from app.services.data_collectors.collector_manager import collector_manager
from app.services.feature_extraction.feature_pipeline import feature_pipeline
from app.services.ml_models.model1_service import model1_service
from app.services.ml_models.model2_service import model2_service
from app.services.risk_engine.risk_engine import risk_engine


class GridSpatialService:
    """Provides regional spatial grid sampling, hotspot identification, and state/district vulnerability indexing."""

    # Strategic regional grid seeds across all 8 NER states
    REGIONAL_GRID_SEEDS = [
        # Sikkim
        {"id": "SK_01", "name": "Gangtok Ridge", "state": "Sikkim", "district": "East Sikkim", "lat": 27.3389, "lon": 88.6065, "elev": 1650, "slope": 32.0},
        {"id": "SK_02", "name": "Mangan North", "state": "Sikkim", "district": "North Sikkim", "lat": 27.5112, "lon": 88.5284, "elev": 1820, "slope": 38.5},
        {"id": "SK_03", "name": "Namchi South", "state": "Sikkim", "district": "South Sikkim", "lat": 27.1667, "lon": 88.3500, "elev": 1315, "slope": 26.0},
        # Arunachal Pradesh
        {"id": "AR_01", "name": "Itanagar Hills", "state": "Arunachal Pradesh", "district": "Papum Pare", "lat": 27.0844, "lon": 93.6053, "elev": 440, "slope": 22.0},
        {"id": "AR_02", "name": "Tawang Pass", "state": "Arunachal Pradesh", "district": "Tawang", "lat": 27.5861, "lon": 91.8678, "elev": 3048, "slope": 42.0},
        {"id": "AR_03", "name": "Pasighat Foothills", "state": "Arunachal Pradesh", "district": "East Siang", "lat": 28.0667, "lon": 95.3333, "elev": 155, "slope": 18.0},
        {"id": "AR_04", "name": "Bomdila Range", "state": "Arunachal Pradesh", "district": "West Kameng", "lat": 27.2644, "lon": 92.4156, "elev": 2217, "slope": 35.0},
        # Meghalaya
        {"id": "ML_01", "name": "Shillong Peak", "state": "Meghalaya", "district": "East Khasi Hills", "lat": 25.5788, "lon": 91.8933, "elev": 1525, "slope": 28.0},
        {"id": "ML_02", "name": "Cherrapunji Escarpment", "state": "Meghalaya", "district": "East Khasi Hills", "lat": 25.2700, "lon": 91.7300, "elev": 1430, "slope": 44.0},
        {"id": "ML_03", "name": "Tura Hills", "state": "Meghalaya", "district": "West Garo Hills", "lat": 25.5144, "lon": 90.2206, "elev": 650, "slope": 24.0},
        # Nagaland
        {"id": "NL_01", "name": "Kohima Urban Slopes", "state": "Nagaland", "district": "Kohima", "lat": 25.6751, "lon": 94.1086, "elev": 1444, "slope": 34.0},
        {"id": "NL_02", "name": "Mokokchung Ridge", "state": "Nagaland", "district": "Mokokchung", "lat": 26.3244, "lon": 94.5186, "elev": 1325, "slope": 29.0},
        {"id": "NL_03", "name": "Wokha Corridor", "state": "Nagaland", "district": "Wokha", "lat": 26.0989, "lon": 94.2600, "elev": 1313, "slope": 31.0},
        # Mizoram
        {"id": "MZ_01", "name": "Aizawl Slopes", "state": "Mizoram", "district": "Aizawl", "lat": 23.7271, "lon": 92.7176, "elev": 1132, "slope": 36.5},
        {"id": "MZ_02", "name": "Lunglei South", "state": "Mizoram", "district": "Lunglei", "lat": 22.8800, "lon": 92.7300, "elev": 1222, "slope": 33.0},
        {"id": "MZ_03", "name": "Champhai Ridge", "state": "Mizoram", "district": "Champhai", "lat": 23.4756, "lon": 93.3278, "elev": 1678, "slope": 30.0},
        # Manipur
        {"id": "MN_01", "name": "Imphal Valley Edge", "state": "Manipur", "district": "Imphal West", "lat": 24.8170, "lon": 93.9368, "elev": 786, "slope": 14.0},
        {"id": "MN_02", "name": "Noney Tupul Railway Zone", "state": "Manipur", "district": "Noney", "lat": 24.8422, "lon": 93.6214, "elev": 920, "slope": 41.0},
        {"id": "MN_03", "name": "Churachandpur Hills", "state": "Manipur", "district": "Churachandpur", "lat": 24.3333, "lon": 93.6667, "elev": 922, "slope": 27.0},
        # Assam
        {"id": "AS_01", "name": "Guwahati Hills", "state": "Assam", "district": "Kamrup Metropolitan", "lat": 26.1445, "lon": 91.7362, "elev": 105, "slope": 19.0},
        {"id": "AS_02", "name": "Dima Hasao Haflong", "state": "Assam", "district": "Dima Hasao", "lat": 25.1833, "lon": 93.0167, "elev": 680, "slope": 35.0},
        {"id": "AS_03", "name": "Karbi Anglong Slopes", "state": "Assam", "district": "Karbi Anglong", "lat": 26.1167, "lon": 93.5333, "elev": 340, "slope": 21.0},
        # Tripura
        {"id": "TR_01", "name": "Agartala Plains Edge", "state": "Tripura", "district": "West Tripura", "lat": 23.8315, "lon": 91.2868, "elev": 45, "slope": 8.0},
        {"id": "TR_02", "name": "Jampui Hills", "state": "Tripura", "district": "North Tripura", "lat": 23.9500, "lon": 92.2800, "elev": 930, "slope": 26.0},
    ]

    def __init__(self, cache_ttl_seconds: int = 600):
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._cache_ttl = cache_ttl_seconds

    async def compute_spatial_hotspots(
        self,
        state_filter: Optional[str] = None,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
    ) -> GridHotspotResponse:
        cache_key = f"hotspots_{state_filter}_{min_lat}_{max_lat}_{min_lon}_{max_lon}"
        if cache_key in self._cache:
            ts, cached_res = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                return cached_res

        seeds = self.REGIONAL_GRID_SEEDS
        if state_filter:
            seeds = [s for s in seeds if state_filter.lower() in s["state"].lower()]

        if min_lat is not None and max_lat is not None:
            seeds = [s for s in seeds if min_lat <= s["lat"] <= max_lat]
        if min_lon is not None and max_lon is not None:
            seeds = [s for s in seeds if min_lon <= s["lon"] <= max_lon]

        cells: List[GridCell] = []
        state_breakdown: Dict[str, int] = {st: 0 for st in NER_STATES}
        high_threat_count = 0

        # Process grid points concurrently
        sem = asyncio.Semaphore(8)

        async def process_seed(seed: Dict[str, Any]) -> GridCell:
            async with sem:
                lat = seed["lat"]
                lon = seed["lon"]
                elev = float(seed["elev"])
                slope = float(seed["slope"])

                # 1. Derive Model 1 static features
                m1_input = feature_pipeline.derive_terrain_features(
                    latitude=lat,
                    longitude=lon,
                    elevation_override=elev,
                    slope_override=slope,
                )
                m1_res = model1_service.predict(m1_input)

                # 2. Acquire Weather Telemetry
                obs = await collector_manager.get_observation(lat, lon)
                m2_input = feature_pipeline.assemble_model2_features(obs, m1_res.susceptibility_probability)
                m2_res = model2_service.predict(m2_input, data_timestamp=obs.observed_at)

                # 3. Fuse in Risk Engine 2.0
                r_res = risk_engine.compute_risk(
                    model1_result=m1_res,
                    model2_result=m2_res,
                    rainfall_24h_mm=obs.rainfall_24h_mm,
                    data_timestamp=obs.observed_at,
                    location_info={"id": seed["id"], "name": seed["name"], "state": seed["state"], "district": seed["district"]},
                )

                is_hot = r_res.final_risk in [RiskLevel.ALERT, RiskLevel.CRITICAL]
                return GridCell(
                    cell_id=seed["id"],
                    latitude=lat,
                    longitude=lon,
                    state=seed["state"],
                    district=seed["district"],
                    elevation_m=elev,
                    slope_deg=slope,
                    susceptibility_probability=m1_res.susceptibility_probability,
                    susceptibility_class=m1_res.susceptibility_class,
                    dynamic_probability=m2_res.dynamic_probability,
                    combined_risk_score=r_res.combined_risk_score,
                    risk_level=r_res.final_risk,
                    rainfall_24h_mm=r_res.rainfall_24h_mm,
                    is_hotspot=is_hot,
                    data_status=r_res.data_status.value,
                )

        results = await asyncio.gather(*[process_seed(s) for s in seeds])

        for cell in results:
            cells.append(cell)
            state_breakdown[cell.state] = state_breakdown.get(cell.state, 0) + (1 if cell.is_hotspot else 0)
            if cell.is_hotspot:
                high_threat_count += 1

        bbox = {
            "min_lat": min((c.latitude for c in cells), default=21.5),
            "max_lat": max((c.latitude for c in cells), default=29.5),
            "min_lon": min((c.longitude for c in cells), default=89.5),
            "max_lon": max((c.longitude for c in cells), default=97.5),
        }

        response = GridHotspotResponse(
            total_cells=len(cells),
            high_threat_cells=high_threat_count,
            bounding_box=bbox,
            cells=cells,
            state_breakdown=state_breakdown,
        )

        self._cache[cache_key] = (time.time(), response)
        return response

    async def compute_states_summary(self) -> StateSummaryResponse:
        cache_key = "states_summary"
        if cache_key in self._cache:
            ts, cached_res = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                return cached_res

        hotspots_res = await self.compute_spatial_hotspots()
        state_summaries: List[StateRiskSummary] = []

        vulnerability_dict = {
            "Sikkim": ["Teesta River Valley slopes", "NH-10 corridor landslides", "High altitude glacial moraines"],
            "Arunachal Pradesh": ["Trans-Arunachal Highway passes", "Seismic thrust zones", "Steep gorges in Kameng & Siang"],
            "Meghalaya": ["Cherrapunji/Mawsynram high rainfall escarpments", "Shillong bypass cuttings", "Limestone karst terrain"],
            "Nagaland": ["NH-29 Kohima-Dimapur corridor", "Shale bedrock weathering", "Active urban slope creeping"],
            "Mizoram": ["Aizawl steep anticlinal ridges", "Unconsolidated sandstone/shale", "Tropical cyclone induced slides"],
            "Manipur": ["Tupul railway cutting zone", "NH-37 Imphal-Jiribam corridor", "Heavy monsoon saturated soils"],
            "Assam": ["Haflong-Dima Hasao hill section", "Guwahati municipal hillocks", "Brahmaputra bank erosion"],
            "Tripura": ["Jampui Hill range", "Monsoon gully erosion in soft sandstone", "Hillock border road cuttings"],
        }

        for state in NER_STATES:
            state_cells = [c for c in hotspots_res.cells if c.state == state]
            if state_cells:
                max_score = max(c.combined_risk_score for c in state_cells)
                mean_score = sum(c.combined_risk_score for c in state_cells) / len(state_cells)
                high_count = sum(1 for c in state_cells if c.is_hotspot)
                max_rain = max(c.rainfall_24h_mm for c in state_cells)
                
                # Dominant risk band
                if max_score >= 0.75:
                    dom_risk = RiskLevel.CRITICAL
                elif max_score >= 0.50:
                    dom_risk = RiskLevel.ALERT
                elif max_score >= 0.25:
                    dom_risk = RiskLevel.WATCH
                else:
                    dom_risk = RiskLevel.NORMAL
            else:
                max_score = 0.0
                mean_score = 0.0
                high_count = 0
                max_rain = 0.0
                dom_risk = RiskLevel.NORMAL

            state_summaries.append(
                StateRiskSummary(
                    state_name=state,
                    monitored_stations=len(state_cells),
                    high_threat_stations=high_count,
                    max_risk_score=round(max_score, 4),
                    mean_risk_score=round(mean_score, 4),
                    dominant_risk_level=dom_risk,
                    max_rainfall_24h_mm=round(max_rain, 1),
                    primary_vulnerabilities=vulnerability_dict.get(state, ["Monsoon precipitation and steep slopes"]),
                )
            )

        response = StateSummaryResponse(states=state_summaries)
        self._cache[cache_key] = (time.time(), response)
        return response

    async def compute_district_rankings(self) -> DistrictRankingResponse:
        cache_key = "district_rankings"
        if cache_key in self._cache:
            ts, cached_res = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                return cached_res

        hotspots_res = await self.compute_spatial_hotspots()
        district_map: Dict[Tuple[str, str], List[GridCell]] = {}

        for c in hotspots_res.cells:
            key = (c.state, c.district)
            district_map.setdefault(key, []).append(c)

        rankings: List[DistrictRankingItem] = []
        for (state, dist), cells in district_map.items():
            avg_slope = sum(c.slope_deg for c in cells) / len(cells)
            avg_risk = sum(c.combined_risk_score for c in cells) / len(cells)
            max_rain = max(c.rainfall_24h_mm for c in cells)
            high_count = sum(1 for c in cells if c.is_hotspot)
            high_area_pct = round((high_count / len(cells)) * 100.0, 1)

            # Objective composite vulnerability (slope weight 0.35, risk score 0.45, rain 0.20)
            comp_score = round(min(1.0, (avg_risk * 0.45) + (min(45.0, avg_slope) / 45.0 * 0.35) + (min(100.0, max_rain) / 100.0 * 0.20)), 3)

            rankings.append(
                DistrictRankingItem(
                    district=dist,
                    state=state,
                    composite_vulnerability_score=comp_score,
                    high_risk_zone_area_pct=high_area_pct,
                    avg_slope_deg=round(avg_slope, 1),
                    recent_rainfall_24h_mm=round(max_rain, 1),
                    monitored_points=len(cells),
                )
            )

        # Sort descending by composite vulnerability
        rankings.sort(key=lambda r: r.composite_vulnerability_score, reverse=True)
        response = DistrictRankingResponse(total_districts=len(rankings), rankings=rankings)
        self._cache[cache_key] = (time.time(), response)
        return response


grid_service = GridSpatialService()
