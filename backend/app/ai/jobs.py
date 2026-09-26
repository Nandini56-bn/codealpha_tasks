"""In-memory background job store for long-running Lyria generation."""

from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Callable, Dict, Optional

_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}


def create_job(kind: str, payload: Dict[str, Any]) -> str:
    job_id = uuid.uuid4().hex[:12]
    with _lock:
        _jobs[job_id] = {
            "id": job_id,
            "kind": kind,
            "status": "queued",
            "message": "Queued",
            "created_at": time.time(),
            "payload": payload,
            "result": None,
            "error": None,
            "error_code": None,
        }
    return job_id


def update_job(job_id: str, **fields: Any) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job.update(fields)


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return None
        public = {k: v for k, v in job.items() if k != "payload"}
        return public


def run_in_background(job_id: str, worker: Callable[[], None]) -> None:
    def _wrap() -> None:
        update_job(job_id, status="running", message="Generating with Lyria 3.5...")
        try:
            worker()
        except Exception as exc:
            update_job(
                job_id,
                status="failed",
                message=str(exc),
                error=str(exc),
                error_code=getattr(exc, "code", "error"),
            )

    thread = threading.Thread(target=_wrap, daemon=True)
    thread.start()
