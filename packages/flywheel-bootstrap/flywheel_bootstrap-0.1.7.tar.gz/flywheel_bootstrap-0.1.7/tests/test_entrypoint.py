from __future__ import annotations

import importlib.metadata


def test_console_entrypoint_exists() -> None:
    """Package must expose a 'bootstrap' console script (used by bootstrap.sh)."""

    scripts = importlib.metadata.entry_points().select(group="console_scripts")
    names = {ep.name: ep.value for ep in scripts}
    assert "bootstrap" in names, "console script 'bootstrap' missing"
    assert names["bootstrap"] == "bootstrap.__main__:main"
