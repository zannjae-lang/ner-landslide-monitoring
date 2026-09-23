from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.config.model_config import RiskLevel
from app.core.logger import logger
from app.models.alert import AlertRecord
from app.models.observation import EnvironmentalObservation
from app.models.prediction import PredictionRecord
from app.schemas.predictions import (
    Model1FeatureInput,
    Model2FeatureInput,
    PredictionRunRequest,
    RiskEngineResult,
)
from app.services.computer_vision.cv_service import cv_service
from app.services.data_collectors.collector_manager import collector_manager
from app.services.feature_extraction.feature_pipeline import feature_pipeline
from app.services.ml_models.model1_service import model1_service
from app.services.ml_models.model2_service import model2_service
from app.services.risk_engine.risk_engine import risk_engine


class PredictionPipeline:
    """Orchestrates end-to-end telemetry collection, dual-model inference, risk fusion, and persistence."""

    async def execute_prediction(
        self,
        request: PredictionRunRequest,
        db: Optional[Session] = None,
        persist: bool = True,
    ) -> RiskEngineResult:
        now_utc = datetime.now(timezone.utc)
        lat = request.latitude
        lon = request.longitude

        # 1. Validate coordinates
        is_valid_coord, coord_warning = feature_pipeline.validate_coordinates(lat, lon)
        if not is_valid_coord:
            raise ValueError(coord_warning)

        # 2. Extract Model 1 features (utilizes live GEE Copernicus DEM & Sentinel-2 if active)
        if request.model1_features is not None:
            m1_features = request.model1_features
            telemetry_meta = {}
        else:
            m1_features, telemetry_meta = await feature_pipeline.derive_live_terrain_features(lat, lon)

        # 3. Execute Model 1 Inference
        m1_output = model1_service.predict(m1_features)

        # 4. Acquire Environmental Weather Data
        if request.model2_features is not None:
            m2_features = request.model2_features
            rain_24h = m2_features.Rainfall_24h
            obs_timestamp = request.observation_time or now_utc
            obs_source = "custom_input"
            obs_obj = None
        else:
            norm_obs = await collector_manager.get_observation(lat, lon)
            m2_features = feature_pipeline.assemble_model2_features(norm_obs, m1_output.susceptibility_probability)
            rain_24h = norm_obs.rainfall_24h_mm
            obs_timestamp = norm_obs.observed_at
            obs_source = norm_obs.provider_id
            obs_obj = norm_obs

        # 5. Execute Model 2 Inference
        m2_output = model2_service.predict(
            m2_features,
            data_timestamp=obs_timestamp,
        )

        # 6. Computer Vision Evaluation (Placeholder)
        cv_output = cv_service.process_image()

        # 7. Execute Risk Engine 2.0
        location_info = {
            "id": request.location_id,
            "name": request.location_name,
            "state": request.state,
            "district": request.district,
            "latitude": lat,
            "longitude": lon,
        }
        risk_result = risk_engine.compute_risk(
            model1_result=m1_output,
            model2_result=m2_output,
            rainfall_24h_mm=rain_24h,
            data_timestamp=obs_timestamp,
            location_info=location_info,
            cv_result=cv_output,
        )

        if coord_warning:
            risk_result.warnings.append(coord_warning)
        if telemetry_meta.get("dem_source") == "gee_copernicus_dem_glo30":
            risk_result.warnings.append("Terrain elevation verified via Google Earth Engine Copernicus DEM GLO-30.")
        if telemetry_meta.get("ndvi_source") == "gee_sentinel2_optical":
            risk_result.warnings.append("Vegetation indices derived via live Sentinel-2 Optical harmonized imagery.")

        # 8. Persist to Database if requested and db session provided
        if persist and db is not None and request.location_id:
            try:
                # Save observation
                if obs_obj:
                    db_obs = EnvironmentalObservation(
                        location_id=request.location_id,
                        source=obs_source,
                        observed_at=obs_timestamp,
                        received_at=now_utc,
                        rainfall_1h_mm=obs_obj.rainfall_1h_mm,
                        rainfall_3h_mm=obs_obj.rainfall_3h_mm,
                        rainfall_6h_mm=obs_obj.rainfall_6h_mm,
                        rainfall_12h_mm=obs_obj.rainfall_12h_mm,
                        rainfall_24h_mm=obs_obj.rainfall_24h_mm,
                        rainfall_3day_mm=obs_obj.rainfall_3day_mm,
                        rainfall_7day_mm=obs_obj.rainfall_7day_mm,
                        soil_moisture_layer_1=obs_obj.soil_moisture_layer_1,
                        soil_moisture_layer_2=obs_obj.soil_moisture_layer_2,
                        temperature_c=obs_obj.temperature_c,
                        humidity_percent=obs_obj.humidity_percent,
                        quality_status=obs_obj.quality_status,
                    )
                    db.add(db_obs)

                # Save prediction
                db_pred = PredictionRecord(
                    location_id=request.location_id,
                    prediction_timestamp=now_utc,
                    model1_probability=m1_output.susceptibility_probability,
                    model1_class=m1_output.susceptibility_class.value,
                    model2_probability=m2_output.dynamic_probability,
                    warning_candidate=m2_output.warning_candidate,
                    rainfall_24h_mm=risk_result.rainfall_24h_mm,
                    rainfall_class=risk_result.rainfall_class.value,
                    rainfall_adjustment=risk_result.rainfall_adjustment,
                    combined_risk_score=risk_result.combined_risk_score,
                    final_risk=risk_result.final_risk.value,
                    engine_version=risk_result.engine_version,
                    data_status=risk_result.data_status.value,
                    data_age_hours=risk_result.data_age_hours,
                    is_stale=risk_result.is_stale,
                    prototype_flag=True,
                    operational_validation=False,
                    details_json=risk_result.model_dump(mode="json"),
                )
                db.add(db_pred)
                db.flush()

                # Generate Alert if severity >= Watch
                if risk_result.final_risk in [RiskLevel.WATCH, RiskLevel.ALERT, RiskLevel.CRITICAL]:
                    alert_title = f"{risk_result.final_risk.value} Threat: {request.location_name or 'Station'} ({request.state})"
                    alert_msg = (
                        f"Prototype risk score reached {risk_result.combined_risk_score:.2f} ({risk_result.final_risk.value}). "
                        f"24h Rainfall: {risk_result.rainfall_24h_mm:.1f}mm ({risk_result.rainfall_class.value}). "
                        f"Susceptibility: {m1_output.susceptibility_class.value} ({m1_output.susceptibility_percent:.1f}%). "
                        f"Dynamic Warning Candidate: {'Yes' if m2_output.warning_candidate else 'No'}."
                    )
                    db_alert = AlertRecord(
                        location_id=request.location_id,
                        source_prediction_id=db_pred.id,
                        severity=risk_result.final_risk.value,
                        title=alert_title,
                        message=alert_msg,
                        score=risk_result.combined_risk_score,
                        rainfall_24h_mm=risk_result.rainfall_24h_mm,
                        status="active",
                    )
                    db.add(db_alert)

                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to persist prediction / alert records: {e}")

        return risk_result


prediction_pipeline = PredictionPipeline()
