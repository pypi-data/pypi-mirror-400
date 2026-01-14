"""SQLite storage for hook checkpoints.

Pattern follows usage/manager.py for SQLite usage.
"""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from zenable_mcp.checkpoint.models import DirtyFileSnapshot, HookCheckpoint
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.utils.retries import retry_on_error

# Checkpoint cache directory
CHECKPOINT_CACHE_DIR = Path.home() / ".zenable" / "checkpoint-cache"


def _is_sqlite_locked(e: Exception) -> bool:
    """Check if exception is a SQLite database locked error."""
    return isinstance(e, sqlite3.OperationalError) and "locked" in str(e).lower()


class CheckpointStorage:
    """SQLite storage for hook checkpoints.

    Stores checkpoint state (HEAD commit, dirty files with stat info) keyed by
    (workspace_root, session_id) to track files modified during
    an agent session.
    """

    TTL_HOURS = 24  # Checkpoints older than this are cleaned up

    def __init__(self, db_path: Path | None = None):
        """Initialize checkpoint storage.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.zenable/checkpoint-cache/checkpoints.db
        """
        self.db_path = db_path or (CHECKPOINT_CACHE_DIR / "checkpoints.db")
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Ensure database and table exist.

        Uses exponential backoff retry on database lock conflicts.
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        @retry_on_error(
            max_retries=6,
            initial_delay=0.1,
            max_delay=3.2,
            backoff_factor=2.0,
            exceptions=(sqlite3.OperationalError,),
            retryable_conditions=_is_sqlite_locked,
        )
        def _do_init() -> None:
            with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA busy_timeout=5000")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS checkpoints (
                        workspace_root TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        head_commit TEXT NOT NULL,
                        dirty_files TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY (workspace_root, session_id)
                    )
                """)
                conn.commit()

        try:
            _do_init()
        except sqlite3.Error as e:
            echo(
                f"Failed to initialize checkpoint database: {e}",
                err=True,
                persona=Persona.DEVELOPER,
            )

    def save(self, checkpoint: HookCheckpoint) -> None:
        """Save a checkpoint, replacing any existing one for this session.

        Also performs opportunistic cleanup of stale checkpoints.
        Uses exponential backoff retry on database lock conflicts.
        """
        # Serialize dirty files to JSON - convert Path to str
        dirty_files_json = json.dumps(
            [
                {"path": str(df.path), "size": df.size, "mtime": df.mtime}
                for df in checkpoint.dirty_files
            ]
        )

        # Convert types for SQLite storage
        workspace_root_str = str(checkpoint.workspace_root)
        session_id_str = checkpoint.session_id or ""
        created_at_str = checkpoint.created_at.isoformat()

        @retry_on_error(
            max_retries=6,
            initial_delay=0.1,
            max_delay=3.2,
            backoff_factor=2.0,
            exceptions=(sqlite3.OperationalError,),
            retryable_conditions=_is_sqlite_locked,
        )
        def _do_save() -> None:
            with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
                conn.execute("PRAGMA busy_timeout=5000")

                # UPSERT: insert or replace existing
                conn.execute(
                    """
                    INSERT OR REPLACE INTO checkpoints
                    (workspace_root, session_id, head_commit, dirty_files, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        workspace_root_str,
                        session_id_str,
                        checkpoint.head_commit,
                        dirty_files_json,
                        created_at_str,
                    ),
                )
                conn.commit()

        try:
            _do_save()
            # Opportunistic cleanup of stale checkpoints
            self.cleanup_stale()

        except sqlite3.Error as e:
            echo(
                f"Failed to save checkpoint: {e}",
                err=True,
                persona=Persona.DEVELOPER,
            )

    def load(self, workspace_root: str, session_id: str) -> HookCheckpoint | None:
        """Load a checkpoint for the given workspace and session.

        Uses exponential backoff retry on database lock conflicts.

        Returns:
            HookCheckpoint if found, None otherwise
        """

        @retry_on_error(
            max_retries=6,
            initial_delay=0.1,
            max_delay=3.2,
            backoff_factor=2.0,
            exceptions=(sqlite3.OperationalError,),
            retryable_conditions=_is_sqlite_locked,
        )
        def _do_load() -> tuple[str, str, str] | None:
            with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
                conn.execute("PRAGMA busy_timeout=5000")

                cursor = conn.execute(
                    """
                    SELECT head_commit, dirty_files, created_at
                    FROM checkpoints
                    WHERE workspace_root = ? AND session_id = ?
                    """,
                    (workspace_root, session_id),
                )
                return cursor.fetchone()

        try:
            row = _do_load()

            if row is None:
                return None

            head_commit, dirty_files_json, created_at = row

            # Parse dirty files from JSON
            dirty_files_data = json.loads(dirty_files_json)
            dirty_files = [DirtyFileSnapshot(**df) for df in dirty_files_data]

            return HookCheckpoint(
                workspace_root=workspace_root,
                session_id=session_id,
                head_commit=head_commit,
                dirty_files=dirty_files,
                created_at=created_at,
            )

        except (sqlite3.Error, json.JSONDecodeError, TypeError, KeyError) as e:
            # TypeError/KeyError can occur if loading old checkpoint with different schema
            # Old checkpoints will auto-expire (24hr TTL), fall back to branch diff
            echo(
                f"Failed to load checkpoint: {e}",
                err=True,
                persona=Persona.DEVELOPER,
            )
            return None

    def delete(self, workspace_root: str, session_id: str) -> bool:
        """Delete a checkpoint after it's been used.

        Uses exponential backoff retry on database lock conflicts.

        Returns:
            True if a checkpoint was deleted, False otherwise
        """

        @retry_on_error(
            max_retries=6,
            initial_delay=0.1,
            max_delay=3.2,
            backoff_factor=2.0,
            exceptions=(sqlite3.OperationalError,),
            retryable_conditions=_is_sqlite_locked,
        )
        def _do_delete() -> int:
            with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
                conn.execute("PRAGMA busy_timeout=5000")

                cursor = conn.execute(
                    """
                    DELETE FROM checkpoints
                    WHERE workspace_root = ? AND session_id = ?
                    """,
                    (workspace_root, session_id),
                )
                conn.commit()
                return cursor.rowcount

        try:
            deleted = _do_delete() > 0
            if deleted:
                session_display = session_id[:8] if session_id else "no-session"
                echo(
                    f"Deleted checkpoint for session {session_display}...",
                    persona=Persona.DEVELOPER,
                )
            return deleted

        except sqlite3.Error as e:
            echo(
                f"Failed to delete checkpoint: {e}",
                err=True,
                persona=Persona.DEVELOPER,
            )
            return False

    def cleanup_stale(self) -> int:
        """Remove checkpoints older than TTL_HOURS.

        Called opportunistically on save to prevent unbounded growth.
        Uses exponential backoff retry on database lock conflicts.

        Returns:
            Number of checkpoints deleted
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.TTL_HOURS)
        cutoff_str = cutoff.isoformat()

        @retry_on_error(
            max_retries=6,
            initial_delay=0.1,
            max_delay=3.2,
            backoff_factor=2.0,
            exceptions=(sqlite3.OperationalError,),
            retryable_conditions=_is_sqlite_locked,
        )
        def _do_cleanup() -> int:
            with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
                conn.execute("PRAGMA busy_timeout=5000")

                cursor = conn.execute(
                    """
                    DELETE FROM checkpoints
                    WHERE created_at < ?
                    """,
                    (cutoff_str,),
                )
                conn.commit()
                return cursor.rowcount

        try:
            deleted = _do_cleanup()
            if deleted > 0:
                echo(
                    f"Cleaned up {deleted} stale checkpoint(s)",
                    persona=Persona.DEVELOPER,
                )
            return deleted

        except sqlite3.Error as e:
            echo(
                f"Failed to cleanup stale checkpoints: {e}",
                err=True,
                persona=Persona.DEVELOPER,
            )
            return 0
