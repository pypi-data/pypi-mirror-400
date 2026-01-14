"""Claude Code hook input handler.

See: https://code.claude.com/docs/en/hooks
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

from zenable_mcp.checkpoint.storage import CheckpointStorage
from zenable_mcp.exceptions import HandlerEnvironmentError
from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.hook_input_handlers.base import (
    HookInputContext,
    HookInputFormat,
    InputHandler,
)
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.utils.git import (
    capture_checkpoint_state,
    get_branch_changed_files,
    get_files_modified_since_checkpoint,
)


class ClaudeCodeInputHandler(InputHandler):
    """Handler for Claude Code hook inputs.

    See: https://code.claude.com/docs/en/hooks

    Supports the following hook events:
    - UserPromptSubmit: Runs when user submits a prompt (checkpoint state)
    - Stop: Runs when agent loop ends (review all modified files)

    Claude Code sends hook data as JSON to stdin. Common fields:
    {
        "session_id": "abc123",
        "transcript_path": "/path/to/transcript.jsonl",
        "cwd": "/working/directory",
        "hook_event_name": "UserPromptSubmit" | "Stop",
        ...
    }

    UserPromptSubmit specific fields:
        "prompt": "user's prompt text"

    Stop specific fields:
        "stop_hook_active": true | false

    Response formats (stdout JSON):
    - UserPromptSubmit: {} to continue, stdout text is added as context
    - Stop: {"decision": "block", "reason": "..."} prevents stopping and
            provides feedback to the agent to address the issues
    """

    # Supported hook events for Claude Code
    SUPPORTED_EVENTS = {"UserPromptSubmit", "Stop"}

    def __init__(self, checkpoint_storage: CheckpointStorage | None = None):
        self._stdin_data: dict[str, Any] | None = None
        self._stdin_read: bool = False
        self._shared_stdin_provided: bool = False
        self._checkpoint_storage = checkpoint_storage or CheckpointStorage()
        self._modified_files: list[Path] = []

    def set_shared_stdin_data(self, data: dict[str, Any] | None) -> None:
        """Set shared stdin data from the registry."""
        self._stdin_data = data
        self._stdin_read = True
        self._shared_stdin_provided = True

    @property
    def name(self) -> str:
        return "ClaudeCode"

    @property
    def format(self) -> HookInputFormat:
        return HookInputFormat.CLAUDE_CODE_HOOK

    def can_handle(self) -> bool:
        """Check if we're running as a Claude Code hook.

        Checks for:
        1. CLAUDE_HOOK_EVENT_NAME environment variable (set by Claude Code)
        2. Non-TTY stdin with JSON data containing hook_event_name
        """
        # Check environment variable hint (set by Claude Code for all hooks)
        env_hook_event = os.environ.get("CLAUDE_HOOK_EVENT_NAME", "")
        if env_hook_event:
            if env_hook_event in self.SUPPORTED_EVENTS:
                echo(
                    f"Found CLAUDE_HOOK_EVENT_NAME={env_hook_event}",
                    persona=Persona.DEVELOPER,
                )
                return True
            # Unknown event, don't claim it
            return False

        # Check stdin for Claude Code JSON
        stdin_data = self._read_stdin()
        if not stdin_data:
            return False

        # Check for hook_event_name field
        hook_event = stdin_data.get("hook_event_name", "")
        if hook_event in self.SUPPORTED_EVENTS:
            echo(
                f"Detected Claude Code {hook_event} hook in stdin",
                persona=Persona.DEVELOPER,
            )
            return True

        return False

    def parse_input(self) -> HookInputContext:
        """Parse Claude Code hook input from stdin.

        Handles different hook types:
        - UserPromptSubmit: Capture checkpoint state
        - Stop: Load checkpoint and find modified files
        """
        stdin_data = self._read_stdin()
        if not stdin_data:
            raise HandlerEnvironmentError(
                "ClaudeCode", "No Claude Code input available"
            )

        hook_event = stdin_data.get("hook_event_name", "")
        session_id = stdin_data.get("session_id", "")
        cwd = stdin_data.get("cwd", "")
        workspace_root = cwd or str(Path.cwd())

        # Handle different hook types
        if hook_event == "UserPromptSubmit":
            return self._parse_user_prompt_submit(
                stdin_data, session_id, workspace_root
            )
        elif hook_event == "Stop":
            return self._parse_stop(stdin_data, session_id, workspace_root)
        else:
            raise HandlerEnvironmentError(
                "ClaudeCode", f"Unsupported hook event: {hook_event}"
            )

    def _parse_user_prompt_submit(
        self, stdin_data: dict[str, Any], session_id: str, workspace_root: str
    ) -> HookInputContext:
        """Handle UserPromptSubmit hook - capture checkpoint state."""
        # Use CLAUDE_PROJECT_DIR as authoritative workspace (set by Claude Code)
        # Fall back to cwd from stdin if not available
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
        workspace = project_dir or workspace_root or str(Path.cwd())
        self._log_checkpoint_event_start("UserPromptSubmit", workspace)

        # Capture checkpoint state before agent starts working
        base_path = Path(workspace)
        checkpoint = capture_checkpoint_state(
            base_path=base_path, session_id=session_id
        )
        self._log_checkpoint_captured("UserPromptSubmit", len(checkpoint.dirty_files))
        self._checkpoint_storage.save(checkpoint)

        return HookInputContext(
            format=self.format,
            raw_data=stdin_data,
            files=[],  # No files to check at this stage
            environment={
                "CLAUDE_HOOK_EVENT_NAME": "UserPromptSubmit",
                "CLAUDE_SESSION_ID": session_id,
                "CLAUDE_CWD": workspace_root,
            },
            metadata={
                "hook_event_name": "UserPromptSubmit",
                "prompt": stdin_data.get("prompt", ""),
                "checkpoint_saved": True,
            },
        )

    def _parse_stop(
        self, stdin_data: dict[str, Any], session_id: str, workspace_root: str
    ) -> HookInputContext:
        """Handle Stop hook - find modified files since checkpoint."""
        # Use CLAUDE_PROJECT_DIR as authoritative workspace (set by Claude Code)
        # Fall back to cwd from stdin if not available
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
        workspace = project_dir or workspace_root or str(Path.cwd())
        self._log_checkpoint_event_start("Stop", workspace)

        # Note: stop_hook_active indicates whether this is a subsequent stop after
        # a previous hook allowed continuation (true) or the first stop (false).
        # We always want to check for conformance regardless of this flag.
        # Infinite loop prevention is handled by returning no findings when appropriate.

        # Load checkpoint and find modified files
        base_path = Path(workspace)
        checkpoint = self._checkpoint_storage.load(workspace, session_id)

        if checkpoint:
            self._log_checkpoint_loaded(
                "Stop", len(checkpoint.dirty_files), checkpoint.head_commit
            )
            # Compare current state to checkpoint
            self._modified_files = get_files_modified_since_checkpoint(
                checkpoint, base_path
            )
            self._log_files_modified_since_checkpoint("Stop", len(self._modified_files))
            # Clean up checkpoint after use
            self._checkpoint_storage.delete(workspace, session_id)
            had_checkpoint = True
        else:
            # No checkpoint - fall back to branch diff
            self._log_no_checkpoint_fallback("Stop")
            self._modified_files = get_branch_changed_files(base_path)
            self._log_branch_diff_result("Stop", len(self._modified_files))
            had_checkpoint = False

        return HookInputContext(
            format=self.format,
            raw_data=stdin_data,
            files=self._modified_files,
            environment={
                "CLAUDE_HOOK_EVENT_NAME": "Stop",
                "CLAUDE_SESSION_ID": session_id,
                "CLAUDE_CWD": workspace_root,
            },
            metadata={
                "hook_event_name": "Stop",
                "stop_hook_active": True,
                "had_checkpoint": had_checkpoint,
            },
        )

    def get_files(self) -> list[Path]:
        """Extract file paths from Claude Code input."""
        context = self.parse_input()
        return context.files

    def build_response_to_hook_call(
        self, has_findings: bool, findings_text: str = ""
    ) -> str | None:
        """Build response as JSON for Claude Code hook.

        Response format depends on hook type:
        - UserPromptSubmit: {} (continue silently)
        - Stop: {"decision": "block", "reason": "..."} if findings, else {}
        """
        stdin_data = self._read_stdin() or {}
        hook_event = stdin_data.get("hook_event_name", "")

        if hook_event == "UserPromptSubmit":
            # Always continue - checkpoint was saved
            return "{}"

        # Stop hook - return block decision if there are findings
        if has_findings and findings_text:
            return json.dumps(
                {
                    "decision": "block",
                    "reason": findings_text,
                }
            )
        return "{}"

    def get_exit_code(self, has_findings: bool) -> int:
        """Get the appropriate exit code for Claude Code handler.

        Args:
            has_findings: Whether conformance issues were found

        Returns:
            CONFORMANCE_ISSUES_FOUND if there are findings (to instruct IDE), SUCCESS otherwise
        """
        return ExitCode.CONFORMANCE_ISSUES_FOUND if has_findings else ExitCode.SUCCESS

    def is_checkpoint_only_event(self, context: HookInputContext) -> bool:
        """Check if this hook event only saves checkpoint state.

        UserPromptSubmit hooks save checkpoint and exit early - no conformance check.

        Args:
            context: The parsed hook input context

        Returns:
            True for UserPromptSubmit events, False otherwise
        """
        hook_event = context.metadata.get("hook_event_name", "")
        return hook_event == "UserPromptSubmit"

    def _read_stdin(self) -> dict[str, Any] | None:
        """Read and parse JSON from stdin if available.

        Returns:
            Parsed JSON data or None if stdin is a tty or can't be read
        """
        if self._stdin_read:
            return self._stdin_data

        self._stdin_read = True

        # Log relevant Claude Code env vars
        self._log_relevant_env_vars(["CLAUDE_"])

        if sys.stdin.isatty():
            echo(
                "Error: stdin is a tty, not reading input",
                persona=Persona.DEVELOPER,
                err=True,
            )
            return None

        try:
            # Try to parse as JSON
            self._stdin_data = json.load(sys.stdin)
            if isinstance(self._stdin_data, dict):
                # Log stdin data for debugging
                self._log_stdin_data(self._stdin_data)
                return self._stdin_data
        except (json.JSONDecodeError, IOError, OSError) as e:
            echo(
                f"Error: Failed to parse stdin as JSON: {e}",
                persona=Persona.DEVELOPER,
                err=True,
            )
            self._stdin_data = None

        return None
