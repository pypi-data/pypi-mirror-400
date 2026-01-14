"""Hook installation commands for zenable-mcp."""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import click

from zenable_mcp import __version__
from zenable_mcp.commands.install.command_generator import attach_hook_commands
from zenable_mcp.exceptions import IDECapabilityError
from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.ide_config import (
    ClaudeCodeConfig,
    CursorConfig,
    IDEConfig,
    WindsurfConfig,
    find_git_root,
)
from zenable_mcp.logging.command_logger import log_command
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.utils.config_manager import (
    backup_config_file,
    load_json_config,
    safe_write_json,
)
from zenable_mcp.utils.context_helpers import (
    get_dry_run_from_context,
    get_flag_from_context,
    get_git_repos_from_context,
    get_is_global_from_context,
    get_recursive_from_context,
)
from zenable_mcp.utils.install_report import (
    filter_git_repositories,
    get_patterns_from_context,
    show_complete_filtering_information,
    show_filtering_results,
)
from zenable_mcp.utils.install_status import (
    InstallResult,
    InstallStatus,
    get_exit_code,
    show_installation_summary,
)
from zenable_mcp.utils.operation_status import OperationStatus
from zenable_mcp.utils.recursive_operations import (
    execute_in_git_repositories,
    find_git_repositories,
)
from zenable_mcp.utils.repo_selection_handler import handle_repository_selection
from zenable_mcp.utils.repo_selector import prompt_for_repository_selection

# Semver pattern for matching version strings in package specifications
_SEMVER_PATTERN = re.compile(
    r"@(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?)"
)


# ============================================================================
# Hook Installation Context - IDE-specific configuration
# ============================================================================


@dataclass
class HookInstallContext:
    """IDE-specific configuration for hook installation.

    This dataclass captures all the differences between IDE hook systems,
    allowing shared installation logic to work across different IDEs.
    """

    # IDE identification
    ide_name: str
    hook_display_name: str

    # Configuration factory
    config_class: type[IDEConfig]

    # Hook structure - how hooks are organized in the config file
    hook_event_key: (
        str  # e.g., "UserPromptSubmit" for Claude, "beforeSubmitPrompt" for Cursor
    )
    hooks_container_key: str = "hooks"  # Top-level key containing hooks

    # Hook config creation
    create_hook_config: Callable[[], dict] = field(default=lambda: {})

    # Structure initialization - called to ensure required keys exist
    ensure_structure: Callable[[dict], None] = field(default=lambda s: None)

    # Hook analysis - extracts command from a hook entry
    extract_command: Callable[[dict], str] = field(default=lambda h: "")


# ============================================================================
# Unified Hook Installation Helpers
# ============================================================================


def get_hook_settings_path(ctx: HookInstallContext, is_global: bool) -> Path:
    """Get the settings path for any IDE using its context.

    Args:
        ctx: IDE-specific hook installation context
        is_global: Whether to use global settings

    Returns:
        Path to the settings file

    Raises:
        SystemExit: If path cannot be determined or IDE doesn't support mode
    """
    try:
        config = ctx.config_class(is_global=is_global)
        config.validate_hook_installation_mode(is_global)
        settings_path = config.get_default_hook_config_path()
        if not settings_path:
            if not is_global:
                echo(
                    "Not in a git repository.\n"
                    "Did you mean to do the global installation with --global?",
                    err=True,
                )
            else:
                echo("No hook configuration path available", err=True)
            sys.exit(ExitCode.INSTALLATION_ERROR)
        return settings_path
    except IDECapabilityError as e:
        echo(str(e), err=True)
        sys.exit(ExitCode.INVALID_PARAMETERS)
    except ValueError as e:
        echo(str(e), err=True)
        sys.exit(ExitCode.INSTALLATION_ERROR)


def _analyze_hooks(
    ctx: HookInstallContext, hooks_list: list, new_hook_config: dict
) -> dict:
    """Analyze existing hooks for duplicates and similar configurations.

    Args:
        ctx: IDE-specific hook installation context
        hooks_list: List of existing hooks for the event
        new_hook_config: The new hook configuration to check against

    Returns:
        Dictionary with analysis results (hook_exists, has_latest, similar_hook_indices,
        pinned_version_indices)
    """
    result = {
        "hook_exists": False,
        "has_latest": False,
        "similar_hook_indices": [],
        "pinned_version_indices": [],
    }

    for i, existing_hook in enumerate(hooks_list):
        if existing_hook == new_hook_config:
            result["hook_exists"] = True
            break

        command = ctx.extract_command(existing_hook)

        if command.startswith("uvx zenable-mcp"):
            if "@latest" in command:
                result["has_latest"] = True
            elif _SEMVER_PATTERN.search(command):
                result["pinned_version_indices"].append(i)
            elif command != "uvx zenable-mcp@latest hook":
                result["similar_hook_indices"].append(i)

    return result


def _hook_install_impl(
    ctx: HookInstallContext, is_global: bool, dry_run: bool = False
) -> InstallResult:
    """Unified hook installation implementation for any IDE.

    Args:
        ctx: IDE-specific hook installation context
        is_global: Whether to install globally
        dry_run: Whether to show what would be done without making changes

    Returns:
        InstallResult object
    """
    settings_path = get_hook_settings_path(ctx, is_global)
    new_hook_config = ctx.create_hook_config()

    # Create directory if not dry-run
    if not dry_run:
        settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings, has_comments = _load_or_create_settings(settings_path)
    ctx.ensure_structure(settings)

    # Get the hooks list for this event type
    hooks_list = settings[ctx.hooks_container_key].get(ctx.hook_event_key, [])
    num_hooks = len(hooks_list)

    if num_hooks > 0:
        echo(
            f"Found {num_hooks} existing {ctx.hook_event_key} hook(s) in {settings_path}",
            persona=Persona.POWER_USER,
        )
    else:
        echo(
            f"No existing {ctx.hook_event_key} hooks found in {settings_path}",
            persona=Persona.POWER_USER,
        )

    analysis = _analyze_hooks(ctx, hooks_list, new_hook_config)

    # Check for already installed hooks
    if analysis["hook_exists"]:
        echo(
            f"{ctx.hook_display_name} already properly installed in {settings_path}",
            persona=Persona.POWER_USER,
        )
        return InstallResult(
            InstallStatus.ALREADY_INSTALLED,
            ctx.hook_display_name,
            "Hook already installed - no changes needed",
        )

    # Check for @latest already installed
    if analysis["has_latest"]:
        echo(
            f"{ctx.hook_display_name} with @latest already installed in {settings_path}",
            persona=Persona.POWER_USER,
        )
        return InstallResult(
            InstallStatus.ALREADY_INSTALLED,
            ctx.hook_display_name,
            "Hook with @latest already installed - no changes needed",
        )

    # Handle pinned versions - update them to @latest
    if analysis["pinned_version_indices"]:
        result = _handle_pinned_versions(
            ctx,
            hooks_list,
            analysis["pinned_version_indices"],
            new_hook_config,
            settings_path,
            settings,
            has_comments,
            dry_run,
        )
        if result:
            return result

    # Handle similar hooks - update them
    if analysis["similar_hook_indices"]:
        result = _handle_similar_hooks(
            ctx,
            hooks_list,
            analysis["similar_hook_indices"],
            new_hook_config,
            settings_path,
            settings,
            has_comments,
            dry_run,
        )
        if result:
            return result

    # Add new hook
    if not dry_run:
        hooks_list.append(new_hook_config)
        success, _ = _save_settings_with_confirmation(
            settings_path, settings, has_comments, dry_run
        )
        if not success:
            return InstallResult(
                InstallStatus.CANCELLED,
                ctx.hook_display_name,
                "Installation cancelled",
            )

    return InstallResult(
        InstallStatus.SUCCESS,
        ctx.hook_display_name,
        f"{ctx.hook_display_name} installed",
    )


def _handle_pinned_versions(
    ctx: HookInstallContext,
    hooks_list: list,
    pinned_indices: list,
    new_hook_config: dict,
    settings_path: Path,
    settings: dict,
    has_comments: bool,
    dry_run: bool,
) -> InstallResult | None:
    """Handle updating pinned version hooks to @latest."""
    if not pinned_indices:
        return None

    old_version = "unknown"

    for idx in pinned_indices:
        old_hook = hooks_list[idx]
        old_command = ctx.extract_command(old_hook)
        version_match = _SEMVER_PATTERN.search(old_command)
        old_version = version_match.group(1) if version_match else "unknown"

        hooks_list[idx] = new_hook_config

        if not dry_run:
            success, _ = _save_settings_with_confirmation(
                settings_path, settings, has_comments, dry_run
            )
            if not success:
                return InstallResult(
                    InstallStatus.CANCELLED,
                    ctx.hook_display_name,
                    "Installation cancelled",
                )

        if old_version != __version__:
            message = f"Updated hook from pinned version ({old_version}) to @latest (current: {__version__})"
        else:
            message = f"Updated hook from pinned version ({old_version}) to @latest"

        return InstallResult(InstallStatus.SUCCESS, ctx.hook_display_name, message)

    return None


def _handle_similar_hooks(
    ctx: HookInstallContext,
    hooks_list: list,
    similar_indices: list,
    new_hook_config: dict,
    settings_path: Path,
    settings: dict,
    has_comments: bool,
    dry_run: bool,
) -> InstallResult | None:
    """Handle updating similar hooks."""
    if not similar_indices:
        return None

    for idx in reversed(similar_indices):
        hooks_list[idx] = new_hook_config

    if not dry_run:
        success, _ = _save_settings_with_confirmation(
            settings_path, settings, has_comments, dry_run
        )
        if not success:
            return InstallResult(
                InstallStatus.CANCELLED, ctx.hook_display_name, "Installation cancelled"
            )

    return InstallResult(
        InstallStatus.SUCCESS,
        ctx.hook_display_name,
        "Updated existing hook to 'uvx zenable-mcp@latest hook'",
    )


# ============================================================================
# IDE-Specific Context Definitions
# ============================================================================


def _claude_ensure_structure(settings: dict) -> None:
    """Ensure Claude Code hook structure exists."""
    settings.setdefault("hooks", {})
    settings["hooks"].setdefault("UserPromptSubmit", [])
    settings["hooks"].setdefault("Stop", [])


def _claude_extract_command(hook: dict) -> str:
    """Extract command from Claude Code hook format.

    Format: {"hooks": [{"type": "command", "command": "..."}]}
    """
    if not isinstance(hook, dict):
        return ""

    if "hooks" in hook and isinstance(hook["hooks"], list):
        for inner_hook in hook["hooks"]:
            if isinstance(inner_hook, dict) and inner_hook.get("type") == "command":
                return inner_hook.get("command", "")

    return ""


def _claude_create_hook_config() -> dict:
    """Create Claude Code hook configuration.

    Uses the new format with matchers:
    {"hooks": [{"type": "command", "command": "..."}]}
    """
    return {"hooks": [{"type": "command", "command": "uvx zenable-mcp@latest hook"}]}


def _cursor_ensure_structure(settings: dict) -> None:
    """Ensure Cursor hook structure exists."""
    settings.setdefault("version", 1)
    settings.setdefault("hooks", {})
    settings["hooks"].setdefault("beforeSubmitPrompt", [])
    settings["hooks"].setdefault("stop", [])


def _cursor_extract_command(hook: dict) -> str:
    """Extract command from Cursor hook format (simple command key)."""
    return hook.get("command", "") if isinstance(hook, dict) else ""


def _cursor_create_hook_config() -> dict:
    """Create Cursor hook configuration."""
    return {"command": "uvx zenable-mcp@latest hook"}


def _windsurf_ensure_structure(settings: dict) -> None:
    """Ensure Windsurf hook structure exists."""
    settings.setdefault("hooks", {})
    settings["hooks"].setdefault("post_write_code", [])


def _windsurf_extract_command(hook: dict) -> str:
    """Extract command from Windsurf hook format (simple command key)."""
    return hook.get("command", "") if isinstance(hook, dict) else ""


def _windsurf_create_hook_config() -> dict:
    """Create Windsurf hook configuration."""
    return {"command": "uvx zenable-mcp@latest hook", "show_output": True}


# Claude Code contexts - UserPromptSubmit and Stop hooks
_CLAUDE_USER_PROMPT_SUBMIT_CONTEXT = HookInstallContext(
    ide_name="claude-code",
    hook_display_name="Claude Code UserPromptSubmit hook",
    config_class=ClaudeCodeConfig,
    hook_event_key="UserPromptSubmit",
    hooks_container_key="hooks",
    create_hook_config=_claude_create_hook_config,
    ensure_structure=_claude_ensure_structure,
    extract_command=_claude_extract_command,
)

_CLAUDE_STOP_CONTEXT = HookInstallContext(
    ide_name="claude-code",
    hook_display_name="Claude Code Stop hook",
    config_class=ClaudeCodeConfig,
    hook_event_key="Stop",
    hooks_container_key="hooks",
    create_hook_config=_claude_create_hook_config,
    ensure_structure=_claude_ensure_structure,
    extract_command=_claude_extract_command,
)

# Cursor contexts - beforeSubmitPrompt and stop hooks
_CURSOR_BEFORE_SUBMIT_CONTEXT = HookInstallContext(
    ide_name="cursor",
    hook_display_name="Cursor beforeSubmitPrompt hook",
    config_class=CursorConfig,
    hook_event_key="beforeSubmitPrompt",
    hooks_container_key="hooks",
    create_hook_config=_cursor_create_hook_config,
    ensure_structure=_cursor_ensure_structure,
    extract_command=_cursor_extract_command,
)

_CURSOR_STOP_CONTEXT = HookInstallContext(
    ide_name="cursor",
    hook_display_name="Cursor stop hook",
    config_class=CursorConfig,
    hook_event_key="stop",
    hooks_container_key="hooks",
    create_hook_config=_cursor_create_hook_config,
    ensure_structure=_cursor_ensure_structure,
    extract_command=_cursor_extract_command,
)

# Windsurf context - post_write_code hook
_WINDSURF_HOOK_CONTEXT = HookInstallContext(
    ide_name="windsurf",
    hook_display_name="Windsurf hook",
    config_class=WindsurfConfig,
    hook_event_key="post_write_code",
    hooks_container_key="hooks",
    create_hook_config=_windsurf_create_hook_config,
    ensure_structure=_windsurf_ensure_structure,
    extract_command=_windsurf_extract_command,
)


# ============================================================================
# Shared Helper Functions
# ============================================================================


def _load_or_create_settings(settings_path: Path) -> tuple[dict, bool]:
    """Load existing settings or create new empty settings.

    Args:
        settings_path: Path to the settings file

    Returns:
        Tuple of (Dictionary of settings, has_comments flag)

    Raises:
        click.ClickException: If JSON is invalid
    """
    if settings_path.exists() and settings_path.stat().st_size > 0:
        try:
            data, has_comments = load_json_config(settings_path)
            return data, has_comments
        except (ValueError, IOError) as e:
            echo(
                f"Failed to load settings from {settings_path}\n"
                f"Details: {e}\n"
                f"Please fix the JSON syntax or backup and remove the file.",
                err=True,
            )
            sys.exit(ExitCode.FILE_READ_ERROR)
    return {}, False


def _prompt_for_comment_warning(
    settings_path: Path, dry_run: bool = False
) -> tuple[bool, Path | None]:
    """Prompt user to confirm modification of a JSON file with comments.

    Args:
        settings_path: Path to the settings file that has comments
        dry_run: If True, always return True without prompting

    Returns:
        Tuple of (True if user confirms or dry_run is True, backup path if created)
    """
    if dry_run:
        return True, None

    # Create backup first
    backup_path = backup_config_file(settings_path)

    echo(
        click.style("\n⚠️  Warning: ", fg="yellow", bold=True)
        + f"The file {settings_path} contains comments or JSON5 features.\n"
        "These comments will be LOST when the file is saved.\n"
        f"\nA backup has been created at: {backup_path}"
    )

    confirmed = click.confirm(
        "Do you want to proceed with the modification?", default=False
    )
    return confirmed, backup_path if confirmed else None


def _save_settings_with_confirmation(
    settings_path: Path, settings: dict, has_comments: bool, dry_run: bool
) -> tuple[bool, Path | None]:
    """Save settings with confirmation if file has comments.

    Args:
        settings_path: Path to save settings to
        settings: Settings dictionary to save
        has_comments: Whether the file has comments
        dry_run: Whether this is a dry run

    Returns:
        Tuple of (success, backup_path)
    """
    if dry_run:
        return True, None

    backup_path = None
    if has_comments:
        confirmed, backup_path = _prompt_for_comment_warning(settings_path, dry_run)
        if not confirmed:
            return False, None

    safe_write_json(settings_path, settings)
    return True, backup_path


# ============================================================================
# IDE Implementation Functions
# ============================================================================


def _install_claude_hook_in_repo(repo_path: Path, dry_run: bool) -> list[InstallResult]:
    """Install Claude Code hook in a specific repository.

    This is used as the operation function for recursive installations.

    Args:
        repo_path: Path to the repository (unused but required by interface)
        dry_run: Whether this is a dry run

    Returns:
        List of InstallResult objects for each hook
    """
    try:
        return _claude_impl(is_global=False, dry_run=dry_run)
    except SystemExit:
        return [InstallResult(InstallStatus.FAILED, "Claude Code hooks", "Failed")]


def _claude_impl(is_global: bool, dry_run: bool = False) -> list[InstallResult]:
    """Implementation of Claude Code hook installation.

    Installs Claude Code hooks: UserPromptSubmit, Stop.

    Args:
        is_global: Whether to install globally
        dry_run: Whether to show what would be done without making changes

    Returns:
        List of InstallResult objects for each hook
    """
    contexts = [
        _CLAUDE_USER_PROMPT_SUBMIT_CONTEXT,
        _CLAUDE_STOP_CONTEXT,
    ]

    results = []
    for ctx in contexts:
        result = _hook_install_impl(ctx, is_global, dry_run)
        results.append(result)

    return results


def _get_claude_global_hook_path() -> Path:
    """Get the Claude Code global hook configuration path.

    Returns:
        Path object for the global hook config
    """
    config = ClaudeCodeConfig(is_global=True)
    return config.get_default_hook_config_path()


def _install_cursor_hook_in_repo(repo_path: Path, dry_run: bool) -> list[InstallResult]:
    """Install Cursor hook in a specific repository.

    Args:
        repo_path: Path to the repository (unused but required by interface)
        dry_run: Whether this is a dry run

    Returns:
        List of InstallResult objects for each hook
    """
    try:
        return _cursor_impl(is_global=False, dry_run=dry_run)
    except SystemExit:
        return [InstallResult(InstallStatus.FAILED, "Cursor hooks", "Failed")]


def _cursor_impl(is_global: bool, dry_run: bool = False) -> list[InstallResult]:
    """Implementation of Cursor hook installation.

    Installs Cursor hooks: beforeSubmitPrompt, stop.

    Args:
        is_global: Whether to install globally
        dry_run: Whether to show what would be done without making changes

    Returns:
        List of InstallResult objects for each hook
    """
    contexts = [
        _CURSOR_BEFORE_SUBMIT_CONTEXT,
        _CURSOR_STOP_CONTEXT,
    ]

    results = []
    for ctx in contexts:
        result = _hook_install_impl(ctx, is_global, dry_run)
        results.append(result)

    return results


def _get_cursor_global_hook_path() -> Path:
    """Get the Cursor global hook configuration path.

    Returns:
        Path object for the global hook config
    """
    config = CursorConfig(is_global=True)
    return config.get_default_hook_config_path()


def _install_windsurf_hook_in_repo(
    repo_path: Path, dry_run: bool
) -> list[InstallResult]:
    """Install Windsurf hook in a specific repository.

    Args:
        repo_path: Path to the repository (unused but required by interface)
        dry_run: Whether this is a dry run

    Returns:
        List of InstallResult objects for each hook
    """
    try:
        return _windsurf_impl(is_global=False, dry_run=dry_run)
    except SystemExit:
        return [InstallResult(InstallStatus.FAILED, "Windsurf hook", "Failed")]


def _windsurf_impl(is_global: bool, dry_run: bool = False) -> list[InstallResult]:
    """Implementation of Windsurf hook installation.

    Args:
        is_global: Whether to install globally
        dry_run: Whether to show what would be done without making changes

    Returns:
        List of InstallResult objects for each hook
    """
    return [_hook_install_impl(_WINDSURF_HOOK_CONTEXT, is_global, dry_run)]


def _get_windsurf_global_hook_path() -> Path:
    """Get the Windsurf global hook configuration path.

    Returns:
        Path object for the global hook config
    """
    config = WindsurfConfig(is_global=True)
    return config.get_default_hook_config_path()


# ============================================================================
# Kiro Hook Installation
# ============================================================================

# Kiro hook file format - discovered via experimentation on 2025-12-26
# See: https://kiro.dev/docs/hooks/types/
# See: https://kiro.dev/changelog/web-tools-subagents-contextual-hooks-and-per-file-code-review/
#
# Kiro uses individual .hook files in .kiro/hooks/ directory, not a single hooks.json.
# Each hook is a separate JSON file with the format:
# {
#   "enabled": true,
#   "name": "Hook Name",
#   "description": "Description",
#   "version": "1",
#   "when": {"type": "agentStart" | "agentEnd"},
#   "then": {"type": "runCommand", "command": "..."}
# }


def _create_kiro_hook_file(hook_type: str) -> dict:
    """Create Kiro hook configuration for agentStart or agentEnd.

    Args:
        hook_type: Either "agentStart" or "agentEnd"

    Returns:
        Dictionary with Kiro hook configuration
    """
    if hook_type == "agentStart":
        return {
            "enabled": True,
            "name": "Zenable MCP Hook on Agent Start",
            "description": "Captures checkpoint state when an agent loop starts",
            "version": "1",
            "when": {"type": "agentStart"},
            "then": {"type": "runCommand", "command": "uvx zenable-mcp@latest hook"},
        }
    else:  # agentEnd
        return {
            "enabled": True,
            "name": "Zenable MCP Hook on Agent End",
            "description": "Runs conformance check when an agent loop ends",
            "version": "1",
            "when": {"type": "agentEnd"},
            "then": {"type": "runCommand", "command": "uvx zenable-mcp@latest hook"},
        }


def _kiro_impl(is_global: bool, dry_run: bool = False) -> list[InstallResult]:
    """Implementation of Kiro hook installation.

    Kiro hooks are individual .hook files in .kiro/hooks/ directory.
    We install two hooks: agentStart (checkpoint) and agentEnd (conformance check).

    Note: Kiro only supports project-level hooks, not global hooks.
    Hook event names discovered via experimentation on 2025-12-26.

    Args:
        is_global: Whether to install globally (not supported for Kiro)
        dry_run: Whether to show what would be done without making changes

    Returns:
        List of InstallResult objects for each hook
    """
    results = []

    # Kiro only supports project-level hooks
    if is_global:
        echo("Kiro only supports project-level hooks, not global hooks", err=True)
        return [
            InstallResult(
                InstallStatus.FAILED,
                "Kiro hooks",
                "Global hooks not supported - use project installation",
            )
        ]

    # Get git root for project hooks
    git_root = find_git_root()
    if not git_root:
        echo(
            "Not in a git repository.\n"
            "Kiro hooks require project-level installation in a git repository.",
            err=True,
        )
        return [
            InstallResult(
                InstallStatus.FAILED,
                "Kiro hooks",
                "Not in a git repository",
            )
        ]

    hooks_dir = git_root / ".kiro" / "hooks"

    # Create hooks directory if needed
    if not dry_run:
        hooks_dir.mkdir(parents=True, exist_ok=True)

    # Install both hooks
    for hook_type in ["agentStart", "agentEnd"]:
        hook_filename = f"zenable-{hook_type.lower()}.hook"
        hook_path = hooks_dir / hook_filename
        hook_config = _create_kiro_hook_file(hook_type)
        hook_display_name = f"Kiro {hook_type} hook"

        # Check if hook already exists with same content
        if hook_path.exists():
            try:
                existing_config, _ = load_json_config(hook_path)
                if existing_config == hook_config:
                    echo(
                        f"{hook_display_name} already properly installed at {hook_path}",
                        persona=Persona.POWER_USER,
                    )
                    results.append(
                        InstallResult(
                            InstallStatus.ALREADY_INSTALLED,
                            hook_display_name,
                            "Hook already installed - no changes needed",
                        )
                    )
                    continue
                else:
                    # Existing hook has different config - check if it's our hook
                    existing_name = existing_config.get("name", "")
                    if "Zenable" in existing_name:
                        echo(
                            f"Updating existing {hook_display_name} at {hook_path}",
                            persona=Persona.POWER_USER,
                        )
                    else:
                        echo(
                            f"Found non-Zenable hook at {hook_path}, skipping",
                            persona=Persona.POWER_USER,
                        )
                        results.append(
                            InstallResult(
                                InstallStatus.SKIPPED,
                                hook_display_name,
                                "Non-Zenable hook exists at path",
                            )
                        )
                        continue
            except Exception as e:
                echo(
                    f"Error reading existing hook at {hook_path}: {e}",
                    persona=Persona.DEVELOPER,
                    err=True,
                )

        # Write the hook file
        if not dry_run:
            try:
                safe_write_json(hook_path, hook_config)
                echo(
                    f"Installed {hook_display_name} at {hook_path}",
                    persona=Persona.POWER_USER,
                )
                results.append(
                    InstallResult(
                        InstallStatus.SUCCESS,
                        hook_display_name,
                        f"Hook installed at {hook_path}",
                    )
                )
            except Exception as e:
                echo(f"Error writing hook file: {e}", err=True)
                results.append(
                    InstallResult(
                        InstallStatus.FAILED,
                        hook_display_name,
                        f"Error: {e}",
                    )
                )
        else:
            # Dry run
            if hook_path.exists():
                echo(f"Would update: {hook_path}", persona=Persona.POWER_USER)
            else:
                echo(f"Would create: {hook_path}", persona=Persona.POWER_USER)
            results.append(
                InstallResult(
                    InstallStatus.SUCCESS,
                    hook_display_name,
                    f"Would install at {hook_path}",
                )
            )

    return results


# ============================================================================
# Hook Implementation Registry
# ============================================================================

# Map tool names to their hook implementation functions
_HOOK_IMPLEMENTATIONS = {
    "claude-code": _claude_impl,
    "cursor": _cursor_impl,
    "windsurf": _windsurf_impl,
    "kiro": _kiro_impl,
}


# Common options decorator for hook subcommands
def _common_hook_options(f):
    """Decorator to add common options to all hook subcommands."""
    f = click.option(
        "--global",
        "-g",
        "is_global",
        is_flag=True,
        default=False,
        help=f"Install globally in {_get_claude_global_hook_path()}",
    )(f)
    f = click.option(
        "--dry-run",
        is_flag=True,
        default=False,
        help="Preview what would be done without actually performing the installation",
    )(f)
    f = click.option(
        "--include",
        multiple=True,
        help="Include only directories matching these glob patterns (e.g., '**/microservice-*')",
    )(f)
    f = click.option(
        "--exclude",
        multiple=True,
        help="Exclude directories matching these glob patterns",
    )(f)
    return f


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be done without actually performing the installation",
)
@click.option(
    "--include",
    multiple=True,
    help="Include only directories matching these glob patterns (e.g., '**/microservice-*')",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Exclude directories matching these glob patterns",
)
@click.pass_context
@log_command
def hook(ctx, dry_run, include, exclude):
    """Install hooks for various tools.

    \b
    Examples:
      # Install all hooks (default)
      zenable-mcp install hook
      zenable-mcp install hook all
    \b
      # Install Claude hook specifically
      zenable-mcp install hook claude
    \b
      # Preview what would be installed
      zenable-mcp install hook --dry-run
      zenable-mcp install hook claude-code --dry-run

    \b
    For more information, visit:
    https://docs.zenable.io/integrations/mcp/hooks
    """
    # Note: --include and --exclude filters can be used

    # Initialize recursive - it will be set by repo selection if needed
    recursive = get_recursive_from_context(ctx) if ctx.parent else False

    # Store dry_run and patterns in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["recursive"] = recursive
    ctx.obj["include_patterns"] = list(include) if include else None
    ctx.obj["exclude_patterns"] = list(exclude) if exclude else None

    # Pass through git_repos from parent context if available
    if ctx.parent and ctx.parent.obj and "git_repos" in ctx.parent.obj:
        ctx.obj["git_repos"] = ctx.parent.obj["git_repos"]

    # Check if we're in a git repo for non-recursive installs
    # Only do repo discovery if no subcommand will be invoked
    # (subcommands handle their own logic, including from unified commands)
    if not recursive and ctx.invoked_subcommand is None:
        git_root = find_git_root()
        if not git_root:
            # Not in a git repo, prompt for repository selection with filters
            include_patterns, exclude_patterns = get_patterns_from_context(
                include, exclude, ctx
            )

            selected = prompt_for_repository_selection(
                max_repos_to_show=100,
                allow_all=True,
                allow_global=False,  # Hook command doesn't support global at group level
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
            )

            recursive, _ = handle_repository_selection(selected, ctx)
            if selected is None:
                # User cancelled
                sys.exit(ExitCode.SUCCESS)

    # If no subcommand is provided, default to 'all'
    if ctx.invoked_subcommand is None:
        # Get parent's recursive flag if available
        if not recursive and ctx.parent and ctx.parent.obj:
            recursive = ctx.parent.obj.get("recursive", False)
        # Get is_global from parent context
        is_global = get_is_global_from_context(ctx)
        ctx.invoke(
            all_hooks,
            is_global=is_global,
            dry_run=dry_run,
            include=include,
            exclude=exclude,
        )


@hook.command(name="all")
@_common_hook_options
@click.pass_context
@log_command
def all_hooks(ctx, is_global, dry_run, include, exclude):
    """Install hooks for all supported tools."""

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    # Get recursive from context (set by parent or repo selection)
    recursive = get_recursive_from_context(ctx)

    # Check if we're being called from parent install command
    from_parent_install = ctx.obj and ctx.obj.get("from_parent_install", False)

    if recursive:
        # Run recursively in all git repositories

        # Get repos from context using helper
        git_repos = get_git_repos_from_context(ctx)

        # If still not found, find them now
        if git_repos is None:
            git_repos = find_git_repositories()
            if ctx.obj:
                ctx.obj["git_repos"] = git_repos

        # Get patterns from context if not explicitly provided
        include_patterns, exclude_patterns = get_patterns_from_context(
            include, exclude, ctx
        )

        # Apply filtering if patterns are provided
        original_count = len(git_repos)
        filter_result = filter_git_repositories(
            git_repos,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            handler_name="recursive hook install",
        )
        git_repos = filter_result.filtered_repos

        if not from_parent_install:
            # Check if all repositories were filtered out
            if (include_patterns or exclude_patterns) and len(git_repos) == 0:
                show_filtering_results(
                    filter_result.original_count,
                    include_patterns=include_patterns,
                    exclude_patterns=exclude_patterns,
                )
                return ExitCode.SUCCESS

            # Check if we should suppress repo list (when called from unified command)
            suppress_repo_list = get_flag_from_context(ctx, "suppress_repo_list")

            # Check if confirmation was already done (by TUI or previous command in unified flow)
            skip_confirmation = get_flag_from_context(ctx, "confirmation_done")

            # Show complete filtering information
            if not show_complete_filtering_information(
                git_repos,
                original_count,
                include_patterns or exclude_patterns,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                dry_run=dry_run,
                suppress_repo_list=suppress_repo_list,
                skip_confirmation=skip_confirmation,
            ):
                return ExitCode.SUCCESS
        elif not from_parent_install and not (include_patterns or exclude_patterns):
            # Only print if not called from parent and no filtering
            # Show simple count without full filtering report
            repo_text = "repository" if len(git_repos) == 1 else "repositories"
            echo(f"\nFound {len(git_repos)} git {repo_text}")

        if not git_repos:
            if not from_parent_install and not (include_patterns or exclude_patterns):
                # Only show message if not filtered (filtering messages shown above)
                echo("No git repositories found in the current directory or below.")
            return OperationStatus.NO_FILES_FOUND

        # Execute the operation across all repositories
        all_results = execute_in_git_repositories(
            operation_func=_install_claude_hook_in_repo,
            operation_name="Claude Code hook",
            dry_run=dry_run,
            git_repos=git_repos,  # Use already-found repositories
        )

        # If called from parent, return results for aggregation
        if from_parent_install:
            return all_results

        # Show summary
        show_installation_summary(
            all_results, dry_run, "Hooks Installation", repositories=git_repos
        )

        # Return appropriate exit code
        return get_exit_code(all_results)
    else:
        # Get patterns from context if not explicitly provided
        include_patterns, exclude_patterns = get_patterns_from_context(
            include, exclude, ctx
        )

        # Check if we have filters and we're in a single repo
        if (include_patterns or exclude_patterns) and not is_global:
            # Get the current git repo if we're in one
            git_root = find_git_root()
            if git_root:
                # Apply filters to the single repo
                filter_result = filter_git_repositories(
                    [git_root],
                    include_patterns=include_patterns,
                    exclude_patterns=exclude_patterns,
                    handler_name="install hook",
                )

                if len(filter_result.filtered_repos) == 0:
                    # Current repo doesn't match filters, skip installation
                    show_filtering_results(
                        filter_result.original_count,
                        include_patterns=include_patterns,
                        exclude_patterns=exclude_patterns,
                    )
                    return ExitCode.SUCCESS

        # Execute the logic - currently only Claude Code is supported
        results: list[InstallResult] = []

        try:
            # Currently only Claude Code is supported
            hook_results = _claude_impl(is_global, dry_run)
            results.extend(hook_results)
        except SystemExit:
            if not from_parent_install:
                echo(
                    "Error: Unknown issue while installing the Claude Code hook, please report this at zenable.io/feedback",
                    err=True,
                )
            results.append(
                InstallResult(InstallStatus.FAILED, "Claude Code hook", "Failed")
            )

    # If called from parent, return results for aggregation
    if from_parent_install:
        return results

    # In dry-run mode, display file operations
    if dry_run and any(r.status == InstallStatus.SUCCESS for r in results):
        settings_path = get_hook_settings_path(
            _CLAUDE_USER_PROMPT_SUBMIT_CONTEXT, is_global
        )
        if settings_path.exists():
            echo(f"\n{click.style('Would modify:', fg='cyan', bold=True)}")
            echo(f"  • {settings_path}")
        else:
            echo(f"\n{click.style('Would create:', fg='cyan', bold=True)}")
            echo(f"  • {settings_path}")

    # Show summary
    show_installation_summary(results, dry_run, "Hooks Installation")

    # In dry-run mode, show preview message
    if dry_run and any(r.is_success for r in results):
        echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )

    # Return appropriate exit code
    return get_exit_code(results)


# Auto-generate hook commands for all tools
# This replaces manual command definitions with dynamic generation
attach_hook_commands(hook, _HOOK_IMPLEMENTATIONS, _common_hook_options, all_hooks)
