from __future__ import annotations

import asyncio
import shutil
import socket
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import stem.process

from ._bundled import find_tor_binary


class TorNotFoundError(RuntimeError):
    pass


@dataclass(frozen=True)
class TorHandle:
    process: object
    socks_host: str
    socks_port: int
    data_dir: Path
    tor_cmd: Path
    source: str  # downloaded/system/explicit


def _get_free_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return int(s.getsockname()[1])


async def start_tor(
    *,
    tor_cmd: Optional[str] = None,
    socks_host: str = "127.0.0.1",
    socks_port: Optional[int] = None,
    timeout: int = 90,
) -> TorHandle:
    """Start a Tor process and wait until it boots."""
    binary = await find_tor_binary(tor_cmd)
    tor_path = binary.path

    if socks_port is None:
        socks_port = _get_free_port(socks_host)

    data_dir = Path(tempfile.mkdtemp(prefix="tor-http-"))

    config = {
        "SocksPort": f"{socks_host}:{socks_port}",
        "DataDirectory": str(data_dir),
        "AvoidDiskWrites": "1",
        "Log": "notice stdout",
    }

    try:
        proc = await asyncio.to_thread(
            stem.process.launch_tor_with_config,
            config=config,
            tor_cmd=str(tor_path),
            take_ownership=True,
            timeout=timeout,
        )
    except TypeError:
        # stem version differences
        proc = await asyncio.to_thread(
            stem.process.launch_tor_with_config,
            config=config,
            tor_cmd=str(tor_path),
            timeout=timeout,
        )

    return TorHandle(
        process=proc,
        socks_host=socks_host,
        socks_port=int(socks_port),
        data_dir=data_dir,
        tor_cmd=tor_path,
        source=binary.source,
    )


async def stop_tor(handle: TorHandle) -> None:
    """Best-effort stop and cleanup."""
    proc = handle.process
    try:
        if hasattr(proc, "terminate"):
            proc.terminate()
        if hasattr(proc, "wait"):
            await asyncio.to_thread(proc.wait, 5)
    except Exception:
        try:
            if hasattr(proc, "kill"):
                proc.kill()
        except Exception:
            pass

    try:
        shutil.rmtree(handle.data_dir, ignore_errors=True)
    except Exception:
        pass
