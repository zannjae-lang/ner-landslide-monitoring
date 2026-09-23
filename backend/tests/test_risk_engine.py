from datetime import datetime, timezone, timedelta
import pytest

from app.config.model_config import DataQualityStatus, RainfallClass, RiskLevel, SusceptibilityClass
from app.schemas.predictions import Model1PredictionOutput, Model2PredictionOutput
from app.services.risk_engine.risk_engine import risk_engine


def test_risk_engine_fusion_normal():
    m1 = Model1PredictionOutput(
        susceptibility_probability=0.15,
        susceptibility_percent=15.0,
        susceptibility_class=SusceptibilityClass.VERY_LOW,
        threshold=0.39,
        is_susceptible=False,
    )
    m2 = Model2PredictionOutput(
        dynamic_probability=0.05,
        warning_candidate=False,
        threshold=0.10,
    )
    result = risk_engine.compute_risk(
        model1_result=m1,
        model2_result=m2,
        rainfall_24h_mm=5.0,
        data_timestamp=datetime.now(timezone.utc),
    )
    # Score = 0.45*0.15 + 0.55*0.05 + 0.00 = 0.0675 + 0.0275 = 0.095 -> Normal (< 0.25)
    assert result.final_risk == RiskLevel.NORMAL
    assert result.rainfall_class == RainfallClass.LOW
    assert result.data_status == DataQualityStatus.FRESH
    assert result.is_stale is False


def test_risk_engine_fusion_critical():
    m1 = Model1PredictionOutput(
        susceptibility_probability=0.85,
        susceptibility_percent=85.0,
        susceptibility_class=SusceptibilityClass.VERY_HIGH,
        threshold=0.39,
        is_susceptible=True,
    )
    m2 = Model2PredictionOutput(
        dynamic_probability=0.80,
        warning_candidate=True,
        threshold=0.10,
    )
    result = risk_engine.compute_risk(
        model1_result=m1,
        model2_result=m2,
        rainfall_24h_mm=75.0,  # Critical rain (+0.15)
        data_timestamp=datetime.now(timezone.utc),
    )
    # Score = 0.45*0.85 + 0.55*0.80 + 0.15 = 0.3825 + 0.44 + 0.15 = 0.9725 -> Critical (>= 0.75)
    assert result.final_risk == RiskLevel.CRITICAL
    assert result.rainfall_class == RainfallClass.CRITICAL
    assert result.combined_risk_score > 0.75


def test_risk_engine_stale_data():
    m1 = Model1PredictionOutput(
        susceptibility_probability=0.5,
        susceptibility_percent=50.0,
        susceptibility_class=SusceptibilityClass.MODERATE,
        threshold=0.39,
        is_susceptible=True,
    )
    m2 = Model2PredictionOutput(
        dynamic_probability=0.2,
        warning_candidate=True,
        threshold=0.10,
    )
    old_time = datetime.now(timezone.utc) - timedelta(hours=10)
    result = risk_engine.compute_risk(
        model1_result=m1,
        model2_result=m2,
        rainfall_24h_mm=20.0,
        data_timestamp=old_time,
    )
    assert result.is_stale is True
    assert result.data_status == DataQualityStatus.STALE
    assert any("exceeds the max freshness limit" in w for w in result.warnings)
