"""Event Service.

Handles generic event ingestion, query filtering (by source, risk level, date),
and event retrieval for team modules.
"""
from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.device import Device
from app.schemas.event import EventCreateRequest


class EventService:
    """Business logic for generic multi-module incident events."""

    @classmethod
    def create_event(
        cls,
        db: Session,
        data: EventCreateRequest
    ) -> Event:
        """Store a generic event and ensure device is recognized."""
        # Ensure device exists
        device = db.query(Device).filter(Device.device_id == data.device_id).first()
        if not device:
            device = Device(
                device_id=data.device_id,
                battery=100.0,
                status="active",
                last_seen=datetime.now(timezone.utc),
            )
            db.add(device)
            db.commit()

        event = Event(
            device_id=data.device_id,
            source=data.source,
            event_type=data.event_type,
            risk_level=data.risk_level,
            message=data.message,
            extra=data.extra,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @classmethod
    def get_events(
        cls,
        db: Session,
        device_id: str,
        event_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        filter_date: Optional[date] = None,
        limit: int = 50
    ) -> List[Event]:
        """Query and filter events for a device."""
        query = db.query(Event).filter(Event.device_id == device_id)

        if event_type:
            query = query.filter(Event.event_type == event_type)
        if risk_level:
            query = query.filter(Event.risk_level == risk_level)
        if filter_date:
            start_dt = datetime.combine(filter_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_dt = datetime.combine(filter_date, datetime.max.time()).replace(tzinfo=timezone.utc)
            query = query.filter(Event.timestamp >= start_dt, Event.timestamp <= end_dt)

        return query.order_by(Event.timestamp.desc()).limit(limit).all()
