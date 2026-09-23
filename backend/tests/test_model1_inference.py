import pytest
from app.schemas.predictions import Model1FeatureInput
from app.services.ml_models.model1_service import model1_service


def test_model1_valid_inference():
    features = Model1FeatureInput(
        elevation=1450.0,
        slope=28.5,
        curvature=0.03,
        tpi=2.1,
        tri=4.5,
        aspect_sin=0.6,
        aspect_cos=0.8,
        ndvi_p90=0.72,
        ndvi_p50=0.60,
        ndvi_p10=0.42,
        distance_to_road_m=120.0,
        distance_to_drainage_m=65.0,
        lulc_type="Forest",
    )

    output = model1_service.predict(features)
    assert 0.0 <= output.susceptibility_probability <= 1.0
    assert 0.0 <= output.susceptibility_percent <= 100.0
    assert output.susceptibility_class.value in ["Very Low", "Low", "Moderate", "High", "Very High"]
    assert output.threshold == 0.39
    assert output.is_susceptible == (output.susceptibility_probability >= 0.39)
    assert output.operational_validation is False


def test_model1_missing_feature_error():
    incomplete_dict = {
        "elevation": 1200.0,
        "slope": 20.0,
    }
    with pytest.raises(ValueError) as exc:
        model1_service.predict(incomplete_dict)
    assert "Missing required Model 1 features" in str(exc.value)
