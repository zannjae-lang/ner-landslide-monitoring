from typing import Dict, Any, Union
import pandas as pd
import numpy as np

from app.config.model_config import (
    MODEL1_FEATURE_ORDER,
    classify_susceptibility,
    SusceptibilityClass,
)
from app.core.logger import logger
from app.schemas.predictions import Model1FeatureInput, Model1PredictionOutput
from app.services.ml_models.artifact_loader import model_loader


class Model1Service:
    """Service for Model 1: Static Landslide Susceptibility Prediction."""

    THRESHOLD: float = 0.39
    VERSION: str = "model1_v1.0"

    def predict(self, features: Union[Model1FeatureInput, Dict[str, Any]]) -> Model1PredictionOutput:
        if not model_loader.is_ready or model_loader.model1 is None:
            # Try reloading
            ready, _ = model_loader.load_artifacts()
            if not ready or model_loader.model1 is None:
                raise RuntimeError(
                    f"Model 1 artifact is not loaded or available: {model_loader.errors.get('model1', 'Unknown error')}"
                )

        if isinstance(features, Model1FeatureInput):
            data_dict = features.model_dump()
        else:
            data_dict = dict(features)

        # Enforce exact column order
        missing = [f for f in MODEL1_FEATURE_ORDER if f not in data_dict]
        if missing:
            raise ValueError(f"Missing required Model 1 features: {missing}")

        ordered_data = {col: [data_dict[col]] for col in MODEL1_FEATURE_ORDER}
        df = pd.DataFrame(ordered_data)

        try:
            proba_arr = model_loader.model1.predict_proba(df)
            prob = float(proba_arr[0][1])
        except Exception as e:
            logger.error(f"Inference error in Model 1: {e}")
            raise RuntimeError(f"Model 1 inference failed: {str(e)}")

        # Clip probability to [0.0, 1.0]
        prob_clipped = max(0.0, min(1.0, prob))
        susc_class = classify_susceptibility(prob_clipped)
        is_susc = prob_clipped >= self.THRESHOLD

        return Model1PredictionOutput(
            model_name="Landslide Susceptibility Model",
            model_version=self.VERSION,
            susceptibility_probability=round(prob_clipped, 4),
            susceptibility_percent=round(prob_clipped * 100.0, 2),
            susceptibility_class=susc_class,
            threshold=self.THRESHOLD,
            is_susceptible=is_susc,
            operational_validation=False,
            calibrated=False,
            disclaimer="Prototype research candidate. Not calibrated or operationally validated.",
        )


model1_service = Model1Service()
