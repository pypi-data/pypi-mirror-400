"""Session management with proper memory cleanup."""

from __future__ import annotations

import logging
import threading
import uuid
import weakref
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from .._client import Client

from ._library import get_library

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Tracks session state for memory management."""

    session_id: str
    is_destroyed: bool = False
    pending_responses: set[str] = field(default_factory=set)
    lock: threading.Lock = field(default_factory=threading.Lock)


class SessionManager:
    """Thread-safe session management with guaranteed cleanup.

    This class fixes the memory leak issues in existing wrappers by:
    1. Using context managers for response memory cleanup
    2. Using weak reference finalizers for session cleanup
    3. Thread-safe operations for concurrent access
    """

    _lock = threading.Lock()
    _sessions: dict[str, SessionState] = {}
    _finalizers: dict[str, weakref.finalize] = {}

    @classmethod
    def create_session(cls) -> str:
        """Create a new session.

        Returns:
            New unique session ID.
        """
        session_id = str(uuid.uuid4())

        with cls._lock:
            cls._sessions[session_id] = SessionState(session_id=session_id)

        logger.debug(f"Created session: {session_id}")
        return session_id

    @classmethod
    def register_client(cls, client: Client, session_id: str) -> None:
        """Register a finalizer to destroy session when client is garbage collected.

        Args:
            client: The Client instance.
            session_id: Session ID to cleanup.
        """

        def cleanup() -> None:
            logger.debug(f"Finalizer triggered for session: {session_id}")
            cls.destroy_session(session_id)

        with cls._lock:
            # Remove any existing finalizer
            old_finalizer = cls._finalizers.pop(session_id, None)
            if old_finalizer:
                old_finalizer.detach()

            # Register new finalizer
            cls._finalizers[session_id] = weakref.finalize(client, cleanup)

    @classmethod
    def destroy_session(cls, session_id: str) -> None:
        """Destroy a session and free all pending responses.

        Args:
            session_id: Session ID to destroy.
        """
        with cls._lock:
            state = cls._sessions.get(session_id)
            if state is None:
                return

            if state.is_destroyed:
                return

            state.is_destroyed = True

        # Free pending response memory outside the lock
        with state.lock:
            pending = list(state.pending_responses)
            state.pending_responses.clear()

        library = get_library()

        for response_id in pending:
            try:
                library.free_memory(response_id)
            except Exception as e:
                logger.warning(f"Failed to free response {response_id}: {e}")

        # Destroy the Go session
        try:
            library.destroy_session(session_id)
        except Exception as e:
            logger.warning(f"Failed to destroy session {session_id}: {e}")

        # Cleanup tracking
        with cls._lock:
            cls._sessions.pop(session_id, None)
            finalizer = cls._finalizers.pop(session_id, None)
            if finalizer:
                finalizer.detach()

        logger.debug(f"Destroyed session: {session_id}")

    @classmethod
    @contextmanager
    def response_memory(
        cls, session_id: str, response_id: str
    ) -> Generator[None, None, None]:
        """Context manager ensuring response memory is freed.

        This is the key fix for memory leaks - the freeMemory call
        happens in a finally block, guaranteed to run even on exceptions.

        Args:
            session_id: Session ID.
            response_id: Response ID to free after context exits.

        Yields:
            None
        """
        # Track this response
        with cls._lock:
            state = cls._sessions.get(session_id)
            if state:
                with state.lock:
                    state.pending_responses.add(response_id)

        try:
            yield
        finally:
            # Remove from tracking
            with cls._lock:
                state = cls._sessions.get(session_id)
                if state:
                    with state.lock:
                        state.pending_responses.discard(response_id)

            # Always free memory, even if session was destroyed
            try:
                library = get_library()
                library.free_memory(response_id)
            except Exception as e:
                logger.warning(f"Failed to free response {response_id}: {e}")

    @classmethod
    def get_session_count(cls) -> int:
        """Get the number of active sessions.

        Returns:
            Number of active sessions.
        """
        with cls._lock:
            return len(cls._sessions)

    @classmethod
    def destroy_all(cls) -> None:
        """Destroy all sessions."""
        with cls._lock:
            session_ids = list(cls._sessions.keys())

        for session_id in session_ids:
            cls.destroy_session(session_id)

        logger.debug("Destroyed all sessions")
