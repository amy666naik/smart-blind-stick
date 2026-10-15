"""Mock Smart Stick Device Simulator.

Simulates periodic check-ins, battery decay, and GPS movement for testing the backend
without physical ESP32 hardware.
"""
import argparse
import random
import time
import requests

from app.services.location_service import LocationService


def simulate_stick(
    base_url: str = "http://127.0.0.1:8000",
    device_id: str = "STICK_001",
    interval: int = 5,
    once: bool = False,
):
    print(f"🦯 Starting device simulation for '{device_id}' -> {base_url}")
    battery = 98.0
    lat, lon = 12.9716, 77.5946

    while True:
        # Simulate slight GPS walking movement
        lat, lon = LocationService.generate_mock_gps_point(base_lat=lat, base_lon=lon, drift_radius_meters=15.0)
        battery = max(0.0, round(battery - random.uniform(0.05, 0.2), 1))

        payload = {
            "device_id": device_id,
            "battery": battery,
            "status": "active",
            "latitude": lat,
            "longitude": lon,
            "gps_available": True,
        }

        try:
            res = requests.post(f"{base_url}/api/device/data", json=payload, timeout=5)
            print(f"[{time.strftime('%X')}] Check-in: Status={res.status_code}, Battery={battery}%, GPS=({lat}, {lon})")
        except Exception as err:
            print(f"[{time.strftime('%X')}] ❌ Check-in failed: {err}")

        if once:
            break
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Simulate Smart Blind Stick Hardware")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API base URL")
    parser.add_argument("--device-id", default="STICK_001", help="Device ID")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between check-ins")
    parser.add_argument("--once", action="store_true", help="Send single check-in then exit")
    args = parser.parse_args()

    simulate_stick(
        base_url=args.base_url,
        device_id=args.device_id,
        interval=args.interval,
        once=args.once,
    )


if __name__ == "__main__":
    main()
