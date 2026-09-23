from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.data_source_repository import DataSourceRepository
from app.schemas.data_sources import DataSourceListResponse, DataSourceStatusResponse
from app.services.data_collectors.collector_manager import collector_manager

router = APIRouter(prefix="/data-sources", tags=["Data Sources & Providers"])


@router.get("/status", response_model=DataSourceListResponse)
async def get_data_sources_status(db: Session = Depends(get_db)):
    """Return health, availability, latency, and capabilities of all external data providers."""
    providers_data = await collector_manager.get_all_providers_status()
    
    # Sync with DB records
    repo = DataSourceRepository(db)
    items = []
    for p in providers_data:
        repo.update_status(
            provider_id=p["provider_id"],
            name=p["name"],
            status=p["status"],
            is_available=p["is_available"],
            requires_auth=p["requires_auth"],
            latency_ms=p.get("latency_ms"),
            error_message=p.get("error_message"),
        )
        items.append(DataSourceStatusResponse(**p))
    return DataSourceListResponse(total=len(items), providers=items)


@router.post("/providers/{provider_id}/test", response_model=DataSourceStatusResponse)
async def test_provider_connection(provider_id: str, db: Session = Depends(get_db)):
    """Trigger real-time diagnostic and authentication test for a specific provider."""
    providers_data = await collector_manager.get_all_providers_status()
    target = next((p for p in providers_data if p["provider_id"] == provider_id), None)
    if not target:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found in registry.")

    # Update status record in DB
    repo = DataSourceRepository(db)
    repo.update_status(
        provider_id=target["provider_id"],
        name=target["name"],
        status=target["status"],
        is_available=target["is_available"],
        requires_auth=target["requires_auth"],
        latency_ms=target.get("latency_ms"),
        error_message=target.get("error_message"),
    )
    return DataSourceStatusResponse(**target)
