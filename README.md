# Notification Microservice (CS 361)

## Service Description

This microservice provides a simple notification scheduling API for CS 361 projects. Clients can:

- Schedule a notification with a future `run_at` timestamp.
- Cancel a notification before it is sent.
- Query a notification's current status.

The service stores notifications in an in-memory dictionary for this milestone. A background worker checks due notifications and logs:

`SENDING NOTIFICATION: [message]`

to the console, then marks the notification as `sent`.

## Technology

- Python 3
- Flask REST API

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the microservice:

```bash
python app.py
```

3. Run the separate client test script (in another terminal):

```bash
python test_program.py
```

## Communication Contract

### Base URL

`http://127.0.0.1:5000`

### Endpoint: `POST /schedule`

Schedules a new notification.

#### How to REQUEST data (Python example)

```python
import requests

payload = {
    "message": "Do homework",
    "run_at": "2026-02-23T20:30:00+00:00"
}

response = requests.post("http://127.0.0.1:5000/schedule", json=payload, timeout=5)
print(response.status_code, response.json())
```

#### How to RECEIVE data (JSON example)

```json
{
  "notification_id": "1d0ea64a-0f3d-40a5-9cf2-1d5be99c0a8f",
  "status": "scheduled"
}
```

### Endpoint: `DELETE /cancel/<notification_id>`

Cancels a scheduled notification.

#### Example response

```json
{
  "notification_id": "1d0ea64a-0f3d-40a5-9cf2-1d5be99c0a8f",
  "status": "cancelled"
}
```

### Endpoint: `GET /status/<notification_id>`

Returns status details for a notification.

#### Example response

```json
{
  "notification_id": "1d0ea64a-0f3d-40a5-9cf2-1d5be99c0a8f",
  "status": "scheduled",
  "run_at": "2026-02-23T20:30:00+00:00"
}
```

### Endpoint: `GET /process`

Optional manual trigger to process due notifications immediately.

#### Example response

```json
{
  "processed": true,
  "sent_count": 1
}
```

## UML Sequence Diagram (Placeholder)

Add UML sequence diagram here to show:

1. Client sends `POST /schedule`
2. Service returns `notification_id`
3. Client checks `GET /status/<notification_id>`
4. Client optionally sends `DELETE /cancel/<notification_id>`
5. Worker logs and marks notification as `sent` when due
