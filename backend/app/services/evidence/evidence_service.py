import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.config.model_config import RainfallClass, RiskLevel, SusceptibilityClass
from app.core.logger import logger
from app.schemas.evidence import (
    CoordinateLocation,
    EvidenceConfidence,
    EvidenceEvaluationRequest,
    EvidenceFactor,
    EvidenceFactorType,
    EvidenceSummaryResponse,
)
from app.schemas.predictions import PredictionRunRequest
from app.schemas.satellite_evidence import EvidenceQualityStatus
from app.services.data_collectors.collector_manager import collector_manager
from app.services.ml_models.prediction_pipeline import prediction_pipeline
from app.services.satellite.s1_change_service import s1_change_service
from app.services.satellite.s2_disturbance_service import s2_disturbance_service


class EvidenceFusionService:
    """Multi-source Evidence Aggregator & Provenance Engine for Decision Support.

    Fuses:
    1. Static Terrain Susceptibility (Model 1)
    2. Dynamic Meteorological Trigger (Model 2)
    3. Physical 24h & 3-day Rainfall Exceedance
    4. Dual-Layer Soil Moisture Saturation Index
    5. Sentinel-1 SAR Backscatter Anomaly Index (GEE C-band)
    6. Sentinel-2 Optical NDVI Vegetation Loss Index (GEE MSI)
    """

    def __init__(self):
        self.version = "1.0_evidence_fusion"
        # Configured heuristic weights (normalized sum = 1.0)
        self.weights = {
            "model1_susceptibility": 0.25,
            "model2_dynamic": 0.30,
            "rainfall_physical": 0.20,
            "soil_moisture": 0.10,
            "sar_change": 0.10,
            "optical_ndvi": 0.05,
        }

    async def evaluate_evidence(
        self,
        request: EvidenceEvaluationRequest,
    ) -> EvidenceSummaryResponse:
        lat = request.latitude
        lon = request.longitude
        location = CoordinateLocation(
            latitude=lat,
            longitude=lon,
            location_name=request.location_name,
            state=request.state,
            district=request.district,
        )

        factors: List[EvidenceFactor] = []
        supporting_factors: List[str] = []
        conflicting_factors: List[str] = []
        missing_factors: List[str] = []
        provenance: Dict[str, Any] = {"version": self.version}

        # 1. Run Baseline Prediction Pipeline (Model 1 -> Model 2 -> Risk Engine 2.0)
        pred_req = PredictionRunRequest(
            location_id=request.location_id,
            location_name=request.location_name,
            state=request.state,
            district=request.district,
            latitude=lat,
            longitude=lon,
        )
        
        try:
            risk_result = await prediction_pipeline.execute_prediction(pred_req, persist=False)
            m1 = risk_result.model1_result
            m2 = risk_result.model2_result
            m1_prob = m1.susceptibility_probability if m1 else 0.0
            m1_class = m1.susceptibility_class if m1 else SusceptibilityClass.VERY_LOW
            m2_prob = m2.dynamic_probability if m2 else 0.0
            m2_candidate = m2.warning_candidate if m2 else False
            rain_24h = risk_result.rainfall_24h_mm
            rain_class = risk_result.rainfall_class
            provenance["risk_engine_2_score"] = risk_result.combined_risk_score
            provenance["risk_engine_2_band"] = risk_result.final_risk.value
        except Exception as e:
            logger.warning(f"Prediction pipeline failed during evidence evaluation: {e}")
            m1_prob = 0.0
            m1_class = SusceptibilityClass.VERY_LOW
            m2_prob = 0.0
            m2_candidate = False
            rain_24h = 0.0
            rain_class = RainfallClass.LOW
            missing_factors.append("Model 1 & 2 inference unavailable")

        # Factor 1: Model 1 Static Susceptibility
        f1_score = m1_prob
        f1_supporting = f1_score >= 0.39
        factors.append(
            EvidenceFactor(
                factor_id="F1_STATIC_SUSCEPTIBILITY",
                factor_type=EvidenceFactorType.TERRAIN_SUSCEPTIBILITY,
                source="Model 1 XGBoost (Static Susceptibility)",
                parameter="susceptibility_probability",
                observed_value=round(m1_prob, 4),
                indicator_score=round(f1_score, 4),
                weight=self.weights["model1_susceptibility"],
                status=EvidenceQualityStatus.VALID if m1 else EvidenceQualityStatus.NOT_AVAILABLE,
                interpretation=f"Terrain natural susceptibility is {m1_class.value} ({m1_prob * 100.0:.1f}%).",
                is_supporting=f1_supporting,
            )
        )
        if f1_supporting:
            supporting_factors.append(f"High inherent terrain susceptibility ({m1_class.value})")
        else:
            conflicting_factors.append("Terrain susceptibility is naturally low")

        # Factor 2: Model 2 Dynamic Early Warning
        f2_score = m2_prob
        f2_supporting = m2_candidate
        factors.append(
            EvidenceFactor(
                factor_id="F2_DYNAMIC_FORECAST",
                factor_type=EvidenceFactorType.RAINFALL_TRIGGER,
                source="Model 2 XGBoost (Temporal Candidate)",
                parameter="dynamic_probability",
                observed_value=round(m2_prob, 4),
                indicator_score=round(f2_score, 4),
                weight=self.weights["model2_dynamic"],
                status=EvidenceQualityStatus.VALID if m2 else EvidenceQualityStatus.NOT_AVAILABLE,
                interpretation=f"Dynamic meteorological probability is {m2_prob * 100.0:.1f}% (Candidate: {'Yes' if m2_candidate else 'No'}).",
                is_supporting=f2_supporting,
                verification_required=m2_candidate,
            )
        )
        if f2_supporting:
            supporting_factors.append("Dynamic rainfall-soil moisture model candidate threshold exceeded")

        # Factor 3: Physical Rainfall Trigger (24h accumulation threshold exceedance)
        # Normalized score: 0 to 100mm mapped to 0.0 - 1.0
        f3_score = min(1.0, rain_24h / 100.0)
        f3_supporting = rain_24h >= 35.0
        factors.append(
            EvidenceFactor(
                factor_id="F3_PHYSICAL_RAINFALL",
                factor_type=EvidenceFactorType.RAINFALL_TRIGGER,
                source="Live Precipitation Sensor / Ingestion",
                parameter="rainfall_24h_mm",
                observed_value=round(rain_24h, 1),
                baseline_value=35.0,  # Threshold for High rainfall
                difference=round(rain_24h - 35.0, 1),
                indicator_score=round(f3_score, 4),
                weight=self.weights["rainfall_physical"],
                status=EvidenceQualityStatus.VALID,
                interpretation=f"24h precipitation is {rain_24h:.1f}mm ({rain_class.value} category).",
                is_supporting=f3_supporting,
                verification_required=rain_24h >= 65.0,
            )
        )
        if f3_supporting:
            supporting_factors.append(f"Heavy 24h precipitation accumulation ({rain_24h:.1f}mm)")
        else:
            conflicting_factors.append(f"24h rainfall is moderate/low ({rain_24h:.1f}mm)")

        # Factor 4: Soil Moisture Saturation Index
        try:
            obs = await collector_manager.get_observation(lat, lon)
            sm1 = obs.soil_moisture_layer_1 or 0.25
            sm2 = obs.soil_moisture_layer_2 or 0.28
            avg_sm = (sm1 + sm2) / 2.0
            f4_score = min(1.0, max(0.0, (avg_sm - 0.20) / 0.35))
            f4_supporting = avg_sm >= 0.38
            factors.append(
                EvidenceFactor(
                    factor_id="F4_SOIL_MOISTURE_SATURATION",
                    factor_type=EvidenceFactorType.SOIL_SATURATION,
                    source=f"{obs.provider_id} Volumetric Soil Moisture",
                    parameter="volumetric_fraction_0_28cm",
                    observed_value=round(avg_sm, 3),
                    indicator_score=round(f4_score, 4),
                    weight=self.weights["soil_moisture"],
                    status=EvidenceQualityStatus.VALID,
                    interpretation=f"Subsurface soil moisture saturation is {avg_sm * 100.0:.1f}% volumetric fraction.",
                    is_supporting=f4_supporting,
                )
            )
            if f4_supporting:
                supporting_factors.append(f"High subsurface soil saturation ({avg_sm * 100.0:.1f}%)")
        except Exception as e:
            missing_factors.append(f"Soil moisture reading unavailable: {e}")

        # Factor 5 & 6: Satellite Remote Sensing Evidence (Optional concurrent query)
        s1_res = None
        s2_res = None
        if request.include_satellite_check:
            s1_task = s1_change_service.compute_s1_change(lat, lon)
            s2_task = s2_disturbance_service.compute_s2_disturbance(lat, lon)
            s1_res, s2_res = await asyncio.gather(s1_task, s2_task, return_exceptions=True)

        # Process Sentinel-1 SAR change factor
        if isinstance(s1_res, Exception) or s1_res is None or not getattr(s1_res, "is_valid_comparison", False):
            missing_factors.append("Sentinel-1 SAR surface change comparison unavailable or insufficient passes")
            factors.append(
                EvidenceFactor(
                    factor_id="F5_SAR_SURFACE_CHANGE",
                    factor_type=EvidenceFactorType.SAR_SURFACE_CHANGE,
                    source="Sentinel-1 C-band SAR GRD",
                    parameter="delta_vv_db",
                    observed_value=None,
                    indicator_score=0.0,
                    weight=self.weights["sar_change"],
                    status=getattr(s1_res, "quality_status", EvidenceQualityStatus.NOT_AVAILABLE) if s1_res else EvidenceQualityStatus.NOT_AVAILABLE,
                    interpretation="No geometrically comparable cloud-penetrating SAR observation pair available in recent window.",
                    is_supporting=False,
                )
            )
        else:
            delta_vv = s1_res.delta_vv_db or 0.0
            # A negative backscatter delta (e.g. -2.0 to -5.0 dB) signals surface scarp/roughness variation
            f5_score = min(1.0, max(0.0, abs(delta_vv) / 4.0)) if delta_vv < -0.5 else 0.1
            f5_supporting = delta_vv <= -1.5
            factors.append(
                EvidenceFactor(
                    factor_id="F5_SAR_SURFACE_CHANGE",
                    factor_type=EvidenceFactorType.SAR_SURFACE_CHANGE,
                    source="Sentinel-1 C-band SAR GRD (GEE)",
                    parameter="delta_vv_db",
                    observed_value=delta_vv,
                    difference=delta_vv,
                    indicator_score=round(f5_score, 4),
                    weight=self.weights["sar_change"],
                    status=s1_res.quality_status,
                    interpretation=f"C-band SAR backscatter changed by {delta_vv:+.2f} dB between matching orbit passes.",
                    is_supporting=f5_supporting,
                    verification_required=abs(delta_vv) >= 2.0,
                )
            )
            if f5_supporting:
                supporting_factors.append(f"Significant SAR backscatter shift ({delta_vv:+.2f} dB) detected")
            else:
                conflicting_factors.append(f"SAR backscatter is relatively stable ({delta_vv:+.2f} dB)")

        # Process Sentinel-2 Optical NDVI disturbance factor
        if isinstance(s2_res, Exception) or s2_res is None or not getattr(s2_res, "is_valid_comparison", False):
            missing_factors.append("Sentinel-2 Optical NDVI disturbance comparison cloud-limited or unavailable")
            factors.append(
                EvidenceFactor(
                    factor_id="F6_OPTICAL_NDVI_DISTURBANCE",
                    factor_type=EvidenceFactorType.OPTICAL_VEGETATION_LOSS,
                    source="Sentinel-2 Harmonized MSI (GEE)",
                    parameter="delta_ndvi",
                    observed_value=None,
                    indicator_score=0.0,
                    weight=self.weights["optical_ndvi"],
                    status=getattr(s2_res, "quality_status", EvidenceQualityStatus.LOW_QUALITY) if s2_res else EvidenceQualityStatus.NOT_AVAILABLE,
                    interpretation="Optical vegetation comparison unavailable due to monsoon cloud cover or missing cloud-free scenes.",
                    is_supporting=False,
                )
            )
        else:
            delta_ndvi = s2_res.delta_ndvi or 0.0
            f6_score = min(1.0, max(0.0, abs(delta_ndvi) / 0.30)) if delta_ndvi < -0.05 else 0.05
            f6_supporting = delta_ndvi <= -0.10
            factors.append(
                EvidenceFactor(
                    factor_id="F6_OPTICAL_NDVI_DISTURBANCE",
                    factor_type=EvidenceFactorType.OPTICAL_VEGETATION_LOSS,
                    source="Sentinel-2 Harmonized MSI (GEE)",
                    parameter="delta_ndvi",
                    observed_value=delta_ndvi,
                    difference=delta_ndvi,
                    indicator_score=round(f6_score, 4),
                    weight=self.weights["optical_ndvi"],
                    status=s2_res.quality_status,
                    interpretation=f"Optical NDVI changed by {delta_ndvi:+.3f} between composite periods.",
                    is_supporting=f6_supporting,
                    verification_required=delta_ndvi <= -0.15,
                )
            )
            if f6_supporting:
                supporting_factors.append(f"Vegetation canopy loss detected (NDVI drop of {delta_ndvi:+.3f})")

        # 2. Calculate Weighted Overall Evidence Score & Data Quality Score
        valid_factors = [f for f in factors if f.status in [EvidenceQualityStatus.VALID, EvidenceQualityStatus.REQUIRES_VERIFICATION]]
        total_weight = sum(f.weight for f in valid_factors)
        if total_weight > 0:
            weighted_sum = sum(f.indicator_score * f.weight for f in valid_factors)
            overall_score = round(min(1.0, max(0.0, weighted_sum / total_weight)), 4)
        else:
            overall_score = 0.0

        quality_score = round(len(valid_factors) / max(1, len(factors)), 2)

        # 3. Determine Risk Level & Confidence
        if overall_score >= 0.70:
            evidence_level = RiskLevel.CRITICAL
        elif overall_score >= 0.45:
            evidence_level = RiskLevel.ALERT
        elif overall_score >= 0.25:
            evidence_level = RiskLevel.WATCH
        else:
            evidence_level = RiskLevel.NORMAL

        if quality_score >= 0.80 and len(missing_factors) == 0:
            confidence = EvidenceConfidence.HIGH
        elif quality_score >= 0.50:
            confidence = EvidenceConfidence.MEDIUM
        else:
            confidence = EvidenceConfidence.LOW

        # 4. Formulate Actionable Recommendations
        if evidence_level in [RiskLevel.ALERT, RiskLevel.CRITICAL]:
            rec_action = "Initiate DDMA field verification, review culvert/drainage blockages, and issue regional advisory."
            verif_req = "URGENT: Ground-truth visual inspection of slope crest and toe required within 12 hours."
        elif evidence_level == RiskLevel.WATCH:
            rec_action = "Maintain automated telemetry monitoring; alert local road maintenance teams if rain intensifies."
            verif_req = "Routine patrol inspection along arterial transport corridors."
        else:
            rec_action = "Normal monitoring baseline. Telemetry stations operating within typical seasonal thresholds."
            verif_req = "No immediate field verification required."

        return EvidenceSummaryResponse(
            location=location,
            generated_at=datetime.now(timezone.utc),
            overall_evidence_score=overall_score,
            evidence_level=evidence_level,
            confidence=confidence,
            data_quality_score=quality_score,
            is_provisional=True,
            model1_susceptibility_probability=m1_prob,
            model1_susceptibility_class=m1_class,
            model2_dynamic_probability=m2_prob,
            model2_warning_candidate=m2_candidate,
            rainfall_24h_mm=rain_24h,
            rainfall_class=rain_class,
            factors=factors,
            supporting_factors=supporting_factors,
            conflicting_factors=conflicting_factors,
            missing_factors=missing_factors,
            recommended_action=rec_action,
            verification_requirement=verif_req,
            provenance_trail=provenance,
        )


evidence_service = EvidenceFusionService()
