from __future__ import annotations

import os
import platform
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ._download import download_tor_if_needed, TorDownloadError


@dataclass(frozen=True)
class TorBinary:
    path: Path
    source: str  # "downloaded" | "system" | "explicit"


def ensure_executable(p: Path) -> None:
    if platform.system().lower().startswith("win"):
        return
    try:
        mode = p.stat().st_mode
        p.chmod(mode | 0o111)
    except Exception:
        pass


async def find_tor_binary(tor_cmd: Optional[str] = None) -> TorBinary:
    """Resolve tor binary path.

    Priority:
    1) explicit `tor_cmd` (or env TORHTTP_TOR_CMD)
    2) cached downloaded bundle (Option A)
    3) system PATH
    4) download (Option A) if still missing
    """
    tor_cmd = tor_cmd or os.getenv("TORHTTP_TOR_CMD")
    if tor_cmd:
        p = Path(tor_cmd).expanduser()
        if not p.exists():
            raise FileNotFoundError(f"tor_cmd does not exist: {p}")
        ensure_executable(p)
        return TorBinary(path=p, source="explicit")

    # try cache marker / scan first
    try:
        d = await download_tor_if_needed(force=False)
        ensure_executable(d.tor_path)
        return TorBinary(path=d.tor_path, source="downloaded")
    except TorDownloadError:
        # fall back to system tor below
        pass
    except Exception:
        pass

    sys_path = shutil.which("tor")
    if sys_path:
        p = Path(sys_path)
        ensure_executable(p)
        return TorBinary(path=p, source="system")

    # final attempt: download
    d = await download_tor_if_needed(force=True)
    ensure_executable(d.tor_path)
    return TorBinary(path=d.tor_path, source="downloaded")
