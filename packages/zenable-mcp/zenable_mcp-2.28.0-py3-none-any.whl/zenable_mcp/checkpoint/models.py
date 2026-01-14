"""Models for checkpoint state management."""

import re
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Git commit hash pattern: 40 hex characters for full SHA-1
# Also allow short hashes (7+ chars) commonly used in git output
_GIT_COMMIT_HASH_PATTERN = re.compile(r"^[0-9a-fA-F]{7,40}$")


class DirtyFileSnapshot(BaseModel):
    """Snapshot of a dirty file's state at checkpoint time.

    Captures stat info (size/mtime) for ALL dirty files (both modified tracked
    and untracked) so we can detect changes during the agent session.

    At comparison time:
    - Files in checkpoint: compare stat to detect changes during session
    - Files NOT in checkpoint: include (newly modified/created)
    """

    model_config = ConfigDict(strict=False)

    path: Path
    size: int = Field(ge=0)  # File size in bytes
    mtime: float  # Modification time (Unix timestamp)

    @field_validator("path", mode="before")
    @classmethod
    def coerce_path(cls, v):
        """Coerce string to Path."""
        if isinstance(v, str):
            return Path(v)
        return v


class HookCheckpoint(BaseModel):
    """Checkpoint of git state at prompt submit time.

    Used to track what files existed before the agent started working,
    so we can identify what changed during the session at stop time.

    Stores stat info for ALL dirty files (modified tracked + untracked)
    to enable stat-based change detection.
    """

    model_config = ConfigDict(strict=False)

    workspace_root: Path
    session_id: str | None = (
        None  # session_id (Claude Code), conversation_id (Cursor), or None for IDEs that don't provide one
    )
    head_commit: str  # Git HEAD commit hash at checkpoint time
    dirty_files: list[DirtyFileSnapshot]  # All dirty files with stat info
    created_at: datetime  # Timestamp, coerced from ISO8601 string if needed

    @field_validator("session_id", mode="before")
    @classmethod
    def normalize_session_id(cls, v):
        """Normalize empty string to None for session_id."""
        if v == "":
            return None
        return v

    @field_validator("workspace_root", mode="before")
    @classmethod
    def coerce_workspace_root(cls, v):
        """Coerce string to Path."""
        if isinstance(v, str):
            return Path(v)
        return v

    @field_validator("head_commit", mode="after")
    @classmethod
    def validate_head_commit(cls, v: str) -> str:
        """Validate that head_commit is a valid git commit hash."""
        if not _GIT_COMMIT_HASH_PATTERN.match(v):
            raise ValueError(
                f"head_commit must be a valid git commit hash (7-40 hex chars), got: {v!r}"
            )
        return v

    @field_validator("created_at", mode="before")
    @classmethod
    def coerce_created_at(cls, v):
        """Coerce ISO8601 string to datetime.

        Handles:
        - datetime objects (pass through)
        - ISO8601 formatted strings (e.g., "2025-12-26T10:30:00Z", "2025-12-26T10:30:00+00:00")
        - Timestamps with microseconds
        """
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Try parsing with various ISO8601 formats
            # Replace 'Z' with '+00:00' for fromisoformat compatibility
            v = v.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(
                    f"created_at must be a valid ISO8601 timestamp, got: {v!r}"
                )
        raise ValueError(
            f"created_at must be a datetime or ISO8601 string, got: {type(v).__name__}"
        )
