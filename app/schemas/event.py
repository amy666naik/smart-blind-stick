"""Event and legacy SOS Pydantic schemas."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EventCreateRequest(BaseModel):
    """Generic event ingestion payload for any subsystem."""
    device_id: str = Field(..., json_schema_extra={"example": "STICK_001"})
    source: str = Field(..., json_schema_extra={"example": "safety_engine"}, description="sensor_fusion, ai_vision, safety_engine")
    event_type: str = Field(..., json_schema_extra={"example": "danger"}, description="obstacle, object_detected, danger, fall, etc.")
    risk_level: str = Field("medium", json_schema_extra={"example": "high"}, description="low, medium, high, critical")
    message: str = Field(..., json_schema_extra={"example": "Sudden fall impact detected"})
    extra: Optional[Dict[str, Any]] = Field(default=None, json_schema_extra={"example": {"impact_g": 3.2, "tilt_deg": 65}})


class EventResponse(BaseModel):
    """Event detail response."""
    id: int
    device_id: str
    source: str
    event_type: str
    risk_level: str
    message: str
    extra: Optional[Dict[str, Any]]
    timestamp: datetime


class EventListResponse(BaseModel):
    """List of incident/event history."""
    device_id: str
    count: int
    events: List[EventResponse]


class LegacySOSRequest(BaseModel):
    """Legacy / standard SOS trigger payload."""
    device_id: str = Field(..., json_schema_extra={"example": "STICK_001"})
    reason: Optional[str] = Field("SOS triggered", json_schema_extra={"example": "Emergency button pressed"})
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class LegacySOSResponse(BaseModel):
    """Legacy SOS response."""
    status: str
    device_id: str
    notified: bool
    timestamp: datetime
    maps_url: Optional[str] = None
