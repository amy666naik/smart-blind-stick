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
