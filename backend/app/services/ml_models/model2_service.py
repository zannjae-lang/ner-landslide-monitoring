from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
import pandas as pd
import numpy as np

from app.config.model_config import MODEL2_FEATURE_ORDER, DataQualityStatus
from app.core.logger import logger
from app.schemas.predictions import Model2FeatureInput, Model2PredictionOutput
from app.services.ml_models.artifact_loader import model_loader


class Model2Service:
    """Service for Model 2: Dynamic Landslide Early Warning Model."""

    THRESHOLD: float = 0.10
    VERSION: str = "model2_v1.0_temporal_candidate"

    def predict(
        self,
        features: Union[Model2FeatureInput, Dict[str, Any]],
        data_timestamp: Optional[datetime] = None,
        data_age_hours: Optional[float] = None,
        data_quality: DataQualityStatus = DataQualityStatus.FRESH,
    ) -> Model2PredictionOutput:
        if not model_loader.is_ready or model_loader.model2 is None:
            ready, _ = model_loader.load_artifacts()
            if not ready or model_loader.model2 is None:
                raise RuntimeError(
                    f"Model 2 artifact is not loaded or available: {model_loader.errors.get('model2', 'Unknown error')}"
                )

        if isinstance(features, Model2FeatureInput):
            data_dict = features.model_dump()
        else:
            data_dict = dict(features)

        # Enforce exact column order
        missing = [f for f in MODEL2_FEATURE_ORDER if f not in data_dict]
        if missing:
            raise ValueError(f"Missing required Model 2 features: {missing}")

        ordered_data = {col: [data_dict[col]] for col in MODEL2_FEATURE_ORDER}
        df = pd.DataFrame(ordered_data)

        try:
            proba_arr = model_loader.model2.predict_proba(df)
            prob = float(proba_arr[0][1])
        except Exception as e:
            logger.error(f"Inference error in Model 2: {e}")
            raise RuntimeError(f"Model 2 inference failed: {str(e)}")

        prob_clipped = max(0.0, min(1.0, prob))
        warning_candidate = prob_clipped >= self.THRESHOLD

        return Model2PredictionOutput(
            model_name="Dynamic Landslide Early Warning Model",
            model_version=self.VERSION,
            dynamic_probability=round(prob_clipped, 4),
            warning_candidate=warning_candidate,
            threshold=self.THRESHOLD,
            operational_validation=False,
            calibrated=False,
            data_timestamp=data_timestamp or datetime.now(timezone.utc),
            data_age_hours=round(data_age_hours, 2) if data_age_hours is not None else 0.0,
            data_quality=data_quality,
            disclaimer="Research prototype. Temporal candidate model uncalibrated for operational warning.",
        )


model2_service = Model2Service()
