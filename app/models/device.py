"""Device SQLAlchemy model."""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime
from app.database.base import Base


class Device(Base):
    """Represents a registered Smart Blind Stick device."""
    __tablename__ = "devices"

    device_id = Column(String(64), primary_key=True, index=True)
    battery = Column(Float, nullable=True, default=100.0)
    status = Column(String(32), nullable=False, default="active")  # active, offline, maintenance
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    gps_available = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
