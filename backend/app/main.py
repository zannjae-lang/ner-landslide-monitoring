from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.config.settings import settings
from app.core.logger import logger
from app.db.seed import seed_database
from app.db.session import SessionLocal, init_db
from app.services.ml_models.artifact_loader import model_loader


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    
    # 1. Initialize DB tables
    init_db()
    
    # 2. Seed default NER monitoring locations
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # 3. Load and verify ML model artifacts
    ready, status_info = model_loader.load_artifacts()
    if ready:
        logger.info("All ML Model artifacts loaded and verified successfully.")
    else:
        logger.warning(f"ML Model Loader reported issues: {status_info.get('errors')}")

    yield
    # Shutdown
    logger.info("Shutting down NER Landslide Monitoring Backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "AI-Based Early Warning and Landslide Risk Monitoring Platform for the 8 North Eastern Region (NER) "
        "States of India (SIH 2026 | Problem ID: 26001 | MDoNER). Note: Predictive outputs are prototype research candidates."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "Operational",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "disclaimer": "Prototype early warning and risk monitoring system. Uncalibrated research output.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
