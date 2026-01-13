"""Codex install/detection helpers (skeleton)."""

from __future__ import annotations

import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path
import subprocess
import tempfile
import platform

from bootstrap.constants import CODEX_RELEASE_BASE, DEFAULT_CODEX_VERSION


def codex_on_path() -> bool:
    """Return True if `codex` is already available on PATH."""
    return shutil.which("codex") is not None


def codex_login_status_ok(executable: Path | str = "codex") -> bool:
    """Return True if `codex login status` succeeds."""
    try:
        result = subprocess.run(
            [str(executable), "login", "status"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def ensure_codex(version: str | None = None, download_dir: Path | None = None) -> Path:
    """Ensure codex binary is available.

    Args:
        version: Optional explicit version string to install.
        download_dir: Optional directory where the tarball should be unpacked.

    Returns:
        Path to the resolved codex executable.
    """
    if codex_on_path():
        path = shutil.which("codex")
        assert path
        return Path(path)

    resolved_dir = download_dir or Path(tempfile.mkdtemp())
    resolved_dir.mkdir(parents=True, exist_ok=True)

    url = _build_tarball_url(version)
    tar_path = resolved_dir / "codex.tar.gz"
    _download(url, tar_path)
    with tarfile.open(tar_path, "r:gz") as tf:
        tf.extractall(path=resolved_dir)

    # assume binary named "codex" somewhere in extracted tree
    codex_path = next(resolved_dir.rglob("codex"), None)
    if codex_path is None:
        raise RuntimeError("codex binary not found after extraction")
    codex_path.chmod(codex_path.stat().st_mode | 0o111)
    return codex_path.resolve()


def _build_tarball_url(version: str | None) -> str:
    ver = version or DEFAULT_CODEX_VERSION or "latest"
    system = sys.platform
    machine = platform.machine().lower()
    # Simplistic mapping; may need refinement for actual release names.
    if system.startswith("darwin"):
        platform_tag = "macos"
    elif system.startswith("linux"):
        platform_tag = "linux"
    else:
        raise RuntimeError(f"unsupported platform: {system}")
    if "arm" in machine or "aarch64" in machine:
        arch_tag = "arm64"
    else:
        arch_tag = "x86_64"

    if ver == "latest":
        return f"{CODEX_RELEASE_BASE}/codex-{platform_tag}-{arch_tag}.tar.gz"
    return f"https://github.com/openai/codex/releases/download/{ver}/codex-{platform_tag}-{arch_tag}.tar.gz"


def _download(url: str, dest: Path) -> None:
    with urllib.request.urlopen(url) as resp, dest.open("wb") as fh:
        fh.write(resp.read())
