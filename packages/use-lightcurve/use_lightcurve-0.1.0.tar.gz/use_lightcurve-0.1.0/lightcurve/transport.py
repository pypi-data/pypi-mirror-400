import threading
import queue
import time
import requests
from typing import Dict, Any, Optional
from .schemas import RunPayload

class BackgroundTransport:
    def __init__(self, api_key: Optional[str], api_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self._queue: queue.Queue[RunPayload] = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def send(self, payload: RunPayload):
        self._queue.put(payload)

    def close(self):
        self._stop_event.set()
        self._thread.join(timeout=2.0)

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                payload = self._queue.get(timeout=1.0)
                self._post_payload(payload)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                # In production, we should log this properly or use a dead-letter queue
                # For now, we print to stderr if it's critical, or silent in production
                pass

    def _post_payload(self, payload: RunPayload):
        # Retry logic could go here (3x exponential backoff)
        url = f"{self.api_url}/ingest/trajectory" 
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key or "" 
        }

        try:
            # We dump to json using Pydantic
            data = payload.model_dump(mode='json')
            resp = requests.post(url, json=data, headers=headers, timeout=5)
            if resp.status_code >= 400:
                print(f"Error sending trace: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"Network error sending trace: {e}")
            pass
