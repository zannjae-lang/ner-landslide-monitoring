from fastapi import APIRouter, HTTPException
from app.schemas.replay import EventReplaySimulationResponse, HistoricalEventsListResponse
from app.services.historical.replay_service import replay_service


router = APIRouter(prefix="/replay", tags=["Historical Disaster Timeline & Replay"])


@router.get("/events", response_model=HistoricalEventsListResponse)
def list_historical_disaster_events():
    """Retrieve catalog of landmark past North Eastern landslide disasters for scenario replays."""
    return replay_service.list_events()


@router.post("/simulate/{event_id}", response_model=EventReplaySimulationResponse)
async def simulate_event_timeline(event_id: str):
    """Execute 7-day retrospective timeline simulation for a specific historical landslide event."""
    try:
        return await replay_service.simulate_event_replay(event_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Historical event replay simulation failed: {str(e)}",
        )
