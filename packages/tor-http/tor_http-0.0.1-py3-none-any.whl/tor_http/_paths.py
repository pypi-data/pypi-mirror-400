from __future__ import annotations

from pathlib import Path
from platformdirs import user_cache_dir


def cache_root(app_name: str = "tor-http") -> Path:
    """Return the per-user cache dir used to store downloaded Tor bundles."""
    return Path(user_cache_dir(app_name))


def tor_install_root() -> Path:
    return cache_root() / "tor"
