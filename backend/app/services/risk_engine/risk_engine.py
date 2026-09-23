from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.config.model_config import (
    DataQualityStatus,
    RainfallClass,
    RiskLevel,
)
from app.config.settings import settings
from app.core.logger import logger
from app.schemas.predictions import (
    ComputerVisionOutput,
    Model1PredictionOutput,
    Model2PredictionOutput,
    RiskEngineResult,
)


class RiskEngine:
    """Risk Engine 2.0 for Multi-Factor Landslide Threat Assessment."""

    def __init__(self):
        self.version = "2.0"

    def classify_rainfall(self, rainfall_24h_mm: float) -> Tuple[RainfallClass, float]:
        """Classify 24h rainfall and compute additive risk delta."""
        if rainfall_24h_mm >= settings.RAINFALL_THRESHOLD_CRITICAL_MM:
            return RainfallClass.CRITICAL, settings.RAINFALL_DELTA_CRITICAL
        elif rainfall_24h_mm >= settings.RAINFALL_THRESHOLD_HIGH_MM:
            return RainfallClass.HIGH, settings.RAINFALL_DELTA_HIGH
        elif rainfall_24h_mm >= settings.RAINFALL_THRESHOLD_ELEVATED_MM:
            return RainfallClass.ELEVATED, settings.RAINFALL_DELTA_ELEVATED
        return RainfallClass.LOW, settings.RAINFALL_DELTA_LOW

    def classify_risk_score(self, score: float) -> RiskLevel:
        """Map combined risk score to prototype risk band."""
        if score >= settings.RISK_THRESHOLD_CRITICAL:
            return RiskLevel.CRITICAL
        elif score >= settings.RISK_THRESHOLD_ALERT:
            return RiskLevel.ALERT
        elif score >= settings.RISK_THRESHOLD_WATCH:
            return RiskLevel.WATCH
        return RiskLevel.NORMAL

    def compute_risk(
        self,
        model1_result: Optional[Model1PredictionOutput],
        model2_result: Optional[Model2PredictionOutput],
        rainfall_24h_mm: float,
        data_timestamp: Optional[datetime] = None,
        location_info: Optional[Dict[str, Any]] = None,
        cv_result: Optional[ComputerVisionOutput] = None,
    ) -> RiskEngineResult:
        now_utc = datetime.now(timezone.utc)
        location_info = location_info or {}
        warnings: List[str] = []
        missing_fields: List[str] = []

        # Data Freshness Check
        if data_timestamp:
            if data_timestamp.tzinfo is None:
                data_timestamp = data_timestamp.replace(tzinfo=timezone.utc)
            data_age_hours = (now_utc - data_timestamp).total_seconds() / 3600.0
        else:
            data_age_hours = 0.0

        is_stale = data_age_hours > settings.MAX_DATA_AGE_HOURS

        if is_stale:
            data_status = DataQualityStatus.STALE
            warnings.append(
                f"Data is {data_age_hours:.1f} hours old, which exceeds the max freshness limit of {settings.MAX_DATA_AGE_HOURS} hours."
            )
        else:
            data_status = DataQualityStatus.FRESH

        # Check missing components
        if model1_result is None:
            missing_fields.append("model1_susceptibility")
        if model2_result is None:
            missing_fields.append("model2_dynamic")

        if missing_fields:
            data_status = DataQualityStatus.UNAVAILABLE
            warnings.append(f"Missing essential predictive inputs: {', '.join(missing_fields)}")
            
            # Safe Fallback with uncalibrated base
            p_susc = model1_result.susceptibility_probability if model1_result else 0.0
            p_dyn = model2_result.dynamic_probability if model2_result else 0.0
        else:
            p_susc = model1_result.susceptibility_probability
            p_dyn = model2_result.dynamic_probability

        # Calculate Rainfall Adjustment
        rain_class, rain_delta = self.classify_rainfall(rainfall_24h_mm)

        # Multi-factor Fusion Formula:
        # Score = (0.45 * P_susc) + (0.55 * P_dyn) + Delta_rain
        raw_score = (
            (settings.RISK_SUSCEPTIBILITY_WEIGHT * p_susc)
            + (settings.RISK_DYNAMIC_WEIGHT * p_dyn)
            + rain_delta
        )
        combined_score = max(0.0, min(1.0, raw_score))
        final_risk = self.classify_risk_score(combined_score)

        if combined_score >= 0.999:
            warnings.append(
                "Combined score reached saturation (1.0). This represents mathematical upper bound, NOT 100% empirical certainty."
            )

        return RiskEngineResult(
            engine_version=self.version,
            location_id=location_info.get("id"),
            location_name=location_info.get("name"),
            state=location_info.get("state"),
            district=location_info.get("district"),
            latitude=location_info.get("latitude"),
            longitude=location_info.get("longitude"),
            model1_result=model1_result,
            model2_result=model2_result,
            computer_vision_result=cv_result or ComputerVisionOutput(),
            rainfall_24h_mm=round(rainfall_24h_mm, 2),
            rainfall_class=rain_class,
            rainfall_adjustment=rain_delta,
            combined_risk_score=round(combined_score, 4),
            final_risk=final_risk,
            data_status=data_status,
            data_age_hours=round(data_age_hours, 2),
            is_stale=is_stale,
            missing_fields=missing_fields,
            warnings=warnings,
            prediction_timestamp=now_utc,
            prototype_warning="PROTOTYPE ONLY: This risk score is uncalibrated research output and NOT an official government disaster warning.",
            operational_validation=False,
        )


risk_engine = RiskEngine()
