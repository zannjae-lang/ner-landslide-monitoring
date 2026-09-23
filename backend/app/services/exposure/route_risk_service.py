import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config.model_config import RiskLevel
from app.schemas.exposure import CorridorRiskRequest, CorridorRiskResponse, RouteSegmentRisk
from app.services.data_collectors.collector_manager import collector_manager
from app.services.feature_extraction.feature_pipeline import feature_pipeline
from app.services.ml_models.model1_service import model1_service
from app.services.ml_models.model2_service import model2_service
from app.services.risk_engine.risk_engine import risk_engine


class RouteCorridorRiskService:
    """Evaluates cumulative landslide vulnerability and chokepoints along critical transport arteries across NER."""

    PREDEFINED_CORRIDORS: Dict[str, Dict[str, Any]] = {
        "NH_10_SK": {
            "name": "NH-10 Siliguri — Sevoke — Rangpo — Gangtok",
            "state_corridor": "West Bengal — Sikkim Corridor",
            "total_length_km": 114.0,
            "waypoints": [
                [88.4200, 26.7200, 120.0, 10.0],   # Siliguri
                [88.4700, 26.8800, 210.0, 24.0],   # Sevoke Coronation Bridge
                [88.5100, 27.0500, 420.0, 34.0],   # Teesta Bazaar
                [88.5400, 27.1800, 680.0, 38.0],   # Rangpo Sikkim Gate
                [88.5900, 27.2600, 1150.0, 32.0],  # Singtam
                [88.6065, 27.3389, 1650.0, 30.0],  # Gangtok
            ],
            "known_chokepoints": ["29th Mile Teesta Slide Zone", "Setijhora Gorge", "Baluakhola Crossing", "Rangpo Checkpost Cutting"],
        },
        "NH_29_NL": {
            "name": "NH-29 Dimapur — Chumukedima — Kohima",
            "state_corridor": "Assam — Nagaland Lifeline",
            "total_length_km": 74.0,
            "waypoints": [
                [93.7200, 25.9000, 145.0, 8.0],    # Dimapur
                [93.7800, 25.8200, 320.0, 28.0],   # Chumukedima Gate
                [93.9200, 25.7500, 840.0, 41.0],   # Pagla Pahar Rockfall Zone
                [94.0200, 25.7000, 1180.0, 36.0],  # Phesama
                [94.1086, 25.6751, 1444.0, 32.0],  # Kohima
            ],
            "known_chokepoints": ["Pagla Pahar Debris Slide", "Old KMC Dumping Ground Slip", "Phesama Sinking Zone"],
        },
        "NH_06_ML_AS": {
            "name": "NH-06 Shillong — Jowai — Silchar",
            "state_corridor": "Meghalaya — Assam (Barak Valley) Lifeline",
            "total_length_km": 218.0,
            "waypoints": [
                [91.8933, 25.5788, 1525.0, 22.0],  # Shillong
                [92.2100, 25.4400, 1380.0, 26.0],  # Jowai
                [92.3800, 25.1800, 820.0, 37.0],   # Sonapur Tunnel Zone
                [92.6500, 24.9500, 310.0, 28.0],   # Kalain
                [92.7900, 24.8200, 35.0, 9.0],     # Silchar
            ],
            "known_chokepoints": ["Sonapur Tunnel Mudflow Sector", "Lumshnong Limestone Slip", "Khliehriat Hillock Cuttings"],
        },
        "NH_102_MN": {
            "name": "NH-102 Imphal — Pallel — Moreh",
            "state_corridor": "Manipur — Myanmar International Corridor",
            "total_length_km": 109.0,
            "waypoints": [
                [93.9368, 24.8170, 786.0, 12.0],   # Imphal
                [93.9800, 24.5300, 810.0, 18.0],   # Thoubal
                [94.0100, 24.4500, 890.0, 35.0],   # Pallel Hill Start
                [94.1800, 24.3200, 1250.0, 39.0],  # Tengnoupal Peak
                [94.3000, 24.2400, 340.0, 15.0],   # Moreh Border
            ],
            "known_chokepoints": ["Tengnoupal Crest Debris Slips", "Pallel Zig-Zag Cuttings", "Lokchao Bridge Flank"],
        },
    }

    def list_available_corridors(self) -> List[Dict[str, Any]]:
        return [
            {
                "corridor_id": cid,
                "corridor_name": data["name"],
                "state": data["state_corridor"],
                "state_corridor": data["state_corridor"],
                "total_length_km": data["total_length_km"],
                "length_km": data["total_length_km"],
                "known_chokepoints": data["known_chokepoints"],
                "polyline_coordinates": [[p[1], p[0]] for p in data["waypoints"]],  # [lat, lon] for Leaflet
                "risk_level": "Alert" if "10" in cid or "29" in cid else "Watch",
                "high_risk_segments_count": 2 if "10" in cid or "29" in cid else 1,
                "total_segments": len(data["waypoints"]) - 1,
            }
            for cid, data in self.PREDEFINED_CORRIDORS.items()
        ]

    async def evaluate_corridor_risk(self, request: CorridorRiskRequest) -> CorridorRiskResponse:
        cid = request.corridor_id or "NH_10_SK"
        if cid in self.PREDEFINED_CORRIDORS:
            meta = self.PREDEFINED_CORRIDORS[cid]
            c_name = meta["name"]
            s_corridor = meta["state_corridor"]
            tot_len = meta["total_length_km"]
            chokepoints = meta["known_chokepoints"]
            waypoints = meta["waypoints"]
        else:
            c_name = request.corridor_name or "Custom Transport Corridor"
            s_corridor = "Custom User Route"
            chokepoints = ["Custom Corridor Sector"]
            tot_len = 50.0
            if request.polyline_coordinates and len(request.polyline_coordinates) >= 2:
                waypoints = [[p[0], p[1], 1000.0, 25.0] for p in request.polyline_coordinates]
            else:
                waypoints = self.PREDEFINED_CORRIDORS["NH_10_SK"]["waypoints"]

        segments: List[RouteSegmentRisk] = []
        high_risk_count = 0
        max_risk = 0.0
        total_risk = 0.0

        for i in range(len(waypoints) - 1):
            p1 = waypoints[i]
            p2 = waypoints[i + 1]

            mid_lon = (p1[0] + p2[0]) / 2.0
            mid_lat = (p1[1] + p2[1]) / 2.0
            elev = (p1[2] + p2[2]) / 2.0
            slope = (p1[3] + p2[3]) / 2.0

            # Distance approx in km
            d_lon = math.radians(p2[0] - p1[0]) * math.cos(math.radians(mid_lat))
            d_lat = math.radians(p2[1] - p1[1])
            seg_len = round(math.sqrt(d_lat**2 + d_lon**2) * 6371.0, 1)
            seg_len = max(1.0, seg_len)

            # Model 1 & Model 2 & Risk Engine inference on segment midpoint
            m1_in = feature_pipeline.derive_terrain_features(
                latitude=mid_lat,
                longitude=mid_lon,
                elevation_override=elev,
                slope_override=slope,
            )
            m1_out = model1_service.predict(m1_in)

            obs = await collector_manager.get_observation(mid_lat, mid_lon)
            m2_in = feature_pipeline.assemble_model2_features(obs, m1_out.susceptibility_probability)
            m2_out = model2_service.predict(m2_in, data_timestamp=obs.observed_at)

            risk_out = risk_engine.compute_risk(
                model1_result=m1_out,
                model2_result=m2_out,
                rainfall_24h_mm=obs.rainfall_24h_mm,
                data_timestamp=obs.observed_at,
            )

            score = risk_out.combined_risk_score
            level = risk_out.final_risk
            total_risk += score
            if score > max_risk:
                max_risk = score

            is_high = level in [RiskLevel.ALERT, RiskLevel.CRITICAL]
            if is_high:
                high_risk_count += 1

            cp_warn = None
            if i < len(chokepoints):
                cp_warn = f"Identified Historical Chokepoint: {chokepoints[i]}"

            segments.append(
                RouteSegmentRisk(
                    segment_index=i + 1,
                    start_coordinates=[p1[0], p1[1]],
                    end_coordinates=[p2[0], p2[1]],
                    length_km=seg_len,
                    elevation_m=round(elev, 1),
                    slope_deg=round(slope, 1),
                    segment_risk_score=score,
                    segment_risk_level=level,
                    rainfall_24h_mm=obs.rainfall_24h_mm,
                    nearby_hotspots_count=1 if is_high else 0,
                    chokepoint_warning=cp_warn,
                )
            )

        avg_risk = round(total_risk / max(1, len(segments)), 4)
        max_risk = round(max_risk, 4)

        if high_risk_count >= 2 or max_risk >= 0.70:
            action = "HIGH CORRIDOR ALERT: Heavy vehicle restriction and pre-positioning of JCB earthmovers recommended."
        elif high_risk_count >= 1 or avg_risk >= 0.40:
            action = "WATCH STATUS: Advise caution to transport operators; monitor rainfall telemetry hourly."
        else:
            action = "NORMAL CORRIDOR TRANSIT: Typical seasonal conditions. No immediate traffic advisories required."

        return CorridorRiskResponse(
            corridor_id=cid,
            corridor_name=c_name,
            state_corridor=s_corridor,
            total_length_km=tot_len,
            total_segments=len(segments),
            high_risk_segments_count=high_risk_count,
            max_segment_risk=max_risk,
            average_segment_risk=avg_risk,
            critical_chokepoints=chokepoints,
            segments=segments,
            recommended_action=action,
            generated_at=datetime.now(timezone.utc),
        )


route_risk_service = RouteCorridorRiskService()
