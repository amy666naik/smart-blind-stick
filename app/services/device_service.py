"""Device Service.

Handles device check-in, heartbeat, status management, and online/offline tracking.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.device import Device
from app.models.location import Location
from app.schemas.device import DeviceCheckInRequest, DeviceStatusResponse


class DeviceService:
    """Business logic for device state and check-ins."""

    @staticmethod
    def is_device_online(last_seen: Optional[datetime], offline_threshold_seconds: int) -> bool:
        """Determine if device is currently online based on last check-in time."""
        if not last_seen:
            return False
        now = datetime.now(timezone.utc)
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        return (now - last_seen).total_seconds() <= offline_threshold_seconds

    @classmethod
    def check_in(
        cls,
        db: Session,
        data: DeviceCheckInRequest
    ) -> Device:
        """Process periodic check-in from smart stick hardware or simulator."""
        now = datetime.now(timezone.utc)
        device = db.query(Device).filter(Device.device_id == data.device_id).first()

        if not device:
            device = Device(
                device_id=data.device_id,
                battery=data.battery if data.battery is not None else 100.0,
                status=data.status or "active",
                last_latitude=data.latitude,
                last_longitude=data.longitude,
                gps_available=data.gps_available if data.gps_available is not None else True,
                last_seen=now,
                created_at=now,
            )
            db.add(device)
        else:
            if data.battery is not None:
                device.battery = data.battery
            if data.status:
                device.status = data.status
            if data.latitude is not None and data.longitude is not None:
                device.last_latitude = data.latitude
                device.last_longitude = data.longitude
            if data.gps_available is not None:
                device.gps_available = data.gps_available
            device.last_seen = now

        # If valid GPS was transmitted with check-in, save to location history
        if data.latitude is not None and data.longitude is not None:
            location_point = Location(
                device_id=data.device_id,
                latitude=data.latitude,
                longitude=data.longitude,
                timestamp=now,
            )
            db.add(location_point)

        db.commit()
        db.refresh(device)
        return device

    @classmethod
    def get_status(
        cls,
        db: Session,
        device_id: str
    ) -> Optional[DeviceStatusResponse]:
        """Fetch device status and compute online flag."""
        settings = get_settings()
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            return None

        online = cls.is_device_online(device.last_seen, settings.DEVICE_OFFLINE_AFTER_SECONDS)
        return DeviceStatusResponse(
            device_id=device.device_id,
            status=device.status,
            battery=device.battery,
            is_online=online,
            last_seen=device.last_seen,
            last_latitude=device.last_latitude,
            last_longitude=device.last_longitude,
            gps_available=device.gps_available,
        )
