from __future__ import annotations

from typing import Any, Optional

from ._runtime import RUNTIME, TorHttpOptions


class TorHttp:
    """A small async facade over a shared Tor + httpx runtime."""

    def __init__(self, options: Optional[TorHttpOptions] = None) -> None:
        self._options = options
        self._acquired = False

    async def configure(self, options: TorHttpOptions) -> None:
        await RUNTIME.configure(options)

    async def _ensure_started(self) -> None:
        if self._options is not None:
            await RUNTIME.configure(self._options)
            self._options = None
        if not self._acquired:
            await RUNTIME.acquire()
            self._acquired = True

    async def request(self, method: str, url: str, **kwargs: Any):
        await self._ensure_started()
        return await RUNTIME.request(method, url, **kwargs)

    async def get(self, url: str, **kwargs: Any):
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any):
        return await self.request("POST", url, **kwargs)

    async def close(self) -> None:
        if self._acquired:
            await RUNTIME.release()
            self._acquired = False

    async def __aenter__(self) -> "TorHttp":
        await self._ensure_started()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


# Keep the shared runtime alive for the module-level singleton.
RUNTIME.pin()

tor_http = TorHttp()
