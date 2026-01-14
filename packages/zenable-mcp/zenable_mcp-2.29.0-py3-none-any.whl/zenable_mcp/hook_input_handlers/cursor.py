"""Cursor hook input handler.

See: https://cursor.com/docs/agent/hooks
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


class CursorInputHandler(InputHandler):
    """Handler for Cursor hook inputs.

    See: https://cursor.com/docs/agent/hooks

    Supports the following hook events:
    - beforeSubmitPrompt: Runs before user prompt is sent (checkpoint state)
    - stop: Runs when agent loop ends (review all modified files)

    Cursor sends hook data as JSON to stdin. Common fields:
    {
        "conversation_id": "string",
        "generation_id": "string",
        "hook_event_name": "beforeSubmitPrompt" | "stop",
        "workspace_roots": ["<path>"],
        ...
    }

    beforeSubmitPrompt specific fields:
        "prompt": "user's prompt text",
        "attachments": [...]

    stop specific fields:
        "status": "completed" | "aborted" | "error",
        "loop_count": 0

    Response formats (stdout JSON):
    - beforeSubmitPrompt: {"continue": true} to proceed, {"continue": false} to block
    - stop: {"followup_message": "<findings>"} auto-submits message to continue
            conversation, prompting the agent to address issues

    Note: Cursor ignores exit codes from hooks - communication is via JSON response.
    """

    # Supported hook events for Cursor
    SUPPORTED_EVENTS = {"beforeSubmitPrompt", "stop"}

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
        return "Cursor"

    @property
    def format(self) -> HookInputFormat:
        return HookInputFormat.CURSOR_HOOK

    def can_handle(self) -> bool:
        """Check if we're running as a Cursor hook.

        Checks for:
        1. Non-TTY stdin with JSON data
        2. JSON contains hook_event_name that's a supported Cursor event
        3. Event-specific required fields are present
        """
        stdin_data = self._read_stdin()
        if not stdin_data:
            return False

        hook_event = stdin_data.get("hook_event_name", "")

        if hook_event == "beforeSubmitPrompt":
            # beforeSubmitPrompt requires prompt field
            # https://cursor.com/docs/agent/hooks#beforesubmitprompt
            if "prompt" not in stdin_data:
                echo(
                    "Cursor beforeSubmitPrompt missing required 'prompt' field",
                    persona=Persona.DEVELOPER,
                    err=True,
                )
                return False
            echo(
                "Detected Cursor beforeSubmitPrompt hook in stdin",
                persona=Persona.DEVELOPER,
            )
            return True

        elif hook_event == "stop":
            # stop requires status field
            # https://cursor.com/docs/agent/hooks#stop
            if "status" not in stdin_data:
                echo(
                    "Cursor stop hook missing required 'status' field",
                    persona=Persona.DEVELOPER,
                    err=True,
                )
                return False
            echo(
                "Detected Cursor stop hook in stdin",
                persona=Persona.DEVELOPER,
            )
            return True

        return False

    def parse_input(self) -> HookInputContext:
        """Parse Cursor hook input from stdin.

        Handles different hook types:
        - beforeSubmitPrompt: Capture checkpoint state
        - stop: Load checkpoint and find modified files
        """
        stdin_data = self._read_stdin()
        if not stdin_data:
            raise HandlerEnvironmentError("Cursor", "No Cursor input available")

        hook_event = stdin_data.get("hook_event_name", "")
        conversation_id = stdin_data.get("conversation_id", "")
        workspace_roots = stdin_data.get("workspace_roots", [])
        workspace_root = workspace_roots[0] if workspace_roots else str(Path.cwd())

        if hook_event == "beforeSubmitPrompt":
            return self._parse_before_submit_prompt(
                stdin_data, conversation_id, workspace_root
            )
        elif hook_event == "stop":
            return self._parse_stop(stdin_data, conversation_id, workspace_root)
        else:
            raise HandlerEnvironmentError(
                "Cursor", f"Unsupported hook event: {hook_event}"
            )

    def _parse_before_submit_prompt(
        self, stdin_data: dict[str, Any], conversation_id: str, workspace_root: str
    ) -> HookInputContext:
        """Handle beforeSubmitPrompt hook - capture checkpoint state."""
        self._log_checkpoint_event_start("beforeSubmitPrompt", workspace_root)

        # Capture checkpoint state before agent starts working
        base_path = Path(workspace_root) if workspace_root else None
        checkpoint = capture_checkpoint_state(
            base_path=base_path, session_id=conversation_id
        )
        self._checkpoint_storage.save(checkpoint)
        self._log_checkpoint_captured("beforeSubmitPrompt", len(checkpoint.dirty_files))

        return HookInputContext(
            format=self.format,
            raw_data=stdin_data,
            files=[],  # No files to check at this stage
            environment={
                "CURSOR_HOOK_EVENT_NAME": "beforeSubmitPrompt",
                "CURSOR_CONVERSATION_ID": conversation_id,
                "CURSOR_GENERATION_ID": stdin_data.get("generation_id", ""),
            },
            metadata={
                "hook_event_name": "beforeSubmitPrompt",
                "prompt": stdin_data.get("prompt", ""),
                "attachments": stdin_data.get("attachments", []),
                "checkpoint_saved": True,
            },
        )

    def _parse_stop(
        self, stdin_data: dict[str, Any], conversation_id: str, workspace_root: str
    ) -> HookInputContext:
        """Handle stop hook - find modified files since checkpoint."""
        # Use workspace_root as-is from stdin (workspace_roots[0] from Cursor)
        # This must match what _parse_before_submit_prompt uses for checkpoint save
        workspace = workspace_root or str(Path.cwd())
        self._log_checkpoint_event_start("stop", workspace)

        status = stdin_data.get("status", "completed")
        loop_count = stdin_data.get("loop_count", 0)

        # Load checkpoint and find modified files
        base_path = Path(workspace)
        checkpoint = self._checkpoint_storage.load(workspace, conversation_id)

        if checkpoint:
            self._log_checkpoint_loaded(
                "stop", len(checkpoint.dirty_files), checkpoint.head_commit
            )
            # Compare current state to checkpoint
            self._modified_files = get_files_modified_since_checkpoint(
                checkpoint, base_path
            )
            self._log_files_modified_since_checkpoint("stop", len(self._modified_files))
            # Clean up checkpoint after use
            self._checkpoint_storage.delete(workspace, conversation_id)
            had_checkpoint = True
        else:
            self._log_no_checkpoint_fallback("stop")
            self._modified_files = get_branch_changed_files(base_path)
            self._log_branch_diff_result("stop", len(self._modified_files))
            had_checkpoint = False

        return HookInputContext(
            format=self.format,
            raw_data=stdin_data,
            files=self._modified_files,
            environment={
                "CURSOR_HOOK_EVENT_NAME": "stop",
                "CURSOR_CONVERSATION_ID": conversation_id,
                "CURSOR_GENERATION_ID": stdin_data.get("generation_id", ""),
            },
            metadata={
                "hook_event_name": "stop",
                "status": status,
                "loop_count": loop_count,
                "had_checkpoint": had_checkpoint,
            },
        )

    def get_files(self) -> list[Path]:
        """Extract file paths from Cursor input."""
        context = self.parse_input()
        return context.files

    def build_response_to_hook_call(
        self, has_findings: bool, findings_text: str = ""
    ) -> str | None:
        """Build JSON response for Cursor hook.

        Response format depends on hook type:
        - beforeSubmitPrompt: {"continue": true}
        - stop: {"followup_message": "<findings>"} if findings, else {"followup_message": ""}
        """
        stdin_data = self._read_stdin() or {}
        hook_event = stdin_data.get("hook_event_name", "")

        if hook_event == "beforeSubmitPrompt":
            # Always continue - checkpoint was saved
            return json.dumps({"continue": True})

        # stop hook - return findings in followup_message, empty string if no findings
        if has_findings and findings_text:
            return json.dumps({"followup_message": findings_text})
        return json.dumps({"followup_message": ""})

    def get_exit_code(self, has_findings: bool) -> int:
        """Get the appropriate exit code for Cursor handler.

        Cursor agents don't use exit codes from hooks.
        See https://cursor.com/docs/agent/hooks for current capabilities.

        Args:
            has_findings: Whether conformance issues were found

        Returns:
            Always SUCCESS (exit code 0) for Cursor
        """
        return ExitCode.SUCCESS

    def is_checkpoint_only_event(self, context: HookInputContext) -> bool:
        """Check if this hook event only saves checkpoint state.

        beforeSubmitPrompt hooks save checkpoint and exit early - no conformance check.

        Args:
            context: The parsed hook input context

        Returns:
            True for beforeSubmitPrompt events, False otherwise
        """
        hook_event = context.metadata.get("hook_event_name", "")
        return hook_event == "beforeSubmitPrompt"

    def _read_stdin(self) -> dict[str, Any] | None:
        """Read and parse JSON from stdin if available.

        Returns:
            Parsed JSON data or None if stdin is a tty or can't be read
        """
        if self._stdin_read:
            return self._stdin_data

        self._stdin_read = True

        # Log relevant Cursor env vars
        self._log_relevant_env_vars(["CURSOR_"])

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
