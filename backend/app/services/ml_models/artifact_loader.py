import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import joblib

from app.config.settings import settings
from app.core.logger import logger


class ModelArtifactLoader:
    """Manages loading, verification, and caching of ML model artifacts and schemas."""

    def __init__(self):
        self._model1: Optional[Any] = None
        self._model2: Optional[Any] = None
        self._registry: Optional[Dict[str, Any]] = None
        self._model2_schema: Optional[Dict[str, Any]] = None
        self._is_ready: bool = False
        self._load_errors: Dict[str, str] = {}

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    @property
    def model1(self) -> Optional[Any]:
        return self._model1

    @property
    def model2(self) -> Optional[Any]:
        return self._model2

    @property
    def registry(self) -> Optional[Dict[str, Any]]:
        return self._registry

    @property
    def model2_schema(self) -> Optional[Dict[str, Any]]:
        return self._model2_schema

    @property
    def errors(self) -> Dict[str, str]:
        return self._load_errors

    def compute_sha256(self, file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def load_artifacts(self) -> Tuple[bool, Dict[str, Any]]:
        """Loads all artifacts, checks existence and integrity."""
        self._load_errors.clear()
        
        # 1. Load Registry
        registry_path = settings.model_registry_path
        if not registry_path.exists():
            err = f"Model registry file not found at: {registry_path}"
            logger.error(err)
            self._load_errors["registry"] = err
        else:
            try:
                with open(registry_path, "r", encoding="utf-8") as f:
                    self._registry = json.load(f)
                logger.info("Loaded model registry successfully.")
            except Exception as e:
                err = f"Failed to parse model registry: {str(e)}"
                logger.error(err)
                self._load_errors["registry"] = err

        # 2. Load Model 2 Schema
        schema_path = settings.model2_schema_path
        if not schema_path.exists():
            err = f"Model 2 schema file not found at: {schema_path}"
            logger.warning(err)
        else:
            try:
                with open(schema_path, "r", encoding="utf-8") as f:
                    self._model2_schema = json.load(f)
                logger.info("Loaded Model 2 schema successfully.")
            except Exception as e:
                logger.warning(f"Failed to parse Model 2 schema: {str(e)}")

        # 3. Load Model 1
        m1_path = settings.model1_artifact_path
        if not m1_path.exists():
            # Check fallback in backend/artifacts/models
            fallback_m1 = settings.artifacts_path / "models" / "model1_landslide_susceptibility.joblib"
            if fallback_m1.exists():
                m1_path = fallback_m1
            else:
                err = f"Model 1 artifact not found at {m1_path}"
                logger.error(err)
                self._load_errors["model1"] = err

        if "model1" not in self._load_errors:
            try:
                m1_sha = self.compute_sha256(m1_path)
                expected_sha = (
                    self._registry.get("models", {}).get("model1", {}).get("sha256")
                    if self._registry else None
                )
                if expected_sha and m1_sha != expected_sha:
                    logger.warning(
                        f"Model 1 SHA-256 mismatch! Computed: {m1_sha}, Registry: {expected_sha}"
                    )
                self._model1 = joblib.load(m1_path)
                logger.info(f"Model 1 loaded successfully from {m1_path} (SHA: {m1_sha[:8]}...)")
            except Exception as e:
                err = f"Failed to load Model 1 artifact: {str(e)}"
                logger.error(err)
                self._load_errors["model1"] = err

        # 4. Load Model 2
        m2_path = settings.model2_artifact_path
        if not m2_path.exists():
            fallback_m2 = settings.artifacts_path / "models" / "model2_landslide_early_warning.joblib"
            if fallback_m2.exists():
                m2_path = fallback_m2
            else:
                err = f"Model 2 artifact not found at {m2_path}"
                logger.error(err)
                self._load_errors["model2"] = err

        if "model2" not in self._load_errors:
            try:
                m2_sha = self.compute_sha256(m2_path)
                expected_sha = (
                    self._registry.get("models", {}).get("model2", {}).get("sha256")
                    if self._registry else None
                )
                if expected_sha and m2_sha != expected_sha:
                    logger.warning(
                        f"Model 2 SHA-256 mismatch! Computed: {m2_sha}, Registry: {expected_sha}"
                    )
                self._model2 = joblib.load(m2_path)
                logger.info(f"Model 2 loaded successfully from {m2_path} (SHA: {m2_sha[:8]}...)")
            except Exception as e:
                err = f"Failed to load Model 2 artifact: {str(e)}"
                logger.error(err)
                self._load_errors["model2"] = err

        self._is_ready = bool(self._model1 is not None and self._model2 is not None)
        status_info = self.get_status_summary()
        return self._is_ready, status_info

    def get_status_summary(self) -> Dict[str, Any]:
        return {
            "is_ready": self._is_ready,
            "models": {
                "model1": {
                    "loaded": self._model1 is not None,
                    "name": "Landslide Susceptibility Model",
                    "version": "model1_v1.0",
                    "algorithm": "XGBoost",
                    "threshold": 0.39,
                    "task": "Static susceptibility prediction",
                    "operational_validation": False,
                },
                "model2": {
                    "loaded": self._model2 is not None,
                    "name": "Dynamic Landslide Early Warning Model",
                    "version": "model2_v1.0_temporal_candidate",
                    "algorithm": "XGBoost",
                    "threshold": 0.10,
                    "task": "Dynamic warning candidate prediction",
                    "operational_validation": False,
                },
            },
            "risk_engine": {
                "version": "2.0",
                "max_data_age_hours": settings.MAX_DATA_AGE_HOURS,
                "warning_status": "Prototype only - uncalibrated research candidate",
                "operational_validation": False,
            },
            "errors": self._load_errors,
        }


model_loader = ModelArtifactLoader()
