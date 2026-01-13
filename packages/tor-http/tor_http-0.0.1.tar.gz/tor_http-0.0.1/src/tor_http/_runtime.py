from __future__ import annotations

import atexit
import asyncio
from dataclasses import dataclass
from typing import Optional

import httpx

from ._tor import TorHandle, start_tor, stop_tor


@dataclass
class TorHttpOptions:
    """Runtime options.

    - tor_cmd: explicit tor executable path (skips auto-download)
    - socks_host/socks_port: where the Tor SOCKS proxy will listen
    - request_timeout_s: httpx request timeout
    """

    tor_cmd: Optional[str] = None
    socks_host: str = "127.0.0.1"
    socks_port: Optional[int] = None
    request_timeout_s: float = 30.0


class _SingletonRuntime:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._options = TorHttpOptions()
        self._tor: Optional[TorHandle] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._refcount = 0
        self._pincount = 0

    async def configure(self, options: TorHttpOptions) -> None:
        async with self._lock:
            self._options = options

    async def acquire(self) -> None:
        async with self._lock:
            self._refcount += 1
            if self._tor is not None and self._client is not None:
                return

            opts = self._options

        tor = await start_tor(
            tor_cmd=opts.tor_cmd,
            socks_host=opts.socks_host,
            socks_port=opts.socks_port,
        )

        proxy = f"socks5h://{tor.socks_host}:{tor.socks_port}"
        client = httpx.AsyncClient(
            proxies=proxy,
            timeout=httpx.Timeout(opts.request_timeout_s),
            follow_redirects=True,
        )

        async with self._lock:
            # another coroutine might have started it; in that case, close ours
            if self._tor is not None or self._client is not None:
                await client.aclose()
                await stop_tor(tor)
                return
            self._tor = tor
            self._client = client

    async def release(self) -> None:
        async with self._lock:
            if self._refcount > 0:
                self._refcount -= 1
            should_stop = (self._refcount == 0 and self._pincount == 0)
        if should_stop:
            await self._stop_all()

    def pin(self) -> None:
        # keep runtime alive for module-level singleton
        self._pincount += 1

    def unpin(self) -> None:
        if self._pincount > 0:
            self._pincount -= 1

    async def request(self, method: str, url: str, **kwargs):
        await self.acquire()
        async with self._lock:
            client = self._client
        if client is None:
            raise RuntimeError("Tor runtime not started.")
        return await client.request(method, url, **kwargs)

    async def _stop_all(self) -> None:
        async with self._lock:
            tor = self._tor
            client = self._client
            self._tor = None
            self._client = None

        if client is not None:
            await client.aclose()
        if tor is not None:
            await stop_tor(tor)

    async def force_close(self) -> None:
        async with self._lock:
            self._refcount = 0
            self._pincount = 0
        await self._stop_all()


RUNTIME = _SingletonRuntime()


def _atexit_close() -> None:
    try:
        loop = asyncio.get_event_loop()
    except Exception:
        return
    if loop.is_closed():
        return
    try:
        loop.create_task(RUNTIME.force_close())
    except Exception:
        pass


atexit.register(_atexit_close)
