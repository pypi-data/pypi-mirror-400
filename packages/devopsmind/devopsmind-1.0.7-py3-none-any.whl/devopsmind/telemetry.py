import requests

TELEMETRY_URL = "https://infraforgelabs.in/meta/devopsmind/event"

def send_event(event: str):
    try:
        requests.post(
            TELEMETRY_URL,
            json={"event": event},
            timeout=2,
        )
    except Exception:
        # Silent by design
        pass
