<<<<<<< HEAD
"""SOS API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.event import SOSIn, SOSOut
from app.services import event_service, device_service

router = APIRouter(prefix="/api/sos", tags=["sos"])


@router.post("", response_model=SOSOut)
def trigger_sos(payload: SOSIn, db: Session = Depends(get_db)):
    """
    Record an SOS event and dispatch it through the notification
    service abstraction (currently a mock -- see services/notification_service.py).
    """
    if device_service.get_device(db, payload.device_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown device_id '{payload.device_id}'")

    sos = event_service.create_sos(db, payload)
    return SOSOut(success=True, message="SOS received", event_id=sos.id)
=======
"""Backward-compatible SOS API Endpoint.

Maintains the legacy /api/sos route contract while routing internally through
the comprehensive Safety & Emergency State Manager pipeline.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.event import LegacySOSRequest, LegacySOSResponse
from app.schemas.emergency import ManualSOSRequest
from app.services.emergency_service import EmergencyService

router = APIRouter(prefix="/api/sos", tags=["SOS (Legacy / Universal)"])


@router.post(
    "",
    response_model=LegacySOSResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger SOS (Universal)",
    description="Universal SOS endpoint maintaining compatibility with base contract while invoking Emergency State Manager."
)
def trigger_sos(
    payload: LegacySOSRequest,
    db: Session = Depends(get_db)
):
    """Trigger SOS and route through Emergency State Manager."""
    manual_request = ManualSOSRequest(
        device_id=payload.device_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        reason=payload.reason or "Universal SOS triggered",
    )
    session = EmergencyService.trigger_manual_sos(db, manual_request)
    
    return LegacySOSResponse(
        status="success",
        device_id=session.device_id,
        notified=session.notification_status in ("DISPATCHED", "PENDING"),
        timestamp=session.started_at,
        maps_url=session.maps_url,
    )
>>>>>>> origin/feature/safety-emergency
