"""Application Configuration Settings."""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment or defaults."""
    
    # Project Info
    PROJECT_NAME: str = "Smart Blind Stick - Mobile & IoT Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./smart_blind_stick.db"
    
    # Device Monitoring
    DEVICE_OFFLINE_AFTER_SECONDS: int = 60
    DEFAULT_EVENT_LIMIT: int = 50
    DEFAULT_LOCATION_HISTORY_LIMIT: int = 50
    
    # Safety & Emergency Subsystem Configuration
    # Fall confirmation countdown window (seconds before auto-escalation to SOS)
    FALL_CONFIRMATION_TIMEOUT_SECONDS: int = 20
    
    # Fall Detection Algorithm Thresholds (Multi-condition)
    # 1. Free fall / weightlessness drop acceleration magnitude threshold in g (1g = 9.81 m/s^2)
    FALL_ACCEL_FREE_FALL_THRESHOLD: float = 0.6
    # 2. Impact acceleration spike magnitude threshold in g
    FALL_ACCEL_IMPACT_THRESHOLD: float = 2.4
    # 3. Orientation tilt change threshold in degrees
    FALL_TILT_THRESHOLD_DEGREES: float = 40.0
    # 4. Post-impact immobility duration threshold in seconds
    FALL_IMMOBILITY_DURATION_SECONDS: float = 2.5
    
    # Guardian Notification Settings
    # Supported: mock, log, sms, firebase, email
    NOTIFICATION_ADAPTER: str = "mock"
    GUARDIAN_NAME: str = "Primary Guardian"
    GUARDIAN_PHONE: str = "+1-555-0199"
    GUARDIAN_EMAIL: str = "guardian@smartblindstick.example"
    FCM_SERVER_KEY: Optional[str] = None
    
    # Simulator Settings
    SIMULATOR_BASE_URL: str = "http://127.0.0.1:8000"
    SIMULATOR_DEVICE_ID: str = "STICK_001"
    SIMULATOR_INTERVAL_SECONDS: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
