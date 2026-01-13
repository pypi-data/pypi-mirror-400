"""Bootstrap payload fetch/validation (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
import urllib.request
import urllib.error
import ssl
import http.client


@dataclass
class BootstrapPayload:
    """Minimal representation of the backend bootstrap payload."""

    prompt: str


def fetch_bootstrap_payload(
    server_url: str,
    run_id: str,
    token: str,
) -> BootstrapPayload:
    """Retrieve bootstrap payload from the backend server.

    Raises:
        NotImplementedError: placeholder until HTTP wiring is added.
    """

    url = f"{server_url.rstrip('/')}/runs/{run_id}/bootstrap"
    req = urllib.request.Request(url, headers={"X-Run-Token": token})
    payload = _urlopen_json_with_retries(
        req,
        timeout_seconds=30,
        attempts=6,
        base_delay_seconds=0.5,
    )
    inner = payload.get("payload", {})
    return BootstrapPayload(
        prompt=str(inner.get("prompt", "")),
    )


def _urlopen_json_with_retries(
    req: urllib.request.Request,
    timeout_seconds: int,
    attempts: int,
    base_delay_seconds: float,
) -> dict:
    """Best-effort JSON fetch with retries.

    Fly.io apps can be cold-started (min_machines_running=0), and network edges
    can occasionally drop connections. This helper retries common transient
    failures with exponential backoff.
    """
    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
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
