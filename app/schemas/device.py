"""Device Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DeviceCheckInRequest(BaseModel):
    """Payload sent periodically by the smart stick (or simulator)."""
    device_id: str = Field(..., json_schema_extra={"example": "STICK_001"})
    battery: Optional[float] = Field(None, ge=0.0, le=100.0, json_schema_extra={"example": 87.5})
    status: Optional[str] = Field("active", json_schema_extra={"example": "active"})
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, json_schema_extra={"example": 12.9716})
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, json_schema_extra={"example": 77.5946})
    gps_available: Optional[bool] = Field(True, json_schema_extra={"example": True})


class DeviceCheckInResponse(BaseModel):
    """Response returned after processing device check-in."""
    status: str
    device_id: str
    last_seen: datetime
    battery: Optional[float]
    is_online: bool


class DeviceStatusResponse(BaseModel):
    """Device status and connectivity info."""
    device_id: str
    status: str
    battery: Optional[float]
    is_online: bool
    last_seen: datetime
    last_latitude: Optional[float]
    last_longitude: Optional[float]
    gps_available: bool
