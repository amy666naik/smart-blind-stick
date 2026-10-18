<<<<<<< HEAD
"""Generic event API routes -- shared by sensor fusion, AI vision, and safety engine."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.event import EventIn, EventOut
from app.services import event_service, device_service

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("", response_model=EventOut)
def create_event(payload: EventIn, db: Session = Depends(get_db)):
    """
    Accept an event from any module (sensor_fusion, ai_vision,
    safety_engine, or manual). See README.md for the integration
    contract each module should follow.
    """
    if device_service.get_device(db, payload.device_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown device_id '{payload.device_id}'")

    return event_service.create_event(db, payload)


@router.get("/{device_id}", response_model=list[EventOut])
def get_events(
    device_id: str,
    event_type: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    date: str | None = Query(default=None, description="ISO date, e.g. 2026-08-11"),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Return recent events for a device, with optional filtering."""
    if device_service.get_device(db, device_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown device_id '{device_id}'")

    return event_service.get_events(
        db, device_id, event_type=event_type, risk_level=risk_level, date=date, limit=limit
=======
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
>>>>>>> origin/feature/safety-emergency
    )
