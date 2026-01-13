from __future__ import annotations

import asyncio
import hashlib
import os
import re
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx

from ._paths import tor_install_root


TOR_DOWNLOAD_PAGE = "https://www.torproject.org/download/tor/"
USER_AGENT = "tor-http/option-a (+https://pypi.org/project/tor-http/)"


@dataclass(frozen=True)
class DownloadedTor:
    tor_path: Path
    source_url: str
    extracted_dir: Path


class TorDownloadError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_extract_tar(tar: tarfile.TarFile, dest: Path) -> None:
    # basic path traversal guard
    dest = dest.resolve()
    for member in tar.getmembers():
        member_path = (dest / member.name).resolve()
        if not str(member_path).startswith(str(dest)):
            raise TorDownloadError("Blocked potentially unsafe tar path traversal.")
    tar.extractall(dest)


def _extract_archive(archive_path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    lower = archive_path.name.lower()
    if lower.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extractall(dest_dir)
    elif lower.endswith(".tar.gz") or lower.endswith(".tgz"):
        with tarfile.open(archive_path, "r:gz") as t:
            _safe_extract_tar(t, dest_dir)
    elif lower.endswith(".tar.xz") or lower.endswith(".txz"):
        with tarfile.open(archive_path, "r:xz") as t:
            _safe_extract_tar(t, dest_dir)
    else:
        raise TorDownloadError(f"Unsupported archive format: {archive_path.name}")
    return dest_dir


def _find_tor_executable(extracted_dir: Path) -> Optional[Path]:
    candidates = []
    for p in extracted_dir.rglob("*"):
        if not p.is_file():
            continue
        name = p.name.lower()
        if name == "tor" or name == "tor.exe":
            candidates.append(p)
    # Prefer paths that look like the standard bundle layout: */Tor/tor(.exe)
    def score(p: Path) -> tuple[int, int]:
        parts = [x.lower() for x in p.parts]
        return (0 if "tor" in parts else 1, len(parts))
    if not candidates:
        return None
    candidates.sort(key=score)
    return candidates[0]


def _platform_key() -> str:
    import platform as _platform

    sys = _platform.system().lower()
    if sys.startswith("win"):
        return "windows"
    if sys.startswith("linux"):
        return "linux"
    if sys.startswith("darwin") or sys.startswith("mac"):
        return "macos"
    return sys


def _arch_key() -> str:
    import platform as _platform

    machine = _platform.machine().lower()
    # normalize common values used by Tor Browser builds
    if machine in {"x86_64", "amd64"}:
        return "x86_64"
    if machine in {"aarch64", "arm64"}:
        return "aarch64"
    if machine in {"i386", "i686", "x86"}:
        return "i686"
    return machine


async def _fetch_text(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    return r.text


def _pick_expert_bundle_link(html: str, platform_key: str, arch_key: str) -> Optional[str]:
    # We look for links containing "tor-expert-bundle" (Tor Project's terminology).
    # The page may include multiple versions; prefer the first match for our platform.
    hrefs = re.findall(r'href="([^"]+)"', html, flags=re.IGNORECASE)

    # Normalize to absolute later via urljoin with TOR_DOWNLOAD_PAGE.
    matches = []
    for h in hrefs:
        if "tor-expert-bundle" not in h.lower():
            continue
        hl = h.lower()
        if platform_key == "windows":
            if "windows" in hl or "win" in hl:
                matches.append(h)
        elif platform_key == "macos":
            if "osx" in hl or "mac" in hl:
                matches.append(h)
        elif platform_key == "linux":
            if "linux" in hl:
                matches.append(h)
        else:
            matches.append(h)

    if not matches:
        return None

    # Try to match arch if present in filename.
    def arch_score(h: str) -> int:
        hl = h.lower()
        if arch_key in hl:
            return 0
        # some bundles may use "x86_64" or "amd64" etc
        if arch_key == "x86_64" and ("x64" in hl or "amd64" in hl):
            return 1
        if arch_key == "aarch64" and ("arm64" in hl):
            return 1
        return 2

    matches.sort(key=lambda h: (arch_score(h), len(h)))
    return matches[0]


async def download_tor_if_needed(
    *,
    force: bool = False,
    download_page: str = TOR_DOWNLOAD_PAGE,
    user_agent: str = USER_AGENT,
    expected_sha256: Optional[str] = None,
    override_url: Optional[str] = None,
) -> DownloadedTor:
    """Download and install Tor Expert Bundle into the user cache.

    - If `override_url` is provided (or env TORHTTP_TOR_URL), downloads that URL.
    - Otherwise, discovers a platform-appropriate Expert Bundle link from Tor's download page.

    Verification:
    - If `expected_sha256` is provided (or env TORHTTP_TOR_SHA256), we verify the downloaded
      archive matches it. If not provided, we still compute SHA256 and store it for logging.
    """
    tor_root = tor_install_root()
    tor_root.mkdir(parents=True, exist_ok=True)

    platform_key = _platform_key()
    arch_key = _arch_key()

    # check if already installed
    marker = tor_root / "installed.json"
    if marker.exists() and not force:
        # trust existing install
        # Try to locate the tor binary via recorded path; if missing, fall back to scan.
        try:
            import json
            data = json.loads(marker.read_text(encoding="utf-8"))
            tor_path = Path(data.get("tor_path", ""))
            extracted_dir = Path(data.get("extracted_dir", ""))
            source_url = str(data.get("source_url", ""))
            if tor_path and tor_path.exists():
                return DownloadedTor(tor_path=tor_path, source_url=source_url, extracted_dir=extracted_dir)
        except Exception:
            pass

        # scan cache
        found = _find_tor_executable(tor_root)
        if found is not None:
            return DownloadedTor(tor_path=found, source_url="cache", extracted_dir=found.parent)

    override_url = override_url or os.getenv("TORHTTP_TOR_URL")
    expected_sha256 = expected_sha256 or os.getenv("TORHTTP_TOR_SHA256")

    async with httpx.AsyncClient(timeout=60.0, headers={"User-Agent": user_agent}) as client:
        if override_url:
            bundle_url = override_url
        else:
            html = await _fetch_text(client, download_page)
            rel = _pick_expert_bundle_link(html, platform_key, arch_key)
            if not rel:
                raise TorDownloadError(
                    "Could not find a Tor Expert Bundle link on Tor's download page for "
                    f"platform={platform_key}, arch={arch_key}. "
                    "Set TORHTTP_TOR_URL to override."
                )
            bundle_url = urljoin(download_page, rel)

        # download to temp file
        parsed = urlparse(bundle_url)
        fname = Path(parsed.path).name or "tor-expert-bundle"
        tmp_dir = tor_root / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        archive_path = tmp_dir / fname

        r = await client.get(bundle_url, follow_redirects=True)
        r.raise_for_status()
        archive_path.write_bytes(r.content)

    digest = _sha256_file(archive_path)
    if expected_sha256 and digest.lower() != expected_sha256.lower():
        raise TorDownloadError(
            f"Tor archive SHA256 mismatch. expected={expected_sha256.lower()} got={digest.lower()}"
        )

    # clean install dir and extract
    extracted_dir = tor_root / "bundle"
    if extracted_dir.exists():
        shutil.rmtree(extracted_dir, ignore_errors=True)
    extracted_dir.mkdir(parents=True, exist_ok=True)

    _extract_archive(archive_path, extracted_dir)

    tor_path = _find_tor_executable(extracted_dir)
    if tor_path is None:
        raise TorDownloadError("Downloaded bundle extracted, but 'tor' executable was not found.")

    # record install metadata
    try:
        import json
        marker.write_text(
            json.dumps(
                {"tor_path": str(tor_path), "extracted_dir": str(extracted_dir), "source_url": bundle_url, "sha256": digest},
                indent=2,
            ),
            encoding="utf-8",
        )
    except Exception:
        pass

    return DownloadedTor(tor_path=tor_path, source_url=bundle_url, extracted_dir=extracted_dir)
