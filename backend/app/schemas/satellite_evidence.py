from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceQualityStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    LOW_QUALITY = "LOW_QUALITY"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    REQUIRES_VERIFICATION = "REQUIRES_VERIFICATION"


class CoordinateLocation(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    location_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


class SatelliteDatasetMetadata(BaseModel):
    dataset_name: str
    provider: str
    is_available: bool = False
    image_id: Optional[str] = None
    acquisition_timestamp: Optional[datetime] = None
    processing_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    orbit_direction: Optional[str] = None  # ASCENDING / DESCENDING for S1
    relative_orbit_number: Optional[int] = None
    polarization: Optional[List[str]] = None  # VV, VH
    cloud_percentage: Optional[float] = None  # For S2
    available_bands: List[str] = Field(default_factory=list)
    spatial_resolution: Optional[str] = None
    quality_flags: Dict[str, Any] = Field(default_factory=dict)
    error_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SatelliteMetadataResponse(BaseModel):
    location: CoordinateLocation
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: EvidenceQualityStatus
    datasets: Dict[str, SatelliteDatasetMetadata]
    summary_notes: List[str] = Field(default_factory=list)


class Sentinel1ObservationDetail(BaseModel):
    image_id: Optional[str] = None
    acquisition_timestamp: Optional[datetime] = None
    orbit_direction: Optional[str] = None
    relative_orbit_number: Optional[int] = None
    instrument_mode: str = "IW"
    polarization: List[str] = Field(default_factory=list)
    vv_backscatter_db: Optional[float] = None
    vh_backscatter_db: Optional[float] = None


class Sentinel1ChangeResponse(BaseModel):
    location: CoordinateLocation
    dataset: str = "COPERNICUS/S1_GRD"
    provider: str = "google_earth_engine"
    baseline_observation: Optional[Sentinel1ObservationDetail] = None
    recent_observation: Optional[Sentinel1ObservationDetail] = None
    delta_vv_db: Optional[float] = Field(
        None, description="Recent VV minus Baseline VV (dB). Negative indicates backscatter drop."
    )
    delta_vh_db: Optional[float] = Field(
        None, description="Recent VH minus Baseline VH (dB)."
    )
    valid_observations_count: int = 0
    is_valid_comparison: bool = False
    quality_status: EvidenceQualityStatus
    missing_data_reasons: List[str] = Field(default_factory=list)
    freshness_hours: Optional[float] = None
    processing_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scientific_limitations: List[str] = Field(
        default_factory=lambda: [
            "SAR backscatter variations reflect changes in surface roughness, dielectric moisture, and geometric orientation.",
            "Steep Himalayan terrain induces radar shadow, layover, and foreshortening distortions.",
            "Dielectric moisture surges following heavy rain can alter backscatter independent of physical mass displacement.",
            "This metric represents preliminary surface-change evidence and is NOT a confirmed landslide event.",
            "Requires field verification and ground-truth confirmation before operational emergency action.",
        ]
    )
    caveat: str = (
        "Preliminary satellite surface-change evidence only. Uncalibrated indicator independent of ML prediction models."
    )


class Sentinel2CompositeDetail(BaseModel):
    period_start: str
    period_end: str
    image_count: int = 0
    mean_cloud_percentage: float = 0.0
    ndvi_mean: Optional[float] = None
    ndvi_p50: Optional[float] = None
    latest_acquisition_date: Optional[str] = None


class Sentinel2NDVIResponse(BaseModel):
    location: CoordinateLocation
    dataset: str = "COPERNICUS/S2_SR_HARMONIZED"
    provider: str = "google_earth_engine"
    cloud_threshold_percentage: float = 30.0
    baseline_composite: Optional[Sentinel2CompositeDetail] = None
    recent_composite: Optional[Sentinel2CompositeDetail] = None
    delta_ndvi: Optional[float] = Field(
        None, description="Recent NDVI minus Baseline NDVI. Negative indicates vegetation loss/scarp."
    )
    is_valid_comparison: bool = False
    quality_status: EvidenceQualityStatus
    missing_data_reasons: List[str] = Field(default_factory=list)
    processing_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scientific_limitations: List[str] = Field(
        default_factory=lambda: [
            "Optical NDVI reduction can be caused by agricultural harvesting, seasonal phenological drop, wildfire, or clearing.",
            "Persistent monsoon cloud cover in Northeast India limits cloud-free optical acquisition.",
            "Sub-pixel cloud shadow contamination can depress reflectance and mimic canopy disturbance.",
            "This metric represents preliminary vegetation disturbance evidence and NOT guaranteed landslide movement.",
            "Requires ground inspection and correlation with geological terrain factors.",
        ]
    )
    caveat: str = (
        "Preliminary vegetation disturbance evidence only. Uncalibrated indicator independent of ML prediction models."
    )
