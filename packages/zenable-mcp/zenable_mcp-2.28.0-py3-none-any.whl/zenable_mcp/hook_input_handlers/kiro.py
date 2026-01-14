"""Kiro hook input handler.

See: https://kiro.dev/docs/hooks/types/
See: https://kiro.dev/changelog/web-tools-subagents-contextual-hooks-and-per-file-code-review/

Kiro supports loop-based hooks with two key triggers:
- agentStart: Runs when an agent loop starts (for checkpointing)
- agentEnd: Runs when the agent loop ends (for conformance check)

Note: Hook event names discovered via experimentation on 2025-12-26.
The documented "userPromptSubmit" doesn't work; "agentStart"/"agentEnd" do.

Kiro hooks are configured via JSON files in .kiro/hooks/<name>.hook directory.
Example hook file format:
{
  "enabled": true,
  "name": "Hook Name",
  "when": {"type": "agentStart"},
  "then": {"type": "runCommand", "command": "..."}
}
"""

import json
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


class KiroInputHandler(InputHandler):
    """Handler for Kiro hook inputs.

    See: https://kiro.dev/docs/hooks/types/
    See: https://kiro.dev/changelog/web-tools-subagents-contextual-hooks-and-per-file-code-review/

    Note: Hook event names discovered via experimentation on 2025-12-26.
    The documented "userPromptSubmit" doesn't work; "agentStart"/"agentEnd" do.

    Supports the following hook events:
    - agentStart: Runs when an agent loop starts (checkpoint state)
    - agentEnd: Runs when agent loop ends (review all modified files)

    Kiro sends hook data as JSON to stdin. Common fields:
    {
        "hook_event_name": "agentStart" | "agentEnd",
        "cwd": "/working/directory",
        ...
    }

    Response format:
    - stdout text is added as context to the conversation
    - Exit code 0 for success, non-zero to indicate issues
    """

    # Supported hook events for Kiro
    # Note: Discovered via experimentation on 2025-12-26
    SUPPORTED_EVENTS = {"agentStart", "agentEnd"}

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
        return "Kiro"

    @property
    def format(self) -> HookInputFormat:
        return HookInputFormat.KIRO_HOOK

    def can_handle(self) -> bool:
        """Check if we're running as a Kiro hook.

        Checks for:
        1. Non-TTY stdin with JSON data
        2. JSON contains hook_event_name that's a supported Kiro event
        """
        stdin_data = self._read_stdin()
        if not stdin_data:
            return False

        hook_event = stdin_data.get("hook_event_name", "")

        if hook_event in self.SUPPORTED_EVENTS:
            echo(
                f"Detected Kiro {hook_event} hook in stdin",
                persona=Persona.DEVELOPER,
            )
            return True

        return False

    def parse_input(self) -> HookInputContext:
        """Parse Kiro hook input from stdin.

        Handles different hook types:
        - agentStart: Capture checkpoint state
        - agentEnd: Load checkpoint and find modified files
        """
        stdin_data = self._read_stdin()
        if not stdin_data:
            raise HandlerEnvironmentError("Kiro", "No Kiro input available")

        hook_event = stdin_data.get("hook_event_name", "")
        cwd = stdin_data.get("cwd", "")
        workspace_root = cwd or str(Path.cwd())

        # Generate a session ID from cwd since Kiro doesn't provide one
        # Use a hash of the workspace to create a stable session ID
        session_id = f"kiro-{hash(workspace_root) & 0xFFFFFFFF:08x}"

        if hook_event == "agentStart":
            return self._parse_agent_start(stdin_data, session_id, workspace_root)
        elif hook_event == "agentEnd":
            return self._parse_agent_end(stdin_data, session_id, workspace_root)
        else:
            raise HandlerEnvironmentError(
                "Kiro", f"Unsupported hook event: {hook_event}"
            )

    def _parse_agent_start(
        self, stdin_data: dict[str, Any], session_id: str, workspace_root: str
    ) -> HookInputContext:
        """Handle agentStart hook - capture checkpoint state."""
        self._log_checkpoint_event_start("agentStart", workspace_root)

        # Capture checkpoint state before agent starts working
        base_path = Path(workspace_root) if workspace_root else None
        checkpoint = capture_checkpoint_state(
            base_path=base_path, session_id=session_id
        )
        self._checkpoint_storage.save(checkpoint)
        self._log_checkpoint_captured("agentStart", len(checkpoint.dirty_files))

        return HookInputContext(
            format=self.format,
            raw_data=stdin_data,
            files=[],  # No files to check at this stage
            environment={
                "KIRO_HOOK_EVENT_NAME": "agentStart",
                "KIRO_CWD": workspace_root,
            },
            metadata={
                "hook_event_name": "agentStart",
                "checkpoint_saved": True,
            },
        )

    def _parse_agent_end(
        self, stdin_data: dict[str, Any], session_id: str, workspace_root: str
    ) -> HookInputContext:
        """Handle agentEnd hook - find modified files since checkpoint."""
        # Use workspace_root as-is from stdin (cwd from Kiro)
        # This must match what _parse_agent_start uses for checkpoint save
        workspace = workspace_root or str(Path.cwd())
        self._log_checkpoint_event_start("agentEnd", workspace)

        # Load checkpoint and find modified files
        base_path = Path(workspace)
        checkpoint = self._checkpoint_storage.load(workspace, session_id)

        if checkpoint:
            self._log_checkpoint_loaded(
                "agentEnd", len(checkpoint.dirty_files), checkpoint.head_commit
            )
            # Compare current state to checkpoint
            self._modified_files = get_files_modified_since_checkpoint(
                checkpoint, base_path
            )
            self._log_files_modified_since_checkpoint(
                "agentEnd", len(self._modified_files)
            )
            # Clean up checkpoint after use
            self._checkpoint_storage.delete(workspace, session_id)
            had_checkpoint = True
        else:
            # No checkpoint - fall back to branch diff
            self._log_no_checkpoint_fallback("agentEnd")
            self._modified_files = get_branch_changed_files(base_path)
            self._log_branch_diff_result("agentEnd", len(self._modified_files))
            had_checkpoint = False

        return HookInputContext(
            format=self.format,
            raw_data=stdin_data,
            files=self._modified_files,
            environment={
                "KIRO_HOOK_EVENT_NAME": "agentEnd",
                "KIRO_CWD": workspace_root,
            },
            metadata={
                "hook_event_name": "agentEnd",
                "had_checkpoint": had_checkpoint,
            },
        )

    def get_files(self) -> list[Path]:
        """Extract file paths from Kiro input."""
        context = self.parse_input()
        return context.files

    def build_response_to_hook_call(
        self, has_findings: bool, findings_text: str = ""
    ) -> str | None:
        """Build response for Kiro hook.

        Kiro adds stdout text as context to the conversation.
        For agentStart, we return empty (checkpoint saved silently).
        For agentEnd, we return findings as plain text for the agent to see.
        """
        stdin_data = self._read_stdin() or {}
        hook_event = stdin_data.get("hook_event_name", "")

        if hook_event == "agentStart":
            # Return empty - checkpoint was saved
            return ""

        # agentEnd hook - return findings as plain text
        if has_findings and findings_text:
            return findings_text
        return ""

    def get_exit_code(self, has_findings: bool) -> int:
        """Get the appropriate exit code for Kiro handler.

        Args:
            has_findings: Whether conformance issues were found

        Returns:
            CONFORMANCE_ISSUES_FOUND if there are findings, SUCCESS otherwise
        """
        return ExitCode.CONFORMANCE_ISSUES_FOUND if has_findings else ExitCode.SUCCESS

    def is_checkpoint_only_event(self, context: HookInputContext) -> bool:
        """Check if this hook event only saves checkpoint state.

        agentStart hooks save checkpoint and exit early - no conformance check.

        Args:
            context: The parsed hook input context

        Returns:
            True for agentStart events, False otherwise
        """
        hook_event = context.metadata.get("hook_event_name", "")
        return hook_event == "agentStart"

    def _read_stdin(self) -> dict[str, Any] | None:
        """Read and parse JSON from stdin if available.

        Returns:
            Parsed JSON data or None if stdin is a tty or can't be read
        """
        if self._stdin_read:
            return self._stdin_data

        self._stdin_read = True

        # Log relevant Kiro env vars
        self._log_relevant_env_vars(["KIRO_"])

        if sys.stdin.isatty():
            echo(
                "Error: stdin is a tty, not reading input",
                persona=Persona.DEVELOPER,
                err=True,
            )
            return None

        try:
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
