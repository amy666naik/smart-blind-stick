"""Event Ingestion & Incident Query Endpoints."""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.event import (
    EventCreateRequest,
    EventResponse,
    EventListResponse,
)
from app.services.event_service import EventService

router = APIRouter(prefix="/api/events", tags=["Events & Incidents"])


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an Event",
    description="Generic endpoint used by all modules (Sensor Fusion, AI Vision, Safety Engine) to report incidents."
)
def create_event(
    payload: EventCreateRequest,
    db: Session = Depends(get_db)
):
    """Ingest generic telemetry/hazard event."""
    event = EventService.create_event(db, payload)
    return EventResponse(
        id=event.id,
        device_id=event.device_id,
        source=event.source,
        event_type=event.event_type,
        risk_level=event.risk_level,
        message=event.message,
        extra=event.extra,
        timestamp=event.timestamp,
    )


@router.get(
    "/{device_id}",
    response_model=EventListResponse,
    summary="Get Incident History",
    description="Retrieve incident events for a device with optional filtering by event type, risk level, or date."
)
def get_events(
    device_id: str,
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. obstacle, danger, fall)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (low, medium, high, critical)"),
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Query incident events with filters."""
    events = EventService.get_events(
        db,
        device_id=device_id,
        event_type=event_type,
        risk_level=risk_level,
        filter_date=date,
        limit=limit,
    )
    res_events = [
        EventResponse(
            id=e.id,
            device_id=e.device_id,
            source=e.source,
            event_type=e.event_type,
            risk_level=e.risk_level,
            message=e.message,
            extra=e.extra,
            timestamp=e.timestamp,
        )
        for e in events
    ]
    return EventListResponse(
        device_id=device_id,
        count=len(res_events),
        events=res_events,
    )
