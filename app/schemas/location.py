"""Location Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LocationPoint(BaseModel):
    """Single GPS location point."""
    latitude: float = Field(..., ge=-90.0, le=90.0, json_schema_extra={"example": 12.9716})
    longitude: float = Field(..., ge=-180.0, le=180.0, json_schema_extra={"example": 77.5946})
    timestamp: datetime
    maps_url: Optional[str] = None


class LatestLocationResponse(BaseModel):
    """Latest known location for a device."""
    device_id: str
    latitude: Optional[float]
    longitude: Optional[float]
    gps_available: bool
    last_updated: Optional[datetime]
    maps_url: Optional[str]


class LocationHistoryResponse(BaseModel):
    """History of location breadcrumbs for a device."""
    device_id: str
    count: int
    locations: List[LocationPoint]
