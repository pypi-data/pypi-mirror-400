from __future__ import annotations

import os, json, platform
from pathlib import Path
from typing import Any, Dict, Optional, Union

import httpx


def publish_report(
    url: str,
    report: Union[str, Dict[str, Any]],
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    POST report to the given URL directly.
    """
    meta = meta or {}

    if isinstance(report, str):
        report_data = json.loads(Path(report).read_text(encoding="utf-8"))
    else:
        report_data = report

    payload = {
        "meta": meta,
        "report_json": report_data,
        "client": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
    }

    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("MEMORYBENCH_API_KEY") or os.getenv("MEMORY_HARNESS_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    with httpx.Client(timeout=30.0) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()
