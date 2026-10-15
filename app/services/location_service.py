"""GPS & Location Service.

Handles real and simulated GPS coordinates, validation, Google Maps URL generation,
and location history tracking.
"""
import math
import random
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.device import Device


class LocationService:
    """Service for querying, saving, and simulating GPS coordinates."""

    @staticmethod
    def format_maps_url(latitude: Optional[float], longitude: Optional[float]) -> Optional[str]:
        """Generate a Google Maps URL for given coordinates.
        
        Returns None if coordinates are missing or invalid.
        """
        if latitude is None or longitude is None:
            return None
        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            return None
        return f"https://maps.google.com/?q={latitude:.6f},{longitude:.6f}"

    @staticmethod
    def is_valid_coordinate(latitude: Optional[float], longitude: Optional[float]) -> bool:
        """Validate latitude and longitude bounds."""
        if latitude is None or longitude is None:
            return False
        return -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0

    @staticmethod
    def generate_mock_gps_point(
        base_lat: float = 12.9716,
        base_lon: float = 77.5946,
        drift_radius_meters: float = 50.0
    ) -> Tuple[float, float]:
        """Generate a realistic mock GPS point simulating location drift/walking.
        
        FUTURE HARDWARE INTEGRATION:
        Replace this mock generator with NMEA sentence parsing from a real
        NEO-6M / SIM800L / GPS module UART stream on the ESP32.
        """
        # Convert meters to approximate degree offsets (1 deg lat ~ 111,139 meters)
        lat_offset = (random.uniform(-drift_radius_meters, drift_radius_meters)) / 111139.0
        lon_offset = (random.uniform(-drift_radius_meters, drift_radius_meters)) / (
            111139.0 * math.cos(math.radians(base_lat))
        )
        return round(base_lat + lat_offset, 6), round(base_lon + lon_offset, 6)

    @classmethod
    def record_location(
        cls,
        db: Session,
        device_id: str,
        latitude: float,
        longitude: float,
    ) -> Optional[Location]:
        """Save a new GPS location point to the history table and update device cache."""
        if not cls.is_valid_coordinate(latitude, longitude):
            return None

        location = Location(
            device_id=device_id,
            latitude=latitude,
            longitude=longitude,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(location)

        # Update cached last coordinates on device record
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if device:
            device.last_latitude = latitude
            device.last_longitude = longitude
            device.gps_available = True
            device.last_seen = datetime.now(timezone.utc)

        db.commit()
        db.refresh(location)
        return location

    @classmethod
    def get_latest_location(
        cls,
        db: Session,
        device_id: str,
        fallback_to_mock: bool = True
    ) -> Tuple[Optional[float], Optional[float], bool, Optional[str]]:
        """Retrieve the latest known location for a device.
        
        Returns: (latitude, longitude, is_mock, maps_url)
        """
        # 1. Check device's cached location
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if device and cls.is_valid_coordinate(device.last_latitude, device.last_longitude):
            maps_url = cls.format_maps_url(device.last_latitude, device.last_longitude)
            return device.last_latitude, device.last_longitude, False, maps_url

        # 2. Check location history table
        latest_record = (
            db.query(Location)
            .filter(Location.device_id == device_id)
            .order_by(Location.timestamp.desc())
            .first()
        )
        if latest_record and cls.is_valid_coordinate(latest_record.latitude, latest_record.longitude):
            maps_url = cls.format_maps_url(latest_record.latitude, latest_record.longitude)
            return latest_record.latitude, latest_record.longitude, False, maps_url

        # 3. If no location found and fallback allowed, generate a simulated mock coordinate
        if fallback_to_mock:
            mock_lat, mock_lon = cls.generate_mock_gps_point()
            # Cache mock location so subsequent queries remain consistent
            if device:
                device.last_latitude = mock_lat
                device.last_longitude = mock_lon
                device.gps_available = True
                db.commit()
            maps_url = cls.format_maps_url(mock_lat, mock_lon)
            return mock_lat, mock_lon, True, maps_url

        return None, None, False, None

    @staticmethod
    def get_location_history(
        db: Session,
        device_id: str,
        limit: int = 50
    ) -> List[Location]:
        """Fetch location history for a device ordered newest first."""
        return (
            db.query(Location)
            .filter(Location.device_id == device_id)
            .order_by(Location.timestamp.desc())
            .limit(limit)
            .all()
        )
