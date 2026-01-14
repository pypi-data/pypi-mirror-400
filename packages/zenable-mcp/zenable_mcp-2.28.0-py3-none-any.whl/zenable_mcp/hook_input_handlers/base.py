"""Base classes and interfaces for hook input handlers."""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona


@dataclass
class HookOutputConfig:
    """Configuration for how hook responses should be output.

    Attributes:
        response_to_stderr: If True, send formatted_response to stderr instead of stdout.
                           Claude Code expects JSON on stdout; Cursor may use stderr.
    """

    response_to_stderr: bool = False


logger = logging.getLogger(__name__)


class HookInputFormat(Enum):
    """Supported hook input formats."""

    CLAUDE_CODE_HOOK = "claude_code_hook"
    CURSOR_HOOK = "cursor_hook"
    WINDSURF_HOOK = "windsurf_hook"
    KIRO_HOOK = "kiro_hook"
    UNKNOWN = "unknown"


class HookInputContext(BaseModel):
    """Context information extracted from various input sources."""

    model_config = ConfigDict(strict=True)

    format: HookInputFormat
    raw_data: Optional[dict[str, Any]] = None
    files: list[Path] = Field(default_factory=list)
    environment: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InputHandler(ABC):
    """Abstract base class for input handlers.

    Each handler is responsible for:
    1. Detecting if it can handle the current input context
    2. Parsing and extracting relevant information
    3. Returning structured data for processing

    Handlers can receive shared stdin data from the registry to avoid
    multiple stdin reads when multiple handlers are registered.
    """

    def set_shared_stdin_data(self, data: dict[str, Any] | None) -> None:
        """Set shared stdin data from the registry.

        This allows the registry to read stdin once and share it with all handlers,
        avoiding the issue of multiple handlers trying to read stdin.

        Args:
            data: Parsed JSON data from stdin, or None if stdin couldn't be read
        """
        # Subclasses should override to use this data
        pass

    @abstractmethod
    def can_handle(self) -> bool:
        """Check if this handler can process the current input.

        This method should check various sources (stdin, env vars, files, etc.)
        to determine if this handler is applicable.

        Returns:
            True if this handler can process the input, False otherwise
        """
        pass

    @abstractmethod
    def parse_input(self) -> HookInputContext:
        """Parse the input and extract relevant information.

        Returns:
            HookInputContext containing parsed data and metadata
        """
        pass

    @abstractmethod
    def get_files(self) -> list[Path]:
        """Extract file paths that should be checked.

        Returns:
            List of Path objects for files to check
        """
        pass

    @abstractmethod
    def build_response_to_hook_call(
        self, has_findings: bool, findings_text: str = ""
    ) -> Optional[str]:
        """Build the response to send back to the hook caller.

        This formats the response according to the hook's protocol requirements
        (e.g., JSON for Claude Code hooks).

        Args:
            has_findings: Whether conformance issues were found
            findings_text: Text describing the findings

        Returns:
            Formatted response string for the hook or None if no special format needed
        """
        pass

    def format_response_for_humans(
        self, has_findings: bool, findings_text: str = ""
    ) -> str:
        """Format the response for human-readable output.

        This provides a user-friendly representation of the findings
        suitable for terminal output or logs.

        Args:
            has_findings: Whether conformance issues were found
            findings_text: Text describing the findings

        Returns:
            Human-readable response string
        """
        if has_findings:
            return f"Conformance issues found:\n{findings_text}"
        return "No conformance issues found."

    def get_exit_code(self, has_findings: bool) -> int:
        """Get the appropriate exit code for this handler.

        Args:
            has_findings: Whether conformance issues were found

        Returns:
            Exit code to use (default is SUCCESS)
        """
        return ExitCode.SUCCESS  # Default: success

    def get_output_config(self) -> HookOutputConfig:
        """Get output configuration for this handler.

        Override in subclasses to customize where output is sent.
        Default sends formatted_response to stdout (for Claude Code compatibility).

        Returns:
            HookOutputConfig with output preferences
        """
        return HookOutputConfig(response_to_stderr=False)

    def is_checkpoint_only_event(self, context: "HookInputContext") -> bool:
        """Check if this hook event only saves checkpoint state (no conformance check).

        Checkpoint-only events (like UserPromptSubmit, beforeSubmitPrompt) save state
        before the agent starts working and should exit early without running checks.

        Args:
            context: The parsed hook input context

        Returns:
            True if this is a checkpoint-only event, False otherwise
        """
        return False  # Default: all events require conformance check

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this handler."""
        pass

    @property
    @abstractmethod
    def format(self) -> HookInputFormat:
        """Get the input format this handler processes."""
        pass

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name}, format={self.format.value})"
        )

    def _log_stdin_data(self, stdin_data: dict[str, Any] | None) -> None:
        """Log stdin data for debugging.

        This should be called after stdin is successfully parsed.
        Uses Persona.DEVELOPER to only show in developer logs.

        Args:
            stdin_data: The parsed stdin data, or None if stdin couldn't be parsed
        """
        if stdin_data is None:
            echo(f"[{self.name}] stdin: None", persona=Persona.DEVELOPER, log=True)
            return

        try:
            stdin_json = json.dumps(stdin_data, default=str, indent=2)
            echo(
                f"[{self.name}] stdin data:\n{stdin_json}",
                persona=Persona.DEVELOPER,
                log=True,
            )
        except (TypeError, ValueError) as e:
            echo(
                f"[{self.name}] stdin data (could not serialize): {e}",
                persona=Persona.DEVELOPER,
                log=True,
            )

    def _log_relevant_env_vars(self, env_var_prefixes: list[str]) -> None:
        """Log relevant environment variables for debugging.

        Args:
            env_var_prefixes: List of env var prefixes to log (e.g., ["CLAUDE_", "CURSOR_"])
        """
        relevant_vars = {}
        for key, value in os.environ.items():
            for prefix in env_var_prefixes:
                if key.startswith(prefix):
                    relevant_vars[key] = value
                    break

        if relevant_vars:
            echo(
                f"[{self.name}] relevant env vars: {relevant_vars}",
                persona=Persona.DEVELOPER,
                log=True,
            )
        else:
            echo(
                f"[{self.name}] no relevant env vars found with prefixes: {env_var_prefixes}",
                persona=Persona.DEVELOPER,
                log=True,
            )

    # Shared checkpoint logging methods for uniform logging across all handlers

    def _log_checkpoint_event_start(self, hook_event: str, workspace: str) -> None:
        """Log the start of processing a checkpoint-related hook event.

        Args:
            hook_event: The hook event name (e.g., "UserPromptSubmit", "Stop")
            workspace: Workspace root path (cwd for Claude Code/Kiro, workspace_roots[0] for Cursor)
        """
        echo(
            f"Handling {self.name} {hook_event} hook: Processing (workspace={workspace})",
            persona=Persona.DEVELOPER,
            log=True,
        )

    def _log_checkpoint_captured(self, hook_event: str, num_dirty_files: int) -> None:
        """Log that a checkpoint was captured.

        Args:
            hook_event: The hook event name
            num_dirty_files: Number of dirty files captured in checkpoint
        """
        echo(
            f"Handling {self.name} {hook_event} hook: Checkpoint captured with {num_dirty_files} dirty file(s)",
            persona=Persona.DEVELOPER,
            log=True,
        )

    def _log_checkpoint_loaded(
        self, hook_event: str, num_dirty_files: int, head_commit: str
    ) -> None:
        """Log that a checkpoint was loaded.

        Args:
            hook_event: The hook event name
            num_dirty_files: Number of dirty files in the checkpoint
            head_commit: HEAD commit hash from checkpoint
        """
        head_display = head_commit[:8] if head_commit else "none"
        echo(
            f"Handling {self.name} {hook_event} hook: Checkpoint loaded with {num_dirty_files} dirty file(s), HEAD={head_display}",
            persona=Persona.DEVELOPER,
            log=True,
        )

    def _log_files_modified_since_checkpoint(
        self, hook_event: str, num_files: int
    ) -> None:
        """Log the number of files modified since checkpoint.

        Args:
            hook_event: The hook event name
            num_files: Number of files modified since checkpoint
        """
        echo(
            f"Handling {self.name} {hook_event} hook: {num_files} file(s) modified since checkpoint",
            persona=Persona.DEVELOPER,
            log=True,
        )

    def _log_no_checkpoint_fallback(self, hook_event: str) -> None:
        """Log that no checkpoint was found and falling back to branch diff.

        Args:
            hook_event: The hook event name
        """
        echo(
            f"Handling {self.name} {hook_event} hook: No checkpoint found, falling back to branch diff",
            persona=Persona.DEVELOPER,
            log=True,
        )

    def _log_branch_diff_result(self, hook_event: str, num_files: int) -> None:
        """Log the result of branch diff fallback.

        Args:
            hook_event: The hook event name
            num_files: Number of files found via branch diff
        """
        echo(
            f"Handling {self.name} {hook_event} hook: Branch diff found {num_files} file(s)",
            persona=Persona.DEVELOPER,
            log=True,
        )
