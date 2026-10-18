<<<<<<< HEAD
"""Device API routes: check-in data + status."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.device import DeviceDataIn, DeviceDataResponse, DeviceStatusResponse
from app.services import device_service

router = APIRouter(prefix="/api/device", tags=["device"])


@router.post("/data", response_model=DeviceDataResponse)
def receive_device_data(payload: DeviceDataIn, db: Session = Depends(get_db)):
    """
    Receive a check-in from the smart stick: battery, GPS position, and
    status. Creates the device on first contact, updates it thereafter,
    and records a location history point.
    """
    device_service.upsert_device_data(db, payload)
    return DeviceDataResponse(
        success=True,
        device_id=payload.device_id,
        message="Device data received",
    )


@router.get("/status/{device_id}", response_model=DeviceStatusResponse)
def get_device_status(device_id: str, db: Session = Depends(get_db)):
    """Return whether a device is online, its battery, and last-seen time."""
    device = device_service.get_device(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail=f"Unknown device_id '{device_id}'")

    return DeviceStatusResponse(
        device_id=device.device_id,
        online=device_service.is_device_online(device),
        battery=device.battery,
        gps_available=device.gps_available,
        last_seen=device.last_seen,
        last_fix_quality=device.last_fix_quality,
        last_satellites=device.last_satellites,
    )
=======
"""Device API Endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.device import (
    DeviceCheckInRequest,
    DeviceCheckInResponse,
    DeviceStatusResponse,
)
from app.services.device_service import DeviceService

router = APIRouter(prefix="/api/device", tags=["Device"])


@router.post(
    "/data",
    response_model=DeviceCheckInResponse,
    status_code=status.HTTP_200_OK,
    summary="Device Check-in / Telemetry",
    description="Receive periodic heartbeat, battery, status, and GPS coordinates from stick or simulator."
)
def device_check_in(
    payload: DeviceCheckInRequest,
    db: Session = Depends(get_db)
):
    """Process stick heartbeat telemetry."""
    device = DeviceService.check_in(db, payload)
    return DeviceCheckInResponse(
        status="ok",
        device_id=device.device_id,
        last_seen=device.last_seen,
        battery=device.battery,
        is_online=True,
    )


@router.get(
    "/status/{device_id}",
    response_model=DeviceStatusResponse,
    summary="Get Device Online/Offline Status",
    description="Query device battery, connectivity, and last seen timestamps."
)
def get_device_status(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve device status."""
    status_info = DeviceService.get_status(db, device_id)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found."
        )
    return status_info
>>>>>>> origin/feature/safety-emergency
