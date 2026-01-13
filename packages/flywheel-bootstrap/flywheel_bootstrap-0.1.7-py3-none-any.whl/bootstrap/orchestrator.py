"""Top-down orchestration for the bootstrap flow.

Implementation is intentionally skeletal; individual steps will be filled in once
design details are finalized.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os
import sys
import threading
import json
import shutil

from bootstrap.constants import (
    DEFAULT_ARTIFACT_MANIFEST,
    DEFAULT_RUN_ROOT,
    DEFAULT_SERVER_URL,
    ENV_RUN_ID,
    ENV_RUN_TOKEN,
    ENV_SERVER_URL,
    HEARTBEAT_INTERVAL_SECONDS,
)
from bootstrap.config_loader import UserConfig, load_codex_config
from bootstrap.install import codex_login_status_ok, codex_on_path, ensure_codex
from bootstrap.payload import BootstrapPayload, fetch_bootstrap_payload
from bootstrap.prompts import build_prompt_text
from bootstrap.runner import (
    CodexInvocation,
    CodexEvent,
    build_invocation,
    run_and_stream,
)
from bootstrap.telemetry import (
    post_artifacts,
    post_completion,
    post_error,
    post_heartbeat,
    post_log,
)
from bootstrap.artifacts import read_manifest


@dataclass
class BootstrapConfig:
    """User-supplied CLI arguments plus derived defaults."""

    run_id: str
    capability_token: str
    config_path: Path
    server_url: str = DEFAULT_SERVER_URL
    run_root: Path = DEFAULT_RUN_ROOT
    artifact_manifest: str = DEFAULT_ARTIFACT_MANIFEST


class BootstrapOrchestrator:
    """Coordinates install, payload fetch, Codex launch, telemetry, and artifacts."""

    def __init__(self, config: BootstrapConfig) -> None:
        self.config = config
        self._mock_codex = bool(os.environ.get("BOOTSTRAP_MOCK_CODEX"))
        self.user_config: UserConfig | None = None
        self.bootstrap_payload: BootstrapPayload | None = None
        self.workspace: Path | None = None
        self.codex_executable: Path | None = None
        self.codex_run_id: str | None = None
        self.heartbeat_thread: threading.Thread | None = None
        self._stop_heartbeats = threading.Event()
        self.last_stderr: str = ""  # Captured stderr for error reporting

    def run(self) -> int:
        """Execute the bootstrap flow.

        Returns:
            Process exit code (0 for success, non-zero for failure).
        """

        try:
            self._ensure_prerequisites()
            self._load_user_config()
            self._resolve_workspace()
            self._ensure_codex_available()
            self._fetch_bootstrap_payload()
            exit_code = self._launch_codex_and_stream()
            self._collect_and_post_artifacts(exit_code)
            return 0
        except SystemExit:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            post_error(
                self.config.server_url,
                self.config.run_id,
                self.config.capability_token,
                reason=repr(exc),
                summary="bootstrap failure",
            )
            print(f"bootstrap failed: {exc}", file=sys.stderr)
            return 1
        finally:
            self._stop_heartbeats.set()
            if self.heartbeat_thread and self.heartbeat_thread.is_alive():
                self.heartbeat_thread.join(timeout=2)

    # --- individual steps (to be implemented) ---

    def _ensure_prerequisites(self) -> None:
        """Validate required binaries/env vars and fail fast if missing."""
        if not self.config.run_id:
            raise SystemExit("missing run id")
        if not self.config.capability_token:
            raise SystemExit("missing capability token")
        if not self.config.config_path.exists():
            raise SystemExit(f"config file not found: {self.config.config_path}")

    def _load_user_config(self) -> None:
        """Read the user's Codex config.toml for sandbox/workspace settings."""
        self.user_config = load_codex_config(self.config.config_path)
        for warning in self.user_config.warnings:
            print(f"bootstrap warning: {warning}", file=sys.stderr)

    def _resolve_workspace(self) -> None:
        """Decide which working directory to hand to Codex (respect user config if set)."""
        assert self.user_config is not None
        if self.user_config.working_dir:
            # Support the documented "<run_id>" placeholder in config paths.
            raw = str(self.user_config.working_dir)
            if "<run_id>" in raw:
                raw = raw.replace("<run_id>", self.config.run_id)
            workdir = Path(raw).expanduser().resolve()
        else:
            workdir = self.config.run_root / self.config.run_id
        workdir.mkdir(parents=True, exist_ok=True)

        manifest_path = workdir / self.config.artifact_manifest
        if self.user_config.writable_roots:
            ok = False
            for root in self.user_config.writable_roots:
                try:
                    manifest_path.relative_to(root)
                    ok = True
                    break
                except ValueError:
                    continue
            if not ok:
                roots = ", ".join(str(r) for r in self.user_config.writable_roots)
                raise SystemExit(
                    f"manifest path {manifest_path} not in sandbox writable_roots ({roots}); "
                    "please add a writable root or adjust config"
                )
        self.workspace = workdir

    def _ensure_codex_available(self) -> None:
        """Skip install if present; otherwise download tarball and prepend to PATH."""
        if self._mock_codex:
            return
        codex_path: Path | None = None
        if codex_on_path():
            found = shutil.which("codex")
            if found:
                codex_path = Path(found)
                self.codex_executable = codex_path
        else:
            download_dir = self.workspace or self.config.run_root
            self.codex_executable = ensure_codex(download_dir=download_dir)
            codex_path = self.codex_executable

        if codex_path is None:
            codex_path = Path("codex")
        self._ensure_codex_authenticated(codex_path)

    def _fetch_bootstrap_payload(self) -> None:
        """Call backend /runs/{id}/bootstrap to get the task prompt."""
        self.bootstrap_payload = fetch_bootstrap_payload(
            self.config.server_url, self.config.run_id, self.config.capability_token
        )

    def _ensure_codex_authenticated(self, codex_path: Path) -> None:
        """Fail fast if codex is present but not logged in."""
        if codex_login_status_ok(codex_path):
            return
        raise SystemExit(
            "Codex isn't authenticated. Run `codex login` (browser/device flow) or "
            "`printenv OPENAI_API_KEY | codex login --with-api-key` then rerun the bootstrap."
        )

    def _launch_codex_and_stream(self) -> int:
        """Run codex exec --json, forward logs/heartbeats, and capture exit status."""
        assert self.workspace is not None
        assert self.bootstrap_payload is not None
        assert self.user_config is not None

        prompt_text = build_prompt_text(
            server_prompt=self.bootstrap_payload.prompt,
            workspace_instructions=self.user_config.workspace_instructions,
            artifact_manifest=self.config.artifact_manifest,
        )

        if self._mock_codex:
            # Fast-path: emit one heartbeat, a couple logs, a run id, and exit 0.
            post_heartbeat(
                self.config.server_url,
                self.config.run_id,
                self.config.capability_token,
                summary="alive (mock)",
            )
            for event in self._mock_codex_events():
                self._handle_event(event)
            self._write_mock_manifest()
            return 0

        codex_path = self.codex_executable or Path("codex")
        env = os.environ.copy()
        env.update(
            {
                "FLYWHEEL_RUN_ID": self.config.run_id,
                "FLYWHEEL_RUN_TOKEN": self.config.capability_token,
                "FLYWHEEL_SERVER": self.config.server_url,
                "FLYWHEEL_WORKSPACE": str(self.workspace.resolve()),
            }
        )

        # Ensure Codex actually sees the same config file bootstrap parsed.
        # Codex reads config from CODEX_HOME/config.toml; point it at a per-run copy.
        try:
            codex_home = self.workspace / ".codex_home"
            codex_home.mkdir(parents=True, exist_ok=True)

            # Copy config but expand ~ paths so codex sees absolute paths
            config_text = self.config.config_path.read_text(encoding="utf-8")
            # Expand common tilde patterns in the config
            home_dir = str(Path.home())
            config_text = config_text.replace('"~/', f'"{home_dir}/')
            config_text = config_text.replace("'~/", f"'{home_dir}/")
            (codex_home / "config.toml").write_text(config_text, encoding="utf-8")

            # Also copy auth credentials from user's default codex home so the
            # spawned codex process stays authenticated.
            # TODO: more sophisticated auth
            user_codex_home = Path.home() / ".codex"
            user_auth = user_codex_home / "auth.json"
            if user_auth.exists():
                shutil.copyfile(user_auth, codex_home / "auth.json")

            env["CODEX_HOME"] = str(codex_home)
        except Exception as exc:
            post_log(
                self.config.server_url,
                self.config.run_id,
                self.config.capability_token,
                level="warning",
                message="failed to prepare CODEX_HOME config override; continuing",
                extra={"error": repr(exc)},
            )

        # Pass sandbox settings as proper CLI flags
        # For provisioned instances, we use --yolo to completely bypass sandbox and approvals
        extra_flags: list[str] = []
        if self.user_config.sandbox_mode:
            if self.user_config.sandbox_mode == "danger-full-access":
                # Use --yolo (--dangerously-bypass-approvals-and-sandbox) for unrestricted access
                # This is safe on provisioned instances since they're isolated VMs
                extra_flags.append("--yolo")
            else:
                extra_flags.extend(["--sandbox", self.user_config.sandbox_mode])

        invocation = build_invocation(
            codex_executable=Path(codex_path),
            prompt=prompt_text,
            workdir=self.workspace,
            env=env,
            extra_flags=tuple(extra_flags),
        )

        # Start heartbeat thread
        self._stop_heartbeats.clear()
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True
        )
        self.heartbeat_thread.start()

        exit_code: int = 1
        for event in run_and_stream(invocation):
            self._handle_event(event)
        if invocation.exit_code is not None:
            exit_code = invocation.exit_code
        # Capture stderr for error reporting
        if invocation.stderr_output:
            self.last_stderr = invocation.stderr_output
        return exit_code

    def _collect_and_post_artifacts(self, exit_code: int) -> None:
        """Read manifest (and optional resume attempt) then POST /artifacts/complete/error."""
        assert self.workspace is not None
        manifest_path = self.workspace / self.config.artifact_manifest
        artifacts = self._load_artifacts_with_content(manifest_path)

        # Optional auto-resume once if missing
        if not artifacts and self.codex_run_id:
            self._attempt_resume(manifest_path)
            artifacts = self._load_artifacts_with_content(manifest_path)

        if artifacts:
            post_artifacts(
                self.config.server_url,
                self.config.run_id,
                self.config.capability_token,
                artifacts,
            )

        if exit_code == 0:
            summary = "codex run completed"
            post_completion(
                self.config.server_url,
                self.config.run_id,
                self.config.capability_token,
                summary,
            )
        else:
            # Include stderr in error reason for debugging
            reason = f"codex exit code {exit_code}"
            if self.last_stderr:
                # Truncate stderr to avoid overly long error messages
                stderr_preview = self.last_stderr[:2000]
                if len(self.last_stderr) > 2000:
                    stderr_preview += "... (truncated)"
                reason = f"{reason}\nstderr: {stderr_preview}"
            post_error(
                self.config.server_url,
                self.config.run_id,
                self.config.capability_token,
                reason=reason,
                summary="codex failed",
            )

    def _load_artifacts_with_content(
        self, manifest_path: Path
    ) -> list[dict[str, object]]:
        """Load artifacts and inline content when a path is provided.

        For text/html artifacts, if payload includes a "path" (or "file") inside the workspace,
        read the file as UTF-8 and attach it as payload["content"].
        For image artifacts, read as binary and create a base64 data URL.
        This keeps artifacts self-contained for server-side rendering.
        Best-effort; failures are logged and skipped.

        Size limit: 2MB per artifact to prevent huge payloads.
        """
        import base64
        import mimetypes

        MAX_ARTIFACT_SIZE = 25 * 1024 * 1024  # 25MB

        assert self.workspace is not None
        artifacts = read_manifest(manifest_path)
        enriched: list[dict[str, object]] = []

        for artifact in artifacts:
            try:
                artifact_type = str(artifact.get("artifact_type", "")).lower()
                payload = artifact.get("payload", {})

                # Handle text and html artifacts - inline as content
                if artifact_type in ("text", "html") and isinstance(payload, dict):
                    path_str = payload.get("path") or payload.get("file")
                    if isinstance(path_str, str) and path_str:
                        resolved = self._resolve_artifact_path(path_str)
                        if resolved and resolved.is_file():
                            file_size = resolved.stat().st_size
                            if file_size > MAX_ARTIFACT_SIZE:
                                payload = dict(payload)
                                payload["rendering_error"] = (
                                    f"File too large ({file_size} bytes, max {MAX_ARTIFACT_SIZE})"
                                )
                            else:
                                try:
                                    payload = dict(payload)
                                    payload["content"] = resolved.read_text(
                                        encoding="utf-8"
                                    )
                                except UnicodeDecodeError:
                                    self._log(
                                        f"failed to read {artifact_type} artifact at {resolved} (encoding)",
                                        level="warning",
                                    )
                        artifact = dict(artifact)
                        artifact["payload"] = payload

                # Handle image artifacts - inline as data_url
                elif artifact_type == "image" and isinstance(payload, dict):
                    path_str = payload.get("path") or payload.get("file")
                    if isinstance(path_str, str) and path_str:
                        resolved = self._resolve_artifact_path(path_str)
                        if resolved and resolved.is_file():
                            file_size = resolved.stat().st_size
                            if file_size > MAX_ARTIFACT_SIZE:
                                payload = dict(payload)
                                payload["rendering_error"] = (
                                    f"File too large ({file_size} bytes, max {MAX_ARTIFACT_SIZE})"
                                )
                            else:
                                try:
                                    image_data = resolved.read_bytes()
                                    mime_type, _ = mimetypes.guess_type(str(resolved))
                                    if not mime_type:
                                        mime_type = "image/png"  # default fallback
                                    b64 = base64.b64encode(image_data).decode("ascii")
                                    payload = dict(payload)
                                    payload["data_url"] = (
                                        f"data:{mime_type};base64,{b64}"
                                    )
                                except Exception as exc:
                                    self._log(
                                        f"failed to read image artifact at {resolved}: {exc}",
                                        level="warning",
                                    )
                        artifact = dict(artifact)
                        artifact["payload"] = payload

                # Handle table artifacts - inline as content
                elif artifact_type == "table" and isinstance(payload, dict):
                    path_str = payload.get("path") or payload.get("file")
                    if isinstance(path_str, str) and path_str:
                        resolved = self._resolve_artifact_path(path_str)
                        if resolved and resolved.is_file():
                            file_size = resolved.stat().st_size
                            if file_size > MAX_ARTIFACT_SIZE:
                                payload = dict(payload)
                                payload["rendering_error"] = (
                                    f"File too large ({file_size} bytes, max {MAX_ARTIFACT_SIZE})"
                                )
                            else:
                                try:
                                    payload = dict(payload)
                                    payload["content"] = resolved.read_text(
                                        encoding="utf-8"
                                    )
                                except UnicodeDecodeError:
                                    self._log(
                                        f"failed to read table artifact at {resolved} (encoding)",
                                        level="warning",
                                    )
                        artifact = dict(artifact)
                        artifact["payload"] = payload

            except Exception as exc:  # pragma: no cover - defensive
                self._log(f"artifact enrichment error: {exc}", level="warning")
            enriched.append(dict(artifact))
        return enriched

    def _resolve_artifact_path(self, path_str: str) -> Path | None:
        """Resolve artifact path within workspace, returning None if invalid."""
        assert self.workspace is not None
        path = Path(path_str)
        resolved = (self.workspace / path).resolve()
        workspace_root = self.workspace.resolve()
        if resolved == workspace_root or workspace_root in resolved.parents:
            return resolved
        self._log(f"skipping artifact outside workspace: {resolved}", level="warning")
        return None

    def _heartbeat_loop(self) -> None:
        while not self._stop_heartbeats.is_set():
            try:
                post_heartbeat(
                    self.config.server_url,
                    self.config.run_id,
                    self.config.capability_token,
                    summary="alive",
                )
            except Exception as exc:  # pragma: no cover - best effort
                print(f"heartbeat failed: {exc}", file=sys.stderr)
            self._stop_heartbeats.wait(HEARTBEAT_INTERVAL_SECONDS)

    def _handle_event(self, event: CodexEvent) -> None:
        post_log(
            self.config.server_url,
            self.config.run_id,
            self.config.capability_token,
            level="info",
            message=str(event.raw),
            extra={},
        )
        if isinstance(event.raw, dict):
            run_id = event.raw.get("run_id")
            if isinstance(run_id, str):
                self.codex_run_id = run_id

    def _attempt_resume(self, manifest_path: Path) -> None:
        if not self.codex_run_id:
            return
        codex_path = self.codex_executable or Path("codex")
        resume_cmd = [str(codex_path), "resume", self.codex_run_id]
        post_log(
            self.config.server_url,
            self.config.run_id,
            self.config.capability_token,
            level="info",
            message="attempting codex resume to collect artifacts",
            extra={"command": resume_cmd},
        )
        try:
            run_and_stream(
                CodexInvocation(
                    args=resume_cmd,
                    env={},
                    workdir=self.workspace or Path("."),
                )
            )
        except Exception as exc:  # pragma: no cover
            post_log(
                self.config.server_url,
                self.config.run_id,
                self.config.capability_token,
                level="error",
                message="codex resume failed",
                extra={"error": repr(exc)},
            )

    def _log(
        self, message: str, level: str = "info", extra: dict[str, object] | None = None
    ) -> None:
        """Lightweight logger that routes to telemetry."""
        post_log(
            self.config.server_url,
            self.config.run_id,
            self.config.capability_token,
            level=level,
            message=message,
            extra=extra or {},
        )

    # --- mock codex helpers (used in tests via BOOTSTRAP_MOCK_CODEX=1) ---

    def _mock_codex_events(self):
        yield CodexEvent(raw={"run_id": "mock-codex-run"})
        yield CodexEvent(raw={"message": "mock: starting work"})
        yield CodexEvent(raw={"message": "mock: finished"})
        self.codex_run_id = "mock-codex-run"

    def _write_mock_manifest(self) -> None:
        assert self.workspace is not None
        manifest_path = self.workspace / self.config.artifact_manifest
        manifest = [{"artifact_type": "text", "payload": {"content": "mock artifact"}}]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def build_config(args: Any) -> BootstrapConfig:
    """Construct BootstrapConfig from CLI args and environment."""

    server_url = args.server or os.environ.get(ENV_SERVER_URL, DEFAULT_SERVER_URL)
    config_path = Path(args.config).expanduser().resolve()
    return BootstrapConfig(
        run_id=args.run_id or _env_or_throw(ENV_RUN_ID, "run id"),
        capability_token=args.token or _env_or_throw(ENV_RUN_TOKEN, "capability token"),
        config_path=config_path,
        server_url=server_url,
    )


def _env_or_throw(var: str, label: str) -> str:
    value = os.environ.get(var)
    if not value:
        raise SystemExit(f"missing {label} (pass flag or set {var})")
    return value
