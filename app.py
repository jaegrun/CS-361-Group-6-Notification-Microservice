from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any
from uuid import uuid4

from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for notifications.
notifications: Dict[str, Dict[str, Any]] = {}
notifications_lock = threading.Lock()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso8601(timestamp: str) -> datetime:
    # Support common ISO-8601 formats including a trailing "Z".
    normalized = timestamp.replace("Z", "+00:00")
    run_at = datetime.fromisoformat(normalized)
    if run_at.tzinfo is None:
        raise ValueError("Timestamp must include timezone information.")
    return run_at.astimezone(timezone.utc)


def process_due_notifications() -> int:
    now = _utc_now()
    sent_count = 0

    with notifications_lock:
        for notification in notifications.values():
            if notification["status"] != "scheduled":
                continue
            if notification["run_at"] <= now:
                print(f'SENDING NOTIFICATION: {notification["message"]}')
                notification["status"] = "sent"
                notification["sent_at"] = now.isoformat()
                sent_count += 1

    return sent_count


def _worker_loop() -> None:
    while True:
        process_due_notifications()
        time.sleep(1)


@app.post("/schedule")
def schedule_notification():
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    run_at_raw = data.get("run_at")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": '"message" must be a non-empty string.'}), 400
    if not isinstance(run_at_raw, str):
        return jsonify({"error": '"run_at" must be an ISO-8601 timestamp string.'}), 400

    try:
        run_at = _parse_iso8601(run_at_raw)
    except ValueError as exc:
        return jsonify({"error": f"Invalid run_at timestamp: {exc}"}), 400

    notification_id = str(uuid4())
    with notifications_lock:
        notifications[notification_id] = {
            "notification_id": notification_id,
            "message": message.strip(),
            "run_at": run_at,
            "status": "scheduled",
            "created_at": _utc_now().isoformat(),
        }

    return (
        jsonify({"notification_id": notification_id, "status": "scheduled"}),
        201,
    )


@app.delete("/cancel/<notification_id>")
def cancel_notification(notification_id: str):
    with notifications_lock:
        notification = notifications.get(notification_id)
        if notification is None:
            return jsonify({"error": "notification_id not found"}), 404
        if notification["status"] == "sent":
            return jsonify({"notification_id": notification_id, "status": "sent"}), 409

        notification["status"] = "cancelled"
        notification["cancelled_at"] = _utc_now().isoformat()

    return jsonify({"notification_id": notification_id, "status": "cancelled"}), 200


@app.get("/status/<notification_id>")
def get_status(notification_id: str):
    with notifications_lock:
        notification = notifications.get(notification_id)
        if notification is None:
            return jsonify({"error": "notification_id not found"}), 404

        response = {
            "notification_id": notification["notification_id"],
            "status": notification["status"],
            "run_at": notification["run_at"].isoformat(),
        }
        if "sent_at" in notification:
            response["sent_at"] = notification["sent_at"]
        if "cancelled_at" in notification:
            response["cancelled_at"] = notification["cancelled_at"]

    return jsonify(response), 200


@app.get("/process")
def process_notifications_endpoint():
    sent_count = process_due_notifications()
    return jsonify({"processed": True, "sent_count": sent_count}), 200


if __name__ == "__main__":
    worker = threading.Thread(target=_worker_loop, daemon=True)
    worker.start()
    app.run(host="127.0.0.1", port=5000, debug=False)
