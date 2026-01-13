"""Heartbeat, log, and artifact POST helpers (skeleton)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping, Sequence
import json
import time
import urllib.request
import urllib.error
import ssl
import http.client


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(tz=timezone.utc)


def post_heartbeat(
    server_url: str, run_id: str, token: str, summary: str | None
) -> None:
    """Send a heartbeat to the backend."""
    _post(
        f"{server_url.rstrip('/')}/runs/{run_id}/heartbeat",
        token,
        {"observed_at": utcnow().isoformat(), "summary": summary},
    )


def post_log(
    server_url: str,
    run_id: str,
    token: str,
    level: str,
    message: str,
    extra: Mapping[str, object] | None = None,
) -> None:
    """Send a log entry to the backend."""
    _post(
        f"{server_url.rstrip('/')}/runs/{run_id}/logs",
        token,
        {
            "created_at": utcnow().isoformat(),
            "level": level,
            "message": message,
            "extra": extra or {},
        },
    )


def post_artifacts(
    server_url: str,
    run_id: str,
    token: str,
    artifacts: Sequence[Mapping[str, object]],
) -> None:
    """Send artifact manifest entries to the backend."""
    for artifact in artifacts:
        payload: Mapping[str, object] | object = artifact
        if isinstance(artifact, Mapping):
            inner = artifact.get("payload", artifact)
            if isinstance(inner, Mapping):
                payload = inner
        _post(
            f"{server_url.rstrip('/')}/runs/{run_id}/artifacts",
            token,
            {
                "artifact_type": str(artifact.get("artifact_type", "unknown")),
                "payload": payload,
            },
        )


def post_completion(server_url: str, run_id: str, token: str, summary: str) -> None:
    """Mark run complete."""
    _post(
        f"{server_url.rstrip('/')}/runs/{run_id}/complete",
        token,
        {"summary": summary},
    )


def post_error(
    server_url: str, run_id: str, token: str, reason: str, summary: str | None = None
) -> None:
    """Mark run errored."""
    _post(
        f"{server_url.rstrip('/')}/runs/{run_id}/error",
        token,
        {"summary": summary or "", "reason": reason},
    )


def _post(url: str, token: str, body: Mapping[str, object]) -> None:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Run-Token": token,
        },
        method="POST",
    )
    _urlopen_with_retries(
        req,
        timeout_seconds=20,
        attempts=6,
        base_delay_seconds=0.5,
    )


def _urlopen_with_retries(
    req: urllib.request.Request,
    timeout_seconds: int,
    attempts: int,
    base_delay_seconds: float,
) -> None:
    """Best-effort POST with retries for transient network errors."""
    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            with urllib.request.urlopen(
                req, timeout=timeout_seconds
            ) as resp:  # pragma: no cover - network
                resp.read()
            return
        except (
            TimeoutError,
            urllib.error.URLError,
            http.client.RemoteDisconnected,
            ssl.SSLError,
        ) as exc:
            last_exc = exc
            if i == attempts - 1:
                break
            delay = base_delay_seconds * (2**i)
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc
