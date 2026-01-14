"""HTTP Provider wrapper for QCG Memory API."""
import json
import urllib.request
import urllib.error
from typing import List, Optional


class HttpProvider:
    def __init__(self, endpoint: str, timeout: int = 60):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, data=None):
        url = f"{self.endpoint}{path}"
        headers = {"Content-Type": "application/json"}
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode())

    def reset(self, seed: int = 42):
        self._request("POST", "/reset", {"seed": seed})

    def store(self, pattern: List[float], cue: List[float], steps: int = 50):
        self._request("POST", "/store", {"pattern": pattern, "cue": cue, "steps": steps})

    def recall(self, cue: List[float], steps: int = 30) -> List[float]:
        resp = self._request("POST", "/recall", {"cue": cue, "steps": steps})
        return resp.get("pattern", resp.get("recalled", []))
