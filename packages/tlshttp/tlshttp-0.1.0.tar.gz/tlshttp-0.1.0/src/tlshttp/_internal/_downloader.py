"""Binary downloader for tls-client shared library."""

from __future__ import annotations

import hashlib
import logging
import shutil
import tempfile
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

from platformdirs import user_cache_dir

from .._exceptions import LibraryNotFoundError
from ._platform import get_cached_platform

logger = logging.getLogger(__name__)

# GitHub release information
GITHUB_REPO = "bogdanfinn/tls-client"
LIBRARY_VERSION = "v1.12.0"
GITHUB_RELEASE_URL = f"https://github.com/{GITHUB_REPO}/releases/download/{LIBRARY_VERSION}"

# Known SHA256 hashes for verification (optional, can be populated later)
BINARY_HASHES: dict[str, str] = {
    # Add hashes here for verification if desired
    # "tls-client-linux-ubuntu-amd64-1.12.0.so": "sha256hash...",
}


def get_cache_dir() -> Path:
    """Get the cache directory for storing binaries."""
    cache = Path(user_cache_dir("tlshttp", ensure_exists=True))
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def get_library_path() -> Path:
    """Get path to the shared library, downloading if necessary.

    Returns:
        Path to the shared library file.

    Raises:
        LibraryNotFoundError: If the library cannot be found or downloaded.
    """
    cache_dir = get_cache_dir()
    platform_info = get_cached_platform()
    binary_name = platform_info.binary_name
    library_path = cache_dir / binary_name

    if library_path.exists():
        logger.debug(f"Using cached library: {library_path}")
        return library_path

    logger.info(f"Downloading tls-client library: {binary_name}")
    download_library(library_path, binary_name)
    return library_path


def download_library(target_path: Path, binary_name: str) -> None:
    """Download the shared library from GitHub releases.

    Args:
        target_path: Where to save the library.
        binary_name: Name of the binary to download.

    Raises:
        LibraryNotFoundError: If download fails.
    """
    url = f"{GITHUB_RELEASE_URL}/{binary_name}"
    logger.info(f"Downloading from: {url}")

    # Create temporary file in the same directory for atomic rename
    temp_fd, temp_path_str = tempfile.mkstemp(
        dir=target_path.parent,
        prefix=".tlshttp_download_",
    )
    temp_path = Path(temp_path_str)

    try:
        # Download with progress
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "tlshttp/0.1.0",
                "Accept": "application/octet-stream",
            },
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            content_length = response.headers.get("Content-Length")
            total_size = int(content_length) if content_length else None

            downloaded = 0
            chunk_size = 64 * 1024  # 64KB chunks

            with open(temp_fd, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size and logger.isEnabledFor(logging.DEBUG):
                        percent = (downloaded / total_size) * 100
                        logger.debug(f"Downloaded: {percent:.1f}%")

        # Verify hash if available
        if binary_name in BINARY_HASHES:
            expected_hash = BINARY_HASHES[binary_name]
            actual_hash = _compute_sha256(temp_path)
            if actual_hash != expected_hash:
                temp_path.unlink()
                raise LibraryNotFoundError(
                    f"Hash mismatch for {binary_name}: "
                    f"expected {expected_hash}, got {actual_hash}"
                )

        # Make executable on Unix
        import platform as plat

        if plat.system() != "Windows":
            temp_path.chmod(0o755)

        # Atomic rename
        shutil.move(str(temp_path), str(target_path))
        logger.info(f"Successfully downloaded library to: {target_path}")

    except HTTPError as e:
        temp_path.unlink(missing_ok=True)
        raise LibraryNotFoundError(
            f"Failed to download {binary_name}: HTTP {e.code} - {e.reason}"
        ) from e
    except URLError as e:
        temp_path.unlink(missing_ok=True)
        raise LibraryNotFoundError(
            f"Failed to download {binary_name}: {e.reason}"
        ) from e
    except OSError as e:
        temp_path.unlink(missing_ok=True)
        raise LibraryNotFoundError(
            f"Failed to save {binary_name}: {e}"
        ) from e


def _compute_sha256(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def clear_cache() -> None:
    """Clear the library cache directory."""
    cache_dir = get_cache_dir()
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        logger.info(f"Cleared cache directory: {cache_dir}")
