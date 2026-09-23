"""Centralized Model and Risk Engine Constants & Configurations."""
from typing import Dict, List, Tuple
from enum import Enum


class SusceptibilityClass(str, Enum):
    VERY_LOW = "Very Low"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"


class RiskLevel(str, Enum):
    NORMAL = "Normal"
    WATCH = "Watch"
    ALERT = "Alert"
    CRITICAL = "Critical"


class RainfallClass(str, Enum):
    LOW = "Low"
    ELEVATED = "Elevated"
    HIGH = "High"
    CRITICAL = "Critical"


class DataQualityStatus(str, Enum):
    FRESH = "Fresh"
    STALE = "Stale"
    UNAVAILABLE = "Unavailable"
    PROVISIONAL = "Provisional/Demo"


# Model 1 Features in strict order
MODEL1_FEATURE_ORDER: List[str] = [
    "elevation",
    "slope",
    "curvature",
    "tpi",
    "tri",
    "aspect_sin",
    "aspect_cos",
    "ndvi_p90",
    "ndvi_p50",
    "ndvi_p10",
    "distance_to_road_m",
    "distance_to_drainage_m",
    "lulc_type",
]

# Model 2 Features in strict order
MODEL2_FEATURE_ORDER: List[str] = [
    "Rainfall_1h",
    "Rainfall_3h",
    "Rainfall_6h",
    "Rainfall_12h",
    "Rainfall_24h",
    "Rainfall_3day",
    "Rainfall_7day",
    "susceptibility_probability",
    "soil_moisture_layer_1",
    "soil_moisture_layer_2",
]

# Susceptibility Probability Bands
SUSCEPTIBILITY_BANDS: List[Tuple[float, float, SusceptibilityClass]] = [
    (0.0, 0.20, SusceptibilityClass.VERY_LOW),
    (0.20, 0.39, SusceptibilityClass.LOW),
    (0.39, 0.60, SusceptibilityClass.MODERATE),
    (0.60, 0.80, SusceptibilityClass.HIGH),
    (0.80, 1.00, SusceptibilityClass.VERY_HIGH),
]


def classify_susceptibility(prob: float) -> SusceptibilityClass:
    """Map static susceptibility probability to qualitative category."""
    for low, high, cls_val in SUSCEPTIBILITY_BANDS:
        if low <= prob <= high:
            return cls_val
    if prob > 1.0:
        return SusceptibilityClass.VERY_HIGH
    return SusceptibilityClass.VERY_LOW


# Eight North Eastern States of India
NER_STATES = [
    "Arunachal Pradesh",
    "Assam",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Sikkim",
    "Tripura",
]
