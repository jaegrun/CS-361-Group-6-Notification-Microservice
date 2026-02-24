from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "http://127.0.0.1:5000"


def main() -> None:
    run_at = (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()
    payload = {
        "message": "CS 361 demo notification",
        "run_at": run_at,
    }

    print("1) Scheduling notification...")
    schedule_response = requests.post(f"{BASE_URL}/schedule", json=payload, timeout=5)
    print(f"   HTTP {schedule_response.status_code} -> {schedule_response.json()}")
    schedule_data = schedule_response.json()
    notification_id = schedule_data.get("notification_id")
    if not notification_id:
        print("   Could not get notification_id. Exiting.")
        return

    print("\n2) Checking status...")
    status_response = requests.get(f"{BASE_URL}/status/{notification_id}", timeout=5)
    print(f"   HTTP {status_response.status_code} -> {status_response.json()}")

    print("\n3) Cancelling notification...")
    cancel_response = requests.delete(f"{BASE_URL}/cancel/{notification_id}", timeout=5)
    print(f"   HTTP {cancel_response.status_code} -> {cancel_response.json()}")

    print("\n4) Checking status after cancel...")
    status_after_cancel = requests.get(f"{BASE_URL}/status/{notification_id}", timeout=5)
    print(f"   HTTP {status_after_cancel.status_code} -> {status_after_cancel.json()}")


if __name__ == "__main__":
    main()
