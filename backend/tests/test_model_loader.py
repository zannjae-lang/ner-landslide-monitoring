import pytest
from app.services.ml_models.artifact_loader import model_loader


def test_model_loader_status():
    assert model_loader.is_ready is True
    assert model_loader.model1 is not None
    assert model_loader.model2 is not None

    status = model_loader.get_status_summary()
    assert status["is_ready"] is True
    assert status["models"]["model1"]["loaded"] is True
    assert status["models"]["model2"]["loaded"] is True
    assert status["models"]["model1"]["threshold"] == 0.39
    assert status["models"]["model2"]["threshold"] == 0.10
