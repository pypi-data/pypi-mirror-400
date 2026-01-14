"""
Git utilities for finding modified files in the repository.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

import git
from git import Repo

from zenable_mcp.checkpoint.models import DirtyFileSnapshot, HookCheckpoint
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona

log = logging.getLogger(__name__)


def get_most_recently_edited_git_file(
    base_path: Path | None = None,
    repo: Repo | None = None,
) -> str | None:
    """
    Find the most recently edited file that is also modified in the git working tree.

    This function finds files that are:
    1. Modified in the git working tree (either unstaged or staged, but not committed)
    2. Most recently modified based on filesystem timestamp
    3. Not ignored by .gitignore

    Args:
        base_path: The base directory to search from (defaults to current directory)
        repo: Optional Repo object to reuse (for performance)

    Returns:
        Path to the most recently edited modified file, or None if no modified files
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    try:
        # Find the git repository (reuse if provided)
        if repo is None:
            repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        echo(f"Git repository root: {git_root}", persona=Persona.POWER_USER)

        # Get list of modified files (both staged and unstaged)
        modified_files = _get_dirty_file_paths(repo, git_root)

        echo(
            f"Total modified files found: {len(modified_files)}",
            persona=Persona.POWER_USER,
        )

        if not modified_files:
            msg = "No modified files found in git repository"
            echo(msg, persona=Persona.POWER_USER)
            return None

        # Find the most recently modified file based on filesystem timestamp
        echo(
            f"Checking modification times for {len(modified_files)} files...",
            persona=Persona.POWER_USER,
        )
        for f in modified_files:
            mtime = f.stat().st_mtime
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            echo(
                f"  {f.relative_to(git_root) if f.is_relative_to(git_root) else f}: {mtime_str}",
                persona=Persona.DEVELOPER,
            )

        most_recent_file = max(modified_files, key=lambda f: f.stat().st_mtime)

        msg = f"Selected most recently edited file: {most_recent_file}"
        echo(msg, persona=Persona.POWER_USER)
        return str(most_recent_file)

    except git.InvalidGitRepositoryError:
        echo(f"Not in a git repository: {base_path}", persona=Persona.DEVELOPER)
        return None
    except (OSError, IOError, AttributeError, TypeError, ValueError) as e:
        echo(f"Error finding most recently edited file: {e}", persona=Persona.DEVELOPER)
        return None


def _get_dirty_file_paths(repo: Repo, git_root: Path) -> list[Path]:
    """Get all dirty file paths from a repo.

    Internal helper that collects unstaged, staged, and untracked files.
    Delegates to git for all detection (respects .gitignore).

    Args:
        repo: Git repository object
        git_root: Path to git root directory

    Returns:
        List of Path objects for dirty files
    """
    modified_files: list[Path] = []
    seen_paths: set[str] = set()

    # Get unstaged changes (git diff)
    for item in repo.index.diff(None):  # diff against working tree
        file_path = git_root / item.a_path
        if file_path.exists() and file_path.is_file():
            path_str = str(file_path)
            if path_str not in seen_paths:
                modified_files.append(file_path)
                seen_paths.add(path_str)

    # Get staged changes (only if there are commits in the repo)
    if repo.head.is_valid():
        for item in repo.index.diff("HEAD"):  # diff against HEAD
            file_path = git_root / item.a_path
            if file_path.exists() and file_path.is_file():
                path_str = str(file_path)
                if path_str not in seen_paths:
                    modified_files.append(file_path)
                    seen_paths.add(path_str)
    else:
        # For repos with no commits, all staged files are new
        for (path, stage), entry in repo.index.entries.items():
            if stage == 0:  # Normal stage entry
                file_path = git_root / path
                if file_path.exists() and file_path.is_file():
                    path_str = str(file_path)
                    if path_str not in seen_paths:
                        modified_files.append(file_path)
                        seen_paths.add(path_str)

    # Get untracked files (repo.untracked_files already respects .gitignore)
    for file_path_str in repo.untracked_files:
        file_path = git_root / file_path_str
        if file_path.exists() and file_path.is_file():
            path_str = str(file_path)
            if path_str not in seen_paths:
                modified_files.append(file_path)
                seen_paths.add(path_str)

    return modified_files


def get_git_modified_files(
    base_path: Path | None = None,
    repo: Repo | None = None,
) -> list[str]:
    """
    Get all files modified in the git working tree.

    This function finds files that are:
    1. Modified in the git working tree (either unstaged or staged, but not committed)
    2. Not ignored by .gitignore

    Args:
        base_path: The base directory to search from (defaults to current directory)
        repo: Optional Repo object to reuse (for performance)

    Returns:
        List of paths to modified files (as strings)
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    try:
        # Find the git repository (reuse if provided)
        if repo is None:
            repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        modified_files = _get_dirty_file_paths(repo, git_root)
        return [str(f) for f in modified_files]

    except git.InvalidGitRepositoryError:
        return []
    except (OSError, IOError, AttributeError, TypeError, ValueError):
        return []


def get_branch_changed_files(
    base_path: Path | None = None,
    base_branch: str = "main",
    repo: Repo | None = None,
) -> list[Path]:
    """
    Get all files changed on the current branch compared to a base branch.

    This function finds files that are:
    1. Changed between the base branch and the current branch (committed changes)
    2. Modified in the working tree (staged and unstaged changes)
    3. Untracked files (not ignored by .gitignore)

    Args:
        base_path: The base directory to search from (defaults to current directory)
        base_branch: The base branch to compare against (default "main")
        repo: Optional Repo object to reuse (for performance)

    Returns:
        List of Path objects for changed files
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    try:
        # Find the git repository (reuse if provided)
        if repo is None:
            repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        echo(f"Git repository root: {git_root}", persona=Persona.DEVELOPER)
        echo(
            f"Comparing current branch against base branch: {base_branch}",
            persona=Persona.POWER_USER,
        )

        changed_files: set[Path] = set()

        # Get the merge base between current branch and base branch
        try:
            # Get current branch name
            current_branch = repo.active_branch.name
            echo(f"Current branch: {current_branch}", persona=Persona.DEVELOPER)

            # Find merge base
            merge_base = repo.merge_base(base_branch, current_branch)
            if merge_base:
                merge_base_commit = merge_base[0]
                echo(
                    f"Found merge base: {merge_base_commit.hexsha[:8]}",
                    persona=Persona.DEVELOPER,
                )

                # Get all files changed between merge base and current HEAD
                diff = merge_base_commit.diff(repo.head.commit)
                for item in diff:
                    # GitPython diff change types:
                    # 'A' = Added, 'D' = Deleted, 'M' = Modified, 'R' = Renamed

                    if item.change_type == "D":
                        # Deleted file - add it even though it doesn't exist
                        file_path = git_root / item.a_path
                        changed_files.add(file_path)
                    elif item.change_type in ["A", "M"]:
                        # Added or modified file
                        file_path = git_root / item.b_path
                        if file_path.exists() and file_path.is_file():
                            changed_files.add(file_path)
                    elif item.change_type.startswith("R"):
                        # Renamed file (e.g., 'R100' for 100% similarity)
                        # Add the new path if it exists
                        if item.b_path:
                            new_path = git_root / item.b_path
                            if new_path.exists() and new_path.is_file():
                                changed_files.add(new_path)
                        # For renamed files, we might also want the old path if different
                        if item.a_path and item.a_path != item.b_path:
                            old_path = git_root / item.a_path
                            # Old path usually won't exist for renames, but add if it does
                            if old_path.exists() and old_path.is_file():
                                changed_files.add(old_path)
                    else:
                        # Handle any other change types generically
                        if item.b_path:
                            file_path = git_root / item.b_path
                            if file_path.exists() and file_path.is_file():
                                changed_files.add(file_path)
                        elif item.a_path:
                            file_path = git_root / item.a_path
                            if file_path.exists() and file_path.is_file():
                                changed_files.add(file_path)

                echo(
                    f"Found {len(changed_files)} file(s) changed in commits on current branch",
                    persona=Persona.POWER_USER,
                )
            else:
                echo(
                    f"Warning: Could not find merge base with {base_branch}",
                    persona=Persona.POWER_USER,
                    err=True,
                )
        except (git.GitCommandError, TypeError) as e:
            echo(
                f"Warning: Could not compare with {base_branch}: {e}",
                persona=Persona.POWER_USER,
                err=True,
            )

        # Also include uncommitted changes (staged, unstaged, and untracked)
        # Reuse the same repo object
        working_tree_changes = _get_dirty_file_paths(repo, git_root)
        initial_count = len(changed_files)
        changed_files.update(working_tree_changes)
        added_count = len(changed_files) - initial_count

        if added_count > 0:
            echo(
                f"Found {added_count} additional file(s) with uncommitted changes",
                persona=Persona.POWER_USER,
            )

        # Convert set to sorted list for consistent ordering
        result = sorted(list(changed_files))
        echo(
            f"Total files changed on branch: {len(result)}",
            persona=Persona.POWER_USER,
        )

        return result

    except git.InvalidGitRepositoryError:
        echo(
            f"Not in a git repository: {base_path}",
            err=True,
            persona=Persona.POWER_USER,
        )
        return []
    except (
        OSError,
        IOError,
        AttributeError,
        TypeError,
        ValueError,
        git.GitCommandError,
    ) as e:
        echo(
            f"Error finding branch changed files: {e}",
            persona=Persona.POWER_USER,
            err=True,
        )
        return []


def capture_checkpoint_state(
    base_path: Path | None = None,
    session_id: str = "",
    repo: Repo | None = None,
) -> HookCheckpoint:
    """Capture current git state for checkpoint.

    Captures:
    - HEAD commit hash
    - List of dirty files (modified, staged, untracked) with stat info (size/mtime)

    Uses stat-based detection for performance - no content hashing.
    This is used at UserPromptSubmit/beforeSubmitPrompt to record state
    before the agent starts working.

    Args:
        base_path: The base directory to search from (defaults to current directory)
        session_id: Session identifier (session_id for Claude Code, conversation_id for Cursor)
        repo: Optional Repo object to reuse (for performance)

    Returns:
        HookCheckpoint with current git state
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    head_commit = ""
    dirty_files: list[DirtyFileSnapshot] = []
    workspace_root = str(base_path)

    try:
        # Find the git repository (reuse if provided)
        if repo is None:
            repo = Repo(base_path, search_parent_directories=True)
        # Keep workspace_root as provided by caller (e.g., CLAUDE_PROJECT_DIR)
        # Use git_root only for finding dirty files
        git_root = Path(repo.working_tree_dir)

        # Get HEAD commit hash
        if repo.head.is_valid():
            head_commit = repo.head.commit.hexsha
            echo(
                f"Checkpoint HEAD: {head_commit[:8]}...",
                persona=Persona.DEVELOPER,
            )

        # Get all dirty files and their stat info (size/mtime)
        dirty_file_paths = _get_dirty_file_paths(repo, git_root)
        for file_path in dirty_file_paths:
            try:
                stat = file_path.stat()
                dirty_files.append(
                    DirtyFileSnapshot(
                        path=str(file_path),
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                    )
                )
            except (OSError, IOError) as e:
                echo(
                    f"Could not stat file {file_path}: {e}",
                    persona=Persona.DEVELOPER,
                    err=True,
                )

        echo(
            f"Checkpoint captured: {len(dirty_files)} dirty file(s)",
            persona=Persona.DEVELOPER,
        )

    except git.InvalidGitRepositoryError:
        echo(
            f"Not in a git repository: {base_path}",
            persona=Persona.DEVELOPER,
            err=True,
        )
    except (OSError, IOError, AttributeError, TypeError, ValueError) as e:
        echo(
            f"Error capturing checkpoint: {e}",
            persona=Persona.DEVELOPER,
            err=True,
        )

    return HookCheckpoint(
        workspace_root=workspace_root,
        session_id=session_id,
        head_commit=head_commit,
        dirty_files=dirty_files,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def get_files_modified_since_checkpoint(
    checkpoint: HookCheckpoint,
    base_path: Path | None = None,
    repo: Repo | None = None,
) -> list[Path]:
    """Get files that have been modified since the checkpoint was taken.

    Compares current git state against the checkpoint to find:
    - New dirty files (not in checkpoint) - always included
    - Files in checkpoint with changed stat (size or mtime) - included
    - Files changed in commits since checkpoint HEAD - included

    Uses stat-based detection for performance - compares size/mtime instead of hashing.
    This is used at Stop/stop hook to find all files the agent modified.

    Args:
        checkpoint: The checkpoint to compare against
        base_path: The base directory (defaults to checkpoint.workspace_root)
        repo: Optional Repo object to reuse (for performance)

    Returns:
        List of Path objects for modified files
    """
    if base_path is None:
        base_path = Path(checkpoint.workspace_root)
    else:
        base_path = Path(base_path).resolve()

    modified_files: set[Path] = set()

    try:
        # Find the git repository (reuse if provided)
        if repo is None:
            repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        # Build lookup of checkpoint file stats (use string keys for consistent comparison)
        checkpoint_stats = {
            str(df.path): (df.size, df.mtime) for df in checkpoint.dirty_files
        }

        # 1. Check for commits since checkpoint HEAD
        if checkpoint.head_commit and repo.head.is_valid():
            current_head = repo.head.commit.hexsha
            if current_head != checkpoint.head_commit:
                echo(
                    f"HEAD moved: {checkpoint.head_commit[:8]} -> {current_head[:8]}",
                    persona=Persona.DEVELOPER,
                )
                try:
                    # Get files changed between checkpoint HEAD and current HEAD
                    checkpoint_commit = repo.commit(checkpoint.head_commit)
                    diff = checkpoint_commit.diff(repo.head.commit)
                    for item in diff:
                        if item.change_type == "D":
                            # Deleted files - skip (they don't exist to check)
                            continue
                        elif item.change_type in ["A", "M"]:
                            file_path = git_root / item.b_path
                            if file_path.exists() and file_path.is_file():
                                modified_files.add(file_path)
                        elif item.change_type.startswith("R"):
                            if item.b_path:
                                new_path = git_root / item.b_path
                                if new_path.exists() and new_path.is_file():
                                    modified_files.add(new_path)
                        else:
                            if item.b_path:
                                file_path = git_root / item.b_path
                                if file_path.exists() and file_path.is_file():
                                    modified_files.add(file_path)

                    echo(
                        f"Found {len(modified_files)} file(s) in new commits",
                        persona=Persona.DEVELOPER,
                    )
                except (git.GitCommandError, git.BadName) as e:
                    echo(
                        f"Could not compare commits: {e}",
                        persona=Persona.DEVELOPER,
                        err=True,
                    )

        # 2. Check current dirty files against checkpoint stats
        current_dirty = _get_dirty_file_paths(repo, git_root)
        for file_path in current_dirty:
            if not file_path.exists() or not file_path.is_file():
                continue

            file_path_str = str(file_path)

            if file_path_str not in checkpoint_stats:
                # New dirty file not in checkpoint - always include
                modified_files.add(file_path)
                echo(
                    f"New dirty file since checkpoint: {file_path.name}",
                    persona=Persona.DEVELOPER,
                )
            else:
                # File was dirty at checkpoint - compare stat to see if it changed
                try:
                    current_stat = file_path.stat()
                    checkpoint_size, checkpoint_mtime = checkpoint_stats[file_path_str]

                    # Include if size OR mtime changed
                    if (
                        current_stat.st_size != checkpoint_size
                        or current_stat.st_mtime != checkpoint_mtime
                    ):
                        modified_files.add(file_path)
                        echo(
                            f"Modified since checkpoint: {file_path.name}",
                            persona=Persona.DEVELOPER,
                        )
                except (OSError, IOError):
                    # If we can't stat it, assume it changed
                    modified_files.add(file_path)

        # 3. Check if any checkpoint files were deleted
        for checkpoint_path in checkpoint_stats:
            path = Path(checkpoint_path)
            if not path.exists():
                # File was deleted - log but don't include (nothing to review)
                echo(
                    f"File deleted since checkpoint: {path.name}",
                    persona=Persona.DEVELOPER,
                )

        result = sorted(list(modified_files))
        echo(
            f"Total files modified since checkpoint: {len(result)}",
            persona=Persona.DEVELOPER,
        )
        return result

    except git.InvalidGitRepositoryError:
        echo(
            f"Not in a git repository: {base_path}",
            persona=Persona.DEVELOPER,
            err=True,
        )
        return []
    except (OSError, IOError, AttributeError, TypeError, ValueError) as e:
        echo(
            f"Error comparing to checkpoint: {e}",
            persona=Persona.DEVELOPER,
            err=True,
        )
        return []
