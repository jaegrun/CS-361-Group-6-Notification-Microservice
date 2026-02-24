import requests
import time
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:5000"

def run_demo():
    print("--- STARTING MICROSERVICE TEST ---")

    # 1. Schedule a notification (5 seconds in the future)
    future_time = (datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat()
    payload = {
        "message": "Assignment 7 Demo Notification",
        "run_at": future_time
    }
    
    print(f"\n1) Requesting: POST /schedule")
    r_sched = requests.post(f"{BASE_URL}/schedule", json=payload)
    data = r_sched.json()
    print(f"   Response ({r_sched.status_code}): {data}")
    
    notif_id = data['notification_id']

    # 2. Check status immediately (should be 'scheduled')
    print(f"\n2) Requesting: GET /status/{notif_id}")
    r_status = requests.get(f"{BASE_URL}/status/{notif_id}")
    print(f"   Response ({r_status.status_code}): {r_status.json()}")

    # 3. Wait for the background worker to process it
    print("\n3) Waiting 6 seconds for background worker to 'send' the notification...")
    time.sleep(6)

    # 4. Check status again (should now be 'sent')
    print(f"\n4) Requesting: GET /status/{notif_id}")
    r_final = requests.get(f"{BASE_URL}/status/{notif_id}")
    print(f"   Response ({r_final.status_code}): {r_final.json()}")

    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    run_demo()