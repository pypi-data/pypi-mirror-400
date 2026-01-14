"""ctypes library loader for tls-client."""

from __future__ import annotations

import ctypes
import json
import logging
import threading
from typing import Any

from .._exceptions import LibraryError, LibraryNotFoundError
from ._downloader import get_library_path

logger = logging.getLogger(__name__)


class TLSLibrary:
    """Wrapper around the tls-client shared library.

    This class handles loading the shared library and provides
    type-safe access to its functions.
    """

    def __init__(self, library_path: str) -> None:
        """Load the shared library.

        Args:
            library_path: Path to the shared library file.

        Raises:
            LibraryNotFoundError: If the library cannot be loaded.
        """
        try:
            self._lib = ctypes.cdll.LoadLibrary(library_path)
        except OSError as e:
            raise LibraryNotFoundError(
                f"Failed to load library from {library_path}: {e}"
            ) from e

        self._setup_functions()
        logger.debug(f"Loaded tls-client library from: {library_path}")

    def _setup_functions(self) -> None:
        """Set up function signatures for the library."""
        # request(requestPayload *C.char) *C.char
        self._lib.request.argtypes = [ctypes.c_char_p]
        self._lib.request.restype = ctypes.c_char_p

        # freeMemory(responseId *C.char)
        self._lib.freeMemory.argtypes = [ctypes.c_char_p]
        self._lib.freeMemory.restype = None

        # destroySession(sessionId *C.char) *C.char
        self._lib.destroySession.argtypes = [ctypes.c_char_p]
        self._lib.destroySession.restype = ctypes.c_char_p

        # destroyAll() *C.char
        self._lib.destroyAll.argtypes = []
        self._lib.destroyAll.restype = ctypes.c_char_p

        # getCookiesFromSession(sessionId *C.char) *C.char
        self._lib.getCookiesFromSession.argtypes = [ctypes.c_char_p]
        self._lib.getCookiesFromSession.restype = ctypes.c_char_p

        # addCookiesToSession(sessionId *C.char, cookiesJson *C.char) *C.char
        self._lib.addCookiesToSession.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._lib.addCookiesToSession.restype = ctypes.c_char_p

    def request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute an HTTP request.

        Args:
            payload: Request payload dictionary.

        Returns:
            Response dictionary from the library.

        Raises:
            LibraryError: If the request fails at the library level.
        """
        payload_json = json.dumps(payload).encode("utf-8")
        response_ptr = self._lib.request(payload_json)

        if response_ptr is None:
            raise LibraryError("Request returned null pointer")

        response_str = response_ptr.decode("utf-8")
        response_data = json.loads(response_str)

        return response_data

    def free_memory(self, response_id: str) -> None:
        """Free memory for a response.

        Args:
            response_id: ID of the response to free.
        """
        try:
            self._lib.freeMemory(response_id.encode("utf-8"))
        except Exception as e:
            logger.warning(f"Failed to free memory for {response_id}: {e}")

    def destroy_session(self, session_id: str) -> None:
        """Destroy a session.

        Args:
            session_id: ID of the session to destroy.
        """
        try:
            result_ptr = self._lib.destroySession(session_id.encode("utf-8"))
            if result_ptr:
                result = json.loads(result_ptr.decode("utf-8"))
                if not result.get("success", True):
                    logger.warning(
                        f"Failed to destroy session {session_id}: {result.get('error')}"
                    )
        except Exception as e:
            logger.warning(f"Failed to destroy session {session_id}: {e}")

    def destroy_all(self) -> None:
        """Destroy all sessions."""
        try:
            self._lib.destroyAll()
        except Exception as e:
            logger.warning(f"Failed to destroy all sessions: {e}")

    def get_cookies(self, session_id: str, url: str) -> list[dict[str, Any]]:
        """Get cookies for a session and URL.

        Args:
            session_id: Session ID.
            url: URL to get cookies for.

        Returns:
            List of cookie dictionaries.
        """
        payload = json.dumps({"sessionId": session_id, "url": url}).encode("utf-8")
        result_ptr = self._lib.getCookiesFromSession(payload)

        if result_ptr is None:
            return []

        result = json.loads(result_ptr.decode("utf-8"))
        return result.get("cookies", [])

    def add_cookies(
        self,
        session_id: str,
        url: str,
        cookies: list[dict[str, Any]],
    ) -> None:
        """Add cookies to a session.

        Args:
            session_id: Session ID.
            url: URL for the cookies.
            cookies: List of cookie dictionaries.
        """
        payload = json.dumps({
            "sessionId": session_id,
            "url": url,
            "cookies": cookies,
        }).encode("utf-8")

        self._lib.addCookiesToSession(
            session_id.encode("utf-8"),
            payload,
        )


# Thread-safe singleton
_library: TLSLibrary | None = None
_library_lock = threading.Lock()


def get_library() -> TLSLibrary:
    """Get the singleton TLSLibrary instance.

    This function is thread-safe and will download the library
    on first access if needed.

    Returns:
        The TLSLibrary instance.

    Raises:
        LibraryNotFoundError: If the library cannot be loaded.
    """
    global _library

    if _library is not None:
        return _library

    with _library_lock:
        # Double-check after acquiring lock
        if _library is not None:
            return _library

        library_path = get_library_path()
        _library = TLSLibrary(str(library_path))
        return _library


def reset_library() -> None:
    """Reset the library singleton (for testing)."""
    global _library
    with _library_lock:
        if _library is not None:
            _library.destroy_all()
            _library = None
