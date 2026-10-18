<<<<<<< HEAD
"""Location / GPS API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.location import LocationOut, LocationHistoryItem
from app.services import location_service, device_service

router = APIRouter(prefix="/api/location", tags=["location"])


@router.get("/{device_id}", response_model=LocationOut)
def get_latest_location(device_id: str, db: Session = Depends(get_db)):
    """Return the most recent known location for a device."""
    if device_service.get_device(db, device_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown device_id '{device_id}'")

    location = location_service.get_latest_location(db, device_id)
    if location is None:
        raise HTTPException(status_code=404, detail=f"No location data for device_id '{device_id}'")

    return location


@router.get("/{device_id}/history", response_model=list[LocationHistoryItem])
def get_location_history(
    device_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Return recent location history for a device, most recent first."""
    if device_service.get_device(db, device_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown device_id '{device_id}'")

    return location_service.get_location_history(db, device_id, limit=limit)
=======
"""Location API Endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.location import (
    LatestLocationResponse,
    LocationHistoryResponse,
    LocationPoint,
)
from app.services.location_service import LocationService

router = APIRouter(prefix="/api/location", tags=["Location & GPS"])


@router.get(
    "/{device_id}",
    response_model=LatestLocationResponse,
    summary="Get Latest Known Location",
    description="Retrieve latest GPS coordinates and Google Maps link for a device."
)
def get_latest_location(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Fetch most recent GPS fix."""
    lat, lon, is_mock, maps_url = LocationService.get_latest_location(db, device_id, fallback_to_mock=True)
    if lat is None or lon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No location data available for device '{device_id}'."
        )

    return LatestLocationResponse(
        device_id=device_id,
        latitude=lat,
        longitude=lon,
        gps_available=True,
        last_updated=None,
        maps_url=maps_url,
    )


@router.get(
    "/{device_id}/history",
    response_model=LocationHistoryResponse,
    summary="Get Location History",
    description="Retrieve chronological location breadcrumbs for map path tracing."
)
def get_location_history(
    device_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Fetch location history points."""
    records = LocationService.get_location_history(db, device_id, limit=limit)
    points = [
        LocationPoint(
            latitude=r.latitude,
            longitude=r.longitude,
            timestamp=r.timestamp,
            maps_url=LocationService.format_maps_url(r.latitude, r.longitude),
        )
        for r in records
    ]
    return LocationHistoryResponse(
        device_id=device_id,
        count=len(points),
        locations=points,
    )
>>>>>>> origin/feature/safety-emergency
