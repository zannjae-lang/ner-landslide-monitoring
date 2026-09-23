from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.config.model_config import (
    DataQualityStatus,
    RainfallClass,
    RiskLevel,
    SusceptibilityClass,
)


class Model1FeatureInput(BaseModel):
    elevation: float = Field(..., description="Elevation above sea level in meters (DEM GLO-30)")
    slope: float = Field(..., description="Terrain slope in degrees")
    curvature: float = Field(..., description="Surface profile/plan curvature")
    tpi: float = Field(..., description="Topographic Position Index")
    tri: float = Field(..., description="Terrain Ruggedness Index")
    aspect_sin: float = Field(..., description="Sine of aspect angle")
    aspect_cos: float = Field(..., description="Cosine of aspect angle")
    ndvi_p90: float = Field(..., description="90th percentile NDVI (vegetation density)")
    ndvi_p50: float = Field(..., description="50th percentile NDVI (median vegetation)")
    ndvi_p10: float = Field(..., description="10th percentile NDVI (sparse vegetation)")
    distance_to_road_m: float = Field(..., description="Proximity to nearest road in meters")
    distance_to_drainage_m: float = Field(..., description="Proximity to nearest stream/drainage channel in meters")
    lulc_type: str = Field("Forest", description="Land-use and land-cover category label")


class Model1PredictionOutput(BaseModel):
    model_name: str = "Landslide Susceptibility Model"
    model_version: str = "model1_v1.0"
    susceptibility_probability: float = Field(..., description="Raw XGBoost positive class probability [0.0 - 1.0]")
    susceptibility_percent: float = Field(..., description="Susceptibility percentage")
    susceptibility_class: SusceptibilityClass = Field(..., description="Qualitative susceptibility band")
    threshold: float = 0.39
    is_susceptible: bool
    operational_validation: bool = False
    calibrated: bool = False
    disclaimer: str = "Prototype research candidate. Not calibrated or operationally validated."


class Model2FeatureInput(BaseModel):
    Rainfall_1h: float = Field(..., ge=0.0, description="1-hour accumulated rainfall (mm)")
    Rainfall_3h: float = Field(..., ge=0.0, description="3-hour accumulated rainfall (mm)")
    Rainfall_6h: float = Field(..., ge=0.0, description="6-hour accumulated rainfall (mm)")
    Rainfall_12h: float = Field(..., ge=0.0, description="12-hour accumulated rainfall (mm)")
    Rainfall_24h: float = Field(..., ge=0.0, description="24-hour accumulated rainfall (mm)")
    Rainfall_3day: float = Field(..., ge=0.0, description="3-day accumulated rainfall (mm)")
    Rainfall_7day: float = Field(..., ge=0.0, description="7-day accumulated rainfall (mm)")
    susceptibility_probability: float = Field(..., ge=0.0, le=1.0, description="Model 1 static susceptibility score")
    soil_moisture_layer_1: float = Field(..., description="Surface volumetric soil moisture (0-7 cm)")
    soil_moisture_layer_2: float = Field(..., description="Root-zone volumetric soil moisture (7-28 cm)")


class Model2PredictionOutput(BaseModel):
    model_name: str = "Dynamic Landslide Early Warning Model"
    model_version: str = "model2_v1.0_temporal_candidate"
    dynamic_probability: float = Field(..., description="Dynamic warning probability candidate [0.0 - 1.0]")
    warning_candidate: bool = Field(..., description="True if dynamic probability >= threshold")
    threshold: float = 0.10
    operational_validation: bool = False
    calibrated: bool = False
    data_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_age_hours: Optional[float] = None
    data_quality: DataQualityStatus = DataQualityStatus.FRESH
    disclaimer: str = "Research prototype. Temporal candidate model uncalibrated for operational warning."


class ComputerVisionOutput(BaseModel):
    module_name: str = "Computer Vision Landslide Detector"
    status: str = "Unavailable"
    evidence_probability: Optional[float] = None
    is_operational: bool = False
    message: str = "CV module is currently inactive/optional. No visual evidence fused into score."


class RiskEngineResult(BaseModel):
    engine_version: str = "2.0"
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Model components
    model1_result: Optional[Model1PredictionOutput] = None
    model2_result: Optional[Model2PredictionOutput] = None
    computer_vision_result: Optional[ComputerVisionOutput] = None

    # Environmental indicators
    rainfall_24h_mm: float
    rainfall_class: RainfallClass
    rainfall_adjustment: float
    
    # Combined Fusion Output
    combined_risk_score: float = Field(..., description="Fused score clipped to [0.0, 1.0]")
    final_risk: RiskLevel = Field(..., description="Normal, Watch, Alert, or Critical")
    
    # Status & Freshness
    data_status: DataQualityStatus
    data_age_hours: float
    is_stale: bool = False
    missing_fields: List[str] = []
    warnings: List[str] = []
    
    # Audit & Ethics
    prediction_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prototype_warning: str = "PROTOTYPE ONLY: This risk score is uncalibrated research output and NOT an official government disaster warning."
    operational_validation: bool = False


class PredictionRunRequest(BaseModel):
    location_id: Optional[str] = None
    latitude: float
    longitude: float
    state: str = "Assam"
    district: Optional[str] = None
    location_name: Optional[str] = "Observation Station"
    model1_features: Optional[Model1FeatureInput] = None
    model2_features: Optional[Model2FeatureInput] = None
    observation_time: Optional[datetime] = None
    use_live_collectors: bool = True
