"""Session management for temporary file storage."""

import shutil
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Session:
    """A user session with uploaded files and state."""

    id: str
    created_at: float
    directory: Path
    files: dict[str, dict[str, Any]] = field(default_factory=dict)
    cropped_images: list[Path] = field(default_factory=list)
    exif_data: dict[str, dict[str, Any]] = field(default_factory=dict)  # filename -> exif

    @property
    def age_seconds(self) -> float:
        """Return session age in seconds."""
        return time.time() - self.created_at


class SessionManager:
    """Manages temporary sessions for file uploads and processing."""

    def __init__(
        self,
        base_dir: Path | None = None,
        max_age_seconds: float = 3600,  # 1 hour
        cleanup_interval: float = 300,  # 5 minutes
    ):
        """
        Initialize session manager.

        Args:
            base_dir: Base directory for session storage. Uses temp dir if None.
            max_age_seconds: Maximum session age before cleanup.
            cleanup_interval: How often to run cleanup (seconds).
        """
        if base_dir is None:
            import tempfile

            base_dir = Path(tempfile.gettempdir()) / "scansplitter_sessions"

        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.max_age_seconds = max_age_seconds
        self.cleanup_interval = cleanup_interval
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def create_session(self) -> Session:
        """Create a new session with unique ID."""
        session_id = uuid.uuid4().hex[:12]
        session_dir = self.base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        session = Session(
            id=session_id,
            created_at=time.time(),
            directory=session_dir,
        )

        with self._lock:
            self._sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID."""
        with self._lock:
            return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its files."""
        with self._lock:
            session = self._sessions.pop(session_id, None)

        if session is None:
            return False

        # Remove directory
        if session.directory.exists():
            shutil.rmtree(session.directory, ignore_errors=True)

        return True

    def cleanup_old_sessions(self) -> int:
        """Remove sessions older than max_age_seconds."""
        now = time.time()
        to_delete = []

        with self._lock:
            for session_id, session in self._sessions.items():
                if now - session.created_at > self.max_age_seconds:
                    to_delete.append(session_id)

        deleted = 0
        for session_id in to_delete:
            if self.delete_session(session_id):
                deleted += 1

        return deleted

    def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            time.sleep(self.cleanup_interval)
            try:
                self.cleanup_old_sessions()
            except Exception:
                pass  # Ignore errors in cleanup


# Global session manager instance
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
