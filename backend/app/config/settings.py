import json
from pathlib import Path
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General
    PROJECT_NAME: str = "NER Landslide Early Warning and Risk Monitoring System"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            return json.loads(v)
        return v

    # Database
    DATABASE_URL: str = "sqlite:///./ner_landslide.db"

    # Base directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Artifact paths (relative to BASE_DIR or absolute)
    ARTIFACTS_DIR: str = "artifacts"
    MODEL1_ARTIFACT_REL: str = "models/model1_landslide_susceptibility.joblib"
    MODEL2_ARTIFACT_REL: str = "models/model2_landslide_early_warning.joblib"
    MODEL_REGISTRY_REL: str = "metadata/model_registry.json"
    MODEL2_SCHEMA_REL: str = "schemas/model2_feature_schema.json"

    # Risk Engine 2.0 Parameters
    MAX_DATA_AGE_HOURS: int = 6
    RISK_SUSCEPTIBILITY_WEIGHT: float = 0.45
    RISK_DYNAMIC_WEIGHT: float = 0.55
    RISK_THRESHOLD_NORMAL: float = 0.25
    RISK_THRESHOLD_WATCH: float = 0.25
    RISK_THRESHOLD_ALERT: float = 0.50
    RISK_THRESHOLD_CRITICAL: float = 0.75

    # Rainfall 24h Thresholds
    RAINFALL_THRESHOLD_ELEVATED_MM: float = 15.0
    RAINFALL_THRESHOLD_HIGH_MM: float = 35.0
    RAINFALL_THRESHOLD_CRITICAL_MM: float = 65.0

    # Rainfall Adjustment Deltas
    RAINFALL_DELTA_LOW: float = 0.00
    RAINFALL_DELTA_ELEVATED: float = 0.05
    RAINFALL_DELTA_HIGH: float = 0.10
    RAINFALL_DELTA_CRITICAL: float = 0.15

    # External Data Providers & Flags
    MOCK_PROVIDERS_ENABLED: bool = True
    AUTO_REFRESH_INTERVAL_MINUTES: int = 30

    # NASA Earthdata & IMERG (GPM) Configuration
    NASA_EARTHDATA_TOKEN: str = ""
    NASA_EARTHDATA_USERNAME: str = ""
    NASA_EARTHDATA_PASSWORD: str = ""
    NASA_IMERG_API_KEY: str = ""

    # ISRO MOSDAC Configuration
    MOSDAC_USER_ID: str = ""
    MOSDAC_USER_KEY: str = ""
    MOSDAC_API_KEY: str = ""

    # Google Earth Engine (GEE)
    GEE_PROJECT_ID: str = ""
    GEE_SERVICE_ACCOUNT_EMAIL: str = ""
    GEE_PRIVATE_KEY_PATH: str = ""

    @property
    def artifacts_path(self) -> Path:
        return self.BASE_DIR / self.ARTIFACTS_DIR

    @property
    def model1_artifact_path(self) -> Path:
        return self.artifacts_path / self.MODEL1_ARTIFACT_REL

    @property
    def model2_artifact_path(self) -> Path:
        return self.artifacts_path / self.MODEL2_ARTIFACT_REL

    @property
    def model_registry_path(self) -> Path:
        primary = self.artifacts_path / self.MODEL_REGISTRY_REL
        if primary.exists():
            return primary
        fallback = self.artifacts_path / "models" / "model_registry.json"
        return fallback

    @property
    def model2_schema_path(self) -> Path:
        primary = self.artifacts_path / self.MODEL2_SCHEMA_REL
        if primary.exists():
            return primary
        fallback = self.artifacts_path / "models" / "model2_feature_schema.json"
        return fallback


settings = Settings()
