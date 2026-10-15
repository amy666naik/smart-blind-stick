"""Guardian Notification Service.

Provides a pluggable abstraction for dispatching emergency alerts to guardians
across multiple channels (Mock/Console, SMS, Firebase Push, Email).

IMPORTANT NOTE:
Physical hardware / live SMS gateways (Twilio, Firebase, GSM SIM800L) are not yet
connected. All adapters run in SIMULATION mode with clear formatting and delivery tracking.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.config import get_settings


class EmergencyAlertPayload(BaseModel):
    """Standardized emergency notification payload sent to guardians."""
    device_id: str
    guardian_name: str
    emergency_type: str  # MANUAL_SOS, AUTOMATIC_FALL, CANCELLED, RESOLVED
    title: str
    message: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    maps_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    extra_details: Optional[Dict[str, Any]] = None


class NotificationResult(BaseModel):
    """Result of an emergency notification dispatch attempt."""
    success: bool
    channel: str  # mock, sms_simulated, firebase_simulated, email_simulated
    recipient: str
    dispatched_at: datetime
    message_id: str
    summary: str
    raw_payload: Dict[str, Any]


class BaseNotificationAdapter(ABC):
    """Abstract interface for all notification adapters."""

    @abstractmethod
    def send_emergency_alert(self, payload: EmergencyAlertPayload) -> NotificationResult:
        """Send an urgent emergency alert to the guardian."""
        pass

    @abstractmethod
    def send_cancellation_notice(self, payload: EmergencyAlertPayload) -> NotificationResult:
        """Send a false-alarm cancellation notification to the guardian."""
        pass

    @abstractmethod
    def send_resolution_notice(self, payload: EmergencyAlertPayload) -> NotificationResult:
        """Send an emergency resolved notification to the guardian."""
        pass


class MockNotificationService(BaseNotificationAdapter):
    """Default Mock Notification Service.
    
    Prints a clear, visually distinguished banner in console logs and maintains
    an in-memory delivery audit list for testing and project demonstrations.
    """
    _delivery_history: List[NotificationResult] = []

    def _dispatch_mock(self, payload: EmergencyAlertPayload, event_kind: str) -> NotificationResult:
        settings = get_settings()
        ts_str = payload.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Build decorative console output for terminal presentation
        border = "=" * 68
        print(f"\n{border}")
        print(f"[GUARDIAN ALERT DISPATCHED - {event_kind.upper()}] (SIMULATION MODE)")
        print(f"{border}")
        print(f"  Target Guardian : {payload.guardian_name} ({settings.GUARDIAN_PHONE} / {settings.GUARDIAN_EMAIL})")
        print(f"  Device ID       : {payload.device_id}")
        print(f"  Emergency Type  : {payload.emergency_type}")
        print(f"  Timestamp       : {ts_str}")
        print(f"  Alert Title     : {payload.title}")
        print(f"  Message Body    : {payload.message}")
        if payload.latitude and payload.longitude:
            print(f"  GPS Location    : Lat {payload.latitude:.6f}, Lon {payload.longitude:.6f}")
            print(f"  Google Maps Link: {payload.maps_url}")
        else:
            print("  GPS Location    : [Coordinates Unavailable]")
        print(f"{border}\n")

        msg_id = f"MOCK-MSG-{int(payload.timestamp.timestamp() * 1000)}"
        result = NotificationResult(
            success=True,
            channel="mock_console",
            recipient=f"{payload.guardian_name} <{settings.GUARDIAN_PHONE}>",
            dispatched_at=payload.timestamp,
            message_id=msg_id,
            summary=f"Mock alert successfully delivered: {payload.title}",
            raw_payload=payload.model_dump(),
        )
        self._delivery_history.append(result)
        return result

    def send_emergency_alert(self, payload: EmergencyAlertPayload) -> NotificationResult:
        return self._dispatch_mock(payload, "CRITICAL EMERGENCY")

    def send_cancellation_notice(self, payload: EmergencyAlertPayload) -> NotificationResult:
        return self._dispatch_mock(payload, "EMERGENCY CANCELLED (FALSE ALARM)")

    def send_resolution_notice(self, payload: EmergencyAlertPayload) -> NotificationResult:
        return self._dispatch_mock(payload, "EMERGENCY RESOLVED")

    @classmethod
    def get_history(cls) -> List[NotificationResult]:
        """Retrieve delivery history for verification and tests."""
        return cls._delivery_history

    @classmethod
    def clear_history(cls) -> None:
        """Clear delivery history for clean test runs."""
        cls._delivery_history.clear()


class SimulatedSMSAdapter(BaseNotificationAdapter):
    """Simulates SMS dispatch (e.g. Twilio / GSM SIM800L module).
    
    FUTURE HARDWARE INTEGRATION:
    Replace simulated print with Twilio Client `client.messages.create(...)`
    or AT commands over UART to a SIM800L/SIM7600 GSM modem on the stick.
    """

    def send_emergency_alert(self, payload: EmergencyAlertPayload) -> NotificationResult:
        settings = get_settings()
        sms_text = f"EMERGENCY ALERT: Stick {payload.device_id} reported {payload.emergency_type}. "
        if payload.maps_url:
            sms_text += f"Location: {payload.maps_url}"
        
        print(f"[SMS SIMULATION] Sending SMS to {settings.GUARDIAN_PHONE}: '{sms_text}'")
        return NotificationResult(
            success=True,
            channel="sms_simulated",
            recipient=settings.GUARDIAN_PHONE,
            dispatched_at=payload.timestamp,
            message_id=f"SMS-SIM-{int(payload.timestamp.timestamp())}",
            summary=f"Simulated SMS queued for {settings.GUARDIAN_PHONE}",
            raw_payload={"sms_body": sms_text, **payload.model_dump()},
        )

    def send_cancellation_notice(self, payload: EmergencyAlertPayload) -> NotificationResult:
        settings = get_settings()
        sms_text = f"CANCELLED: User on stick {payload.device_id} cancelled the emergency alert."
        print(f"[SMS SIMULATION] Sending Cancellation SMS to {settings.GUARDIAN_PHONE}: '{sms_text}'")
        return NotificationResult(
            success=True,
            channel="sms_simulated",
            recipient=settings.GUARDIAN_PHONE,
            dispatched_at=payload.timestamp,
            message_id=f"SMS-SIM-{int(payload.timestamp.timestamp())}",
            summary="Simulated cancellation SMS sent",
            raw_payload={"sms_body": sms_text, **payload.model_dump()},
        )

    def send_resolution_notice(self, payload: EmergencyAlertPayload) -> NotificationResult:
        settings = get_settings()
        sms_text = f"RESOLVED: Emergency for stick {payload.device_id} has been marked resolved."
        print(f"[SMS SIMULATION] Sending Resolution SMS to {settings.GUARDIAN_PHONE}: '{sms_text}'")
        return NotificationResult(
            success=True,
            channel="sms_simulated",
            recipient=settings.GUARDIAN_PHONE,
            dispatched_at=payload.timestamp,
            message_id=f"SMS-SIM-{int(payload.timestamp.timestamp())}",
            summary="Simulated resolution SMS sent",
            raw_payload={"sms_body": sms_text, **payload.model_dump()},
        )


class SimulatedFirebaseAdapter(BaseNotificationAdapter):
    """Simulates Firebase Cloud Messaging (FCM) Push Notifications for Guardian Mobile App."""

    def send_emergency_alert(self, payload: EmergencyAlertPayload) -> NotificationResult:
        settings = get_settings()
        fcm_payload = {
            "to": "/topics/guardian_alerts",
            "notification": {
                "title": f"🚨 EMERGENCY: {payload.title}",
                "body": payload.message,
            },
            "data": {
                "device_id": payload.device_id,
                "emergency_type": payload.emergency_type,
                "maps_url": payload.maps_url or "",
                "latitude": str(payload.latitude or ""),
                "longitude": str(payload.longitude or ""),
            }
        }
        print(f"[FCM SIMULATION] Dispatching Push Notification: {fcm_payload['notification']['title']}")
        return NotificationResult(
            success=True,
            channel="firebase_simulated",
            recipient="FCM Topic: guardian_alerts",
            dispatched_at=payload.timestamp,
            message_id=f"FCM-SIM-{int(payload.timestamp.timestamp())}",
            summary="Simulated FCM push notification sent",
            raw_payload=fcm_payload,
        )

    def send_cancellation_notice(self, payload: EmergencyAlertPayload) -> NotificationResult:
        return NotificationResult(
            success=True,
            channel="firebase_simulated",
            recipient="FCM Topic: guardian_alerts",
            dispatched_at=payload.timestamp,
            message_id=f"FCM-SIM-{int(payload.timestamp.timestamp())}",
            summary="Simulated FCM cancellation push notification sent",
            raw_payload=payload.model_dump(),
        )

    def send_resolution_notice(self, payload: EmergencyAlertPayload) -> NotificationResult:
        return NotificationResult(
            success=True,
            channel="firebase_simulated",
            recipient="FCM Topic: guardian_alerts",
            dispatched_at=payload.timestamp,
            message_id=f"FCM-SIM-{int(payload.timestamp.timestamp())}",
            summary="Simulated FCM resolution push notification sent",
            raw_payload=payload.model_dump(),
        )


def get_notification_service() -> BaseNotificationAdapter:
    """Factory to retrieve configured notification adapter."""
    settings = get_settings()
    adapter = settings.NOTIFICATION_ADAPTER.lower()
    if adapter == "sms":
        return SimulatedSMSAdapter()
    elif adapter in ("firebase", "fcm"):
        return SimulatedFirebaseAdapter()
    return MockNotificationService()
