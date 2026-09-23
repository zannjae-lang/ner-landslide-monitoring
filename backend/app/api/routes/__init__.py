from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.locations import router as locations_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.weather import router as weather_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.data_sources import router as data_sources_router
from app.api.routes.map import router as map_router
from app.api.routes.satellite import router as satellite_router
from app.api.routes.satellite_analysis import router as satellite_analysis_router
from app.api.routes.evidence import router as evidence_router
from app.api.routes.grid import router as grid_router
from app.api.routes.exposure import router as exposure_router
from app.api.routes.reports import router as reports_router
from app.api.routes.replay import router as replay_router
from app.api.routes.field_reports import router as field_reports_router
from app.api.routes.monitoring import router as monitoring_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(locations_router)
api_router.include_router(predictions_router)
api_router.include_router(weather_router)
api_router.include_router(alerts_router)
api_router.include_router(data_sources_router)
api_router.include_router(map_router)
api_router.include_router(satellite_router)
api_router.include_router(satellite_analysis_router)
api_router.include_router(evidence_router)
api_router.include_router(grid_router)
api_router.include_router(exposure_router)
api_router.include_router(reports_router)
api_router.include_router(replay_router)
api_router.include_router(field_reports_router)
api_router.include_router(monitoring_router)








