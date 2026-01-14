"""Hook command for IDE integrations (Claude Code, etc.)."""

import asyncio
import json
import sys
import time
from pathlib import Path

import click

from zenable_mcp.exceptions import (
    APIError,
    AuthenticationError,
    AuthenticationTimeoutError,
)
from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.hook_input_handlers import InputHandlerRegistry
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.usage.manager import record_command_usage
from zenable_mcp.user_config.config_handler_factory import get_config_handler
from zenable_mcp.utils.experimental import log_experimental_mode_warning
from zenable_mcp.utils.files import filter_files_by_patterns, get_file_content
from zenable_mcp.utils.mcp_client import ZenableMCPClient, parse_conformance_results
from zenable_mcp.utils.zenable_config import filter_files_by_zenable_config


def process_hook_input(input_context, active_handler) -> tuple[list[Path], str | None]:
    """
    Process files from input handlers (hooks).

    Returns:
        Tuple of (file_paths, file_content_from_handler)
    """
    handler_files = input_context.files
    if not handler_files:
        echo(
            f"No files to process from {active_handler.name}", persona=Persona.DEVELOPER
        )
        return [], None

    # Check if we have file content (e.g., from Write tool)
    file_content_from_handler = None
    if input_context.metadata.get("file_content"):
        file_content_from_handler = input_context.metadata["file_content"]

    tool_name = input_context.metadata.get("tool_name", "Unknown")
    for fp in handler_files:
        echo(
            f"Using file from {active_handler.name} {tool_name} hook: {fp}",
            persona=Persona.DEVELOPER,
        )

    return handler_files, file_content_from_handler


@click.command()
@click.pass_context
def hook(ctx):
    """Handle calls from the hooks of Agentic IDEs

    This command is specifically designed for IDE integrations like Claude Code.
    It reads hook input from stdin, processes the files, and returns appropriate
    exit codes and formatted responses for the IDE to handle.

    To manually run a scan, use the 'check' command instead.
    """
    # Initialize input handler registry with auto-registration
    registry = InputHandlerRegistry()

    # Detect and parse input using the registry
    try:
        input_context = registry.detect_and_parse()
    except RuntimeError as e:
        # Multiple handlers claiming they can handle - exit with non-2 exit code
        echo(
            "Unknown failure, please report this at zenable.io/feedback",
            err=True,
            log=True,
        )
        echo(f"Error details: {e}", persona=Persona.DEVELOPER, err=True, log=True)
        sys.exit(ExitCode.HANDLER_CONFLICT)

    if not input_context:
        echo(
            "Error: No hook input detected. This command is for IDE hooks only.",
            err=True,
        )
        echo("To manually run a scan, use zenable-mcp check", err=True)
        sys.exit(ExitCode.NO_HOOK_INPUT)

    # Get the active handler after confirming input_context exists
    active_handler = registry.get_active_handler()
    hook_event = input_context.metadata.get("hook_event_name") or "<UNKNOWN EVENT>"
    echo(
        f"Handling {active_handler.name} {hook_event} hook",
        persona=Persona.POWER_USER,
    )

    # Log experimental mode warning if enabled
    log_experimental_mode_warning()

    if input_context.raw_data:
        echo(json.dumps(input_context.raw_data, indent=2), persona=Persona.DEVELOPER)

    # Early exit for checkpoint-only hooks - no conformance check needed
    # These hooks just save checkpoint state and return immediately
    if active_handler.is_checkpoint_only_event(input_context):
        echo(
            f"Handling {active_handler.name} hook: Checkpoint saved for {hook_event}, continuing",
            persona=Persona.DEVELOPER,
            log=True,
        )
        output_config = active_handler.get_output_config()
        response = active_handler.build_response_to_hook_call(False, "")
        if response:
            echo(response, err=output_config.response_to_stderr, log=True)
        echo(
            f"Handling {active_handler.name} hook: Responding to {hook_event} with exit_code=0",
            persona=Persona.POWER_USER,
        )
        sys.exit(ExitCode.SUCCESS)

    # Load configuration to get patterns for filtering
    config_patterns = None
    config_exclude_patterns = None
    try:
        config_handler = get_config_handler()
        config, error = config_handler.load_config()

        if error:
            # This error is meant to be user facing; more debug details are logged inside of load_config()
            # Send to stderr to avoid confusing IDEs that may try to parse stdout as JSON
            echo(error, err=True)

        # Get check patterns from config if available
        if hasattr(config, "check") and config.check:
            config_patterns = getattr(config.check, "patterns", None)
            config_exclude_patterns = getattr(config.check, "exclude_patterns", None)
    except AuthenticationTimeoutError as e:
        # OAuth flow timed out - user didn't complete login in browser
        echo(str(e), err=True)
        sys.exit(ExitCode.AUTHENTICATION_ERROR)
    except AuthenticationError as e:
        echo(
            f"Authentication required: {e}",
            err=True,
            log=True,
        )
        echo(
            "Please run 'zenable-mcp check' to authenticate via OAuth.",
            err=True,
        )
    except Exception as e:
        echo(
            "Unknown failure loading config, please report this at zenable.io/feedback",
            err=True,
            log=True,
        )
        echo(f"Error loading config: {e}", persona=Persona.DEVELOPER)

    # Process hook input to get files
    # Note: We ignore the file content from the handler and read files ourselves below
    file_paths, _ = process_hook_input(input_context, active_handler)

    # Get output configuration for this handler
    output_config = active_handler.get_output_config()

    echo(
        f"Handling {active_handler.name} {hook_event} hook: Received {len(file_paths)} file(s) from handler",
        persona=Persona.DEVELOPER,
        log=True,
    )

    if not file_paths:
        # No files to check
        echo(
            f"Handling {active_handler.name} {hook_event} hook: No files from handler, skipping review",
            persona=Persona.DEVELOPER,
            log=True,
        )
        response = active_handler.build_response_to_hook_call(False, "")
        if response:
            echo(response, err=output_config.response_to_stderr, log=True)
        sys.exit(ExitCode.SUCCESS)

    # Apply pattern filtering if we have config patterns
    if config_patterns or config_exclude_patterns:
        files_before = len(file_paths)
        file_paths = filter_files_by_patterns(
            file_paths,
            patterns=config_patterns,
            exclude_patterns=config_exclude_patterns,
            handler_name=active_handler.name,
        )
        echo(
            f"Handling {active_handler.name} {hook_event} hook: Pattern filter {files_before} -> {len(file_paths)} file(s)",
            persona=Persona.DEVELOPER,
            log=True,
        )

        if not file_paths:
            # All files filtered out
            echo(
                f"Handling {active_handler.name} {hook_event} hook: All files filtered by patterns, skipping review",
                persona=Persona.DEVELOPER,
                log=True,
            )
            response = active_handler.build_response_to_hook_call(False, "")
            if response:
                echo(response, err=output_config.response_to_stderr, log=True)
            sys.exit(ExitCode.SUCCESS)

    # Apply zenable config filtering
    files_before = len(file_paths)
    try:
        file_paths = filter_files_by_zenable_config(file_paths)
    except AuthenticationTimeoutError as e:
        # OAuth flow timed out - user didn't complete login in browser
        echo(str(e), err=True)
        sys.exit(ExitCode.AUTHENTICATION_ERROR)
    echo(
        f"Handling {active_handler.name} {hook_event} hook: Config filter {files_before} -> {len(file_paths)} file(s)",
        persona=Persona.DEVELOPER,
        log=True,
    )

    if not file_paths:
        # All files filtered out by zenable config
        echo(
            f"Handling {active_handler.name} {hook_event} hook: All files filtered by config, skipping review",
            persona=Persona.DEVELOPER,
            log=True,
        )
        response = active_handler.build_response_to_hook_call(False, "")
        if response:
            echo(response, err=output_config.response_to_stderr, log=True)
        echo(
            f"Handling {active_handler.name} hook: Responding to {hook_event} with exit_code=0",
            persona=Persona.POWER_USER,
        )
        sys.exit(ExitCode.SUCCESS)

    # Log files identified for review
    echo(
        f"Handling {active_handler.name} {hook_event} hook: Reviewing {len(file_paths)} file(s)",
        persona=Persona.POWER_USER,
        log=True,
    )
    # Log individual files at DEVELOPER level for debugging
    for fp in file_paths:
        echo(f"  - {fp}", persona=Persona.DEVELOPER, log=True)

    # Read file contents
    files = []

    # Loop through all files and handle them consistently
    for file_path in file_paths:
        try:
            content = get_file_content(file_path)
            files.append({"path": str(file_path), "content": content})
        except Exception as e:
            echo(
                f"Error reading {file_path}: {e}",
                persona=Persona.POWER_USER,
                err=True,
                log=True,
            )
            continue

    if not files:
        echo("Error: No files could be read", err=True, log=True)
        sys.exit(ExitCode.FILE_READ_ERROR)

    async def check_files():
        # Track command duration
        start_time_ns = time.perf_counter_ns()

        # Build file metadata for LOC tracking
        file_metadata = {}
        for file_dict in files:
            file_path = file_dict["path"]
            content = file_dict["content"]
            file_metadata[file_path] = {
                "loc": len(content.splitlines()),
            }

        # Variables to track for usage recording
        loc = 0
        finding_suggestion = 0
        error: Exception | None = None

        # Progress callback for batch logging (only log if multiple files)
        total_files = len(files)

        def on_batch_progress(files_reviewed: int, total: int) -> None:
            if total > 1:
                echo(
                    f"Handling {active_handler.name} {hook_event} hook: Reviewed {files_reviewed}/{total} file(s)",
                    persona=Persona.POWER_USER,
                    log=True,
                )

        try:
            async with ZenableMCPClient() as client:
                # Process files in batches of 5 (same as check command)
                # Use JSON format to get structured response with authoritative pass/fail status
                results = await client.check_conformance(
                    files,
                    batch_size=5,
                    show_progress=False,
                    format="json",
                    progress_callback=on_batch_progress if total_files > 1 else None,
                )

                # Parse results into structured ConformanceReport
                # This handles both JSON and text format responses properly
                report = parse_conformance_results(results, file_metadata=file_metadata)

                echo(
                    f"Results from check_conformance: {len(results)} batch(es)",
                    persona=Persona.DEVELOPER,
                    log=True,
                )
                echo(
                    f"Parsed report: {report.total_findings} finding(s), {report.total_loc} LOC, status={report.overall_status.value}",
                    persona=Persona.DEVELOPER,
                    log=True,
                )

                # Check for API errors across ALL batches (not just the first)
                error_messages = report.get_error_messages()
                if error_messages:
                    # Combine all error messages and raise
                    raise Exception("; ".join(error_messages))

                # Use ConformanceReport's aggregated status across all batches
                # This is the single source of truth for findings status
                has_findings = report.has_findings
                findings_text = report.to_findings_text()

                # Add credit warning to findings text if applicable
                if report.has_insufficient_credits:
                    credit_warning = (
                        f"[INSUFFICIENT CREDITS] Ran {report.total_checks_run} checks, "
                        f"{report.total_checks_skipped} skipped due to insufficient credits. "
                        "Consider upgrading: zenable.io/pricing"
                    )
                    if findings_text:
                        findings_text = f"{credit_warning}\n\n{findings_text}"
                    else:
                        findings_text = credit_warning

                # Insufficient credits is informational only, doesn't affect exit code
                has_issues = has_findings

                echo(
                    f"has_findings (from ConformanceReport): {has_findings}",
                    persona=Persona.DEVELOPER,
                    log=True,
                )
                echo(
                    f"has_insufficient_credits: {report.has_insufficient_credits}",
                    persona=Persona.DEVELOPER,
                    log=True,
                )
                echo(
                    f"findings_text length: {len(findings_text)}",
                    persona=Persona.DEVELOPER,
                    log=True,
                )

                # Build handler-specific response
                # Pass has_issues to include credit warning in response even when no findings
                formatted_response = active_handler.build_response_to_hook_call(
                    has_issues, findings_text
                )
                if formatted_response:
                    # Output response using handler's output config
                    echo(
                        f"Writing formatted response (stderr={output_config.response_to_stderr})",
                        persona=Persona.DEVELOPER,
                    )
                    echo(
                        formatted_response,
                        err=output_config.response_to_stderr,
                        log=True,
                    )
                    echo("Finished writing response", persona=Persona.DEVELOPER)

                # Store values for usage tracking in finally block
                loc = report.total_loc
                finding_suggestion = report.total_findings

                # Use handler-specific exit code (has_issues includes insufficient credits)
                exit_code = active_handler.get_exit_code(has_issues)

                # Log clear summary of what we're sending to the IDE
                findings_summary = (
                    f"{report.total_findings} finding(s)"
                    if has_findings
                    else "no findings"
                )
                if report.has_insufficient_credits:
                    findings_summary += f", {report.total_checks_skipped} check(s) skipped (insufficient credits)"
                echo(
                    f"Handling {active_handler.name} {hook_event} hook: Completed review of {len(files)} file(s), {findings_summary}",
                    persona=Persona.POWER_USER,
                )
                echo(
                    f"Handling {active_handler.name} {hook_event} hook: Responding with exit_code={exit_code}",
                    persona=Persona.POWER_USER,
                )

                # Even though we continue doing work in the finally block we will exit with this exit code
                sys.exit(exit_code)

        except APIError as e:
            # Connection errors are already logged by the MCP client
            error = e
            sys.exit(ExitCode.API_ERROR)
        except Exception as e:
            echo(f"Error: {e}", err=True, log=True)
            error = e
            sys.exit(ExitCode.API_ERROR)
        finally:
            # Calculate duration and track usage
            duration_ms = (time.perf_counter_ns() - start_time_ns) // 1_000_000
            record_command_usage(
                ctx=ctx,
                duration_ms=duration_ms,
                loc=loc,
                finding_suggestion=finding_suggestion,
                error=error,
            )

    asyncio.run(check_files())
