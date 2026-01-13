# tor-http (auto-download Tor on first run)

`tor-http` is a privacy-oriented async wrapper around **httpx** that routes requests through a **locally managed Tor process**.

This package follows a **download-on-first-run** strategy (no bundled Tor binaries in the wheel/sdist):

- ✅ No Tor binary redistribution in your PyPI artifact
- ✅ Works cross-platform (Windows / Linux / macOS)
- ✅ Uses the Tor Project “Tor Expert Bundle” as the source

> Notes
> - This library is intended for **privacy-oriented routing**. It does **not** guarantee a new Tor exit IP per request.
> - Tor can be rate-limited or blocked on some networks.
> - If your environment is air-gapped or blocks downloads, set an explicit `TORHTTP_TOR_CMD` (system Tor).

## Install

```bash
pip install tor-http
```

## Quick start

```python
from tor_http import tor_http

async def main():
    r = await tor_http.get("https://httpbin.org/ip")
    print(r.status_code, r.text)
```

## How Tor is obtained (Option A)

On first use, `tor-http` will:

1. Look for an explicit Tor binary (`TORHTTP_TOR_CMD` or `TorHttpOptions(tor_cmd=...)`)
2. Otherwise, check the local cache (previous download)
3. Otherwise, try `tor` from your system PATH
4. Otherwise, **download** the Tor Expert Bundle from the Tor Project and cache it

The downloaded bundle is cached in your user cache directory (via `platformdirs`), e.g.:

- Windows: `%LOCALAPPDATA%\tor-http\tor\...`
- macOS: `~/Library/Caches/tor-http/tor/...`
- Linux: `~/.cache/tor-http/tor/...`

## Environment variables

- `TORHTTP_TOR_CMD` — path to an existing Tor binary (skips download)
- `TORHTTP_TOR_URL` — override the download URL (advanced / mirrors / pinned versions)
- `TORHTTP_TOR_SHA256` — expected SHA256 for the archive at `TORHTTP_TOR_URL` (recommended if you override the URL)

## License

This project is MIT licensed (see `LICENSE`).

Tor is developed and distributed by The Tor Project. This project is not affiliated with or endorsed by The Tor Project.


### Permissions

This package does not require administrator or sudo privileges.
Tor is downloaded (if needed) and executed entirely in user space.


## Usage (module singleton)

```python
from tor_http import tor_http

r = await tor_http.get("https://httpbin.org/get")
print(r.status_code, r.json())
```

## Usage (class)

```python
from tor_http import TorHttp, TorHttpOptions

client = TorHttp(TorHttpOptions(use_tor=True))
r = await client.get("http://ip-api.com/json/")
print(r.status_code)
await client.close()
```

## Best-effort refresh

```python
ok = await tor_http.try_refresh()
```

This **restarts** Tor+client for reliability. It does **not** promise a new exit IP.
