import pytest
from app.schemas.predictions import Model2FeatureInput
from app.services.ml_models.model2_service import model2_service


def test_model2_valid_inference():
    features = Model2FeatureInput(
        Rainfall_1h=4.5,
        Rainfall_3h=12.0,
        Rainfall_6h=28.0,
        Rainfall_12h=45.0,
        Rainfall_24h=80.0,
        Rainfall_3day=140.0,
        Rainfall_7day=210.0,
        susceptibility_probability=0.75,
        soil_moisture_layer_1=0.38,
        soil_moisture_layer_2=0.42,
    )

    output = model2_service.predict(features)
    assert 0.0 <= output.dynamic_probability <= 1.0
    assert output.threshold == 0.10
    assert output.warning_candidate == (output.dynamic_probability >= 0.10)
    assert output.operational_validation is False
    assert output.calibrated is False


def test_model2_missing_feature_error():
    incomplete = {"Rainfall_1h": 2.0}
    with pytest.raises(ValueError) as exc:
        model2_service.predict(incomplete)
    assert "Missing required Model 2 features" in str(exc.value)
