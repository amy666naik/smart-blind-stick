"""Event and SOSEvent SQLAlchemy models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from app.database.base import Base


class Event(Base):
    """Represents a generic telemetry/hazard event sent by any subsystem."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.device_id"), nullable=False, index=True)
    source = Column(String(64), nullable=False)  # sensor_fusion, ai_vision, safety_engine
    event_type = Column(String(64), nullable=False, index=True)  # obstacle, object_detected, danger, fall, etc.
    risk_level = Column(String(32), nullable=False, index=True)  # low, medium, high, critical
    message = Column(String(255), nullable=False)
    extra = Column(JSON, nullable=True)  # module-specific JSON payload
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class SOSEvent(Base):
    """Represents a legacy/simple SOS event record."""
    __tablename__ = "sos_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.device_id"), nullable=False, index=True)
    reason = Column(String(255), nullable=False, default="SOS triggered")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    notified = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
