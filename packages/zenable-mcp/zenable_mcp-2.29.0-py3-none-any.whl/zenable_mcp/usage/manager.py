"""Usage data management for zenable_mcp commands."""

import asyncio
import json
import os
import sqlite3
from datetime import datetime, timezone
from http.client import HTTPException

import click
import jwt
import requests

from zenable_mcp import __version__
from zenable_mcp.constants import OAUTH_TOKEN_CACHE_DIR
from zenable_mcp.exceptions import AuthenticationTimeoutError, HookInputStructureError
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.usage.fingerprint import get_system_fingerprint
from zenable_mcp.usage.models import (
    UsageEventData,
    ZenableMcpUsagePayload,
)
from zenable_mcp.usage.sender import send_usage_data
from zenable_mcp.utils.install_status import InstallResult
from zenable_mcp.utils.mcp_client import ZenableMCPClient

# Base Zenable URL (override with ZENABLE_URL env var)
_zenable_url = os.environ.get("ZENABLE_URL", "https://www.zenable.app").rstrip("/")

# Private usage API endpoint
_usage_api = f"{_zenable_url}/api/data/usage"

# Timeout for authenticated usage requests (in seconds)
AUTH_REQUEST_TIMEOUT = 5


def is_usage_enabled() -> bool:
    """
    Check if usage data collection is enabled.

    Returns:
        True if usage data collection is enabled, False if disabled via environment variable
    """
    return os.environ.get("ZENABLE_DISABLE_USAGE_TRACKING", "").lower() not in (
        "1",
        "true",
        "yes",
    )


async def _refresh_oauth_token() -> bool:
    """
    Trigger OAuth flow to get a fresh token.

    This will open a browser for user authentication if needed.
    The fresh token will be stored in the OAuth cache.

    Returns:
        True if OAuth flow succeeded, False otherwise

    Raises:
        AuthenticationTimeoutError: If OAuth flow times out waiting for user
    """
    try:
        echo(
            "Refreshing OAuth token...",
            persona=Persona.POWER_USER,
        )

        # Create MCP client - this triggers OAuth flow
        # Just connecting is enough to refresh the token (OAuth flow happens in __aenter__)
        async with ZenableMCPClient():
            echo(
                "OAuth token refreshed successfully",
                persona=Persona.DEVELOPER,
            )
            return True

    except Exception as e:
        echo(
            f"Failed to refresh OAuth token: {type(e).__name__}",
            persona=Persona.DEVELOPER,
            err=True,
        )
        # Any failure during OAuth refresh means user needs to complete login
        # - If timeout: user didn't complete browser auth
        # - If connection failed: OAuth callback didn't complete
        # - If server down: user can't login anyway
        # In all cases, "run uvx zenable-mcp login" is the right message
        raise AuthenticationTimeoutError() from e


def refresh_oauth_token() -> bool:
    """
    Synchronous wrapper for OAuth token refresh.

    Triggers the OAuth flow (opens browser) to get a fresh token.

    Returns:
        True if OAuth flow succeeded, False otherwise

    Raises:
        AuthenticationTimeoutError: If OAuth flow times out waiting for user
    """
    try:
        return asyncio.run(_refresh_oauth_token())
    except AuthenticationTimeoutError:
        # Propagate timeout errors so callers can handle them specifically
        raise
    except Exception:
        return False


def _is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired by decoding and checking the exp claim.

    Uses PyJWT to decode the token without signature verification and
    checks the exp claim. PyJWT handles the expiration check automatically.

    Note: We skip signature verification here because we're only checking
    if the cached token needs refresh - the token will be validated by
    the server when actually used.

    Args:
        token: JWT token string

    Returns:
        True if token is expired, False otherwise
    """
    try:
        # Decode without signature verification - we just want to check expiration
        # PyJWT will raise ExpiredSignatureError if token is expired
        # nosemgrep: github.policy.rules.insecure-jwt-decode-no-signature-verification
        jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": True,
                "verify_aud": False,
            },
        )
        return False
    except jwt.ExpiredSignatureError:
        return True
    except jwt.DecodeError:
        # Can't decode - treat as expired to be safe
        return True
    except Exception:
        # Any other error - assume valid to avoid blocking
        return False


def _get_jwt_token_from_cache() -> str | None:
    """
    Extract JWT token from OAuth cache if available and not expired.

    FastMCP stores tokens in SQLite database (cache.db) with structure:
    - Table: Cache
    - Key format: "mcp-oauth-token::<url>"
    - Value: JSON blob with {"value": {"access_token": "...", ...}}

    Returns:
        JWT token string if available and not expired, None otherwise
    """
    try:
        # Check OAuth cache directory
        if not OAUTH_TOKEN_CACHE_DIR.exists():
            return None

        # Try SQLite database (current FastMCP format)
        cache_db = OAUTH_TOKEN_CACHE_DIR / "cache.db"
        if cache_db.exists():
            try:
                with sqlite3.connect(str(cache_db)) as conn:
                    cursor = conn.cursor()

                    # Query for OAuth token entries
                    # FastMCP stores tokens with key pattern "mcp-oauth-token::<url>"
                    cursor.execute(
                        "SELECT value FROM Cache WHERE key LIKE 'mcp-oauth-token::%'"
                    )
                    rows = cursor.fetchall()

                    for (value_blob,) in rows:
                        try:
                            # Value is stored as JSON blob
                            token_data = json.loads(value_blob)

                            # FastMCP structure: {"value": {"access_token": "...", "id_token": "...", ...}}
                            if "value" in token_data:
                                token_value = token_data["value"]
                                # Only use access_token, never id_token
                                # id_token cannot be used to call Auth0 /userinfo endpoint
                                # which is required during tenant onboarding in data_api
                                access_token = token_value.get("access_token")

                                if access_token:
                                    # Check if token is expired using JWT exp claim
                                    if _is_token_expired(access_token):
                                        echo(
                                            "OAuth token is expired.",
                                            persona=Persona.DEVELOPER,
                                            err=True,
                                        )
                                        continue
                                    return access_token

                                # Log if id_token exists but access_token doesn't
                                # This helps diagnose OAuth configuration issues
                                if token_value.get("id_token"):
                                    echo(
                                        "OAuth cache has id_token but no access_token. "
                                        "This may indicate an Auth0 configuration issue.",
                                        persona=Persona.DEVELOPER,
                                        err=True,
                                    )

                        except (json.JSONDecodeError, KeyError, TypeError):
                            continue

            except sqlite3.Error:
                echo(
                    "Failed to extract authentication token from cache",
                    persona=Persona.DEVELOPER,
                    err=True,
                )
                return None

        return None

    except Exception:
        return None


def get_jwt_token_with_refresh() -> str | None:
    """
    Get JWT token from cache, refreshing via OAuth if needed.

    If no valid token exists in cache, triggers the OAuth flow
    (opens browser) to authenticate and get a fresh token.

    Returns:
        JWT token string if available, None if auth failed

    Raises:
        AuthenticationTimeoutError: If OAuth flow times out waiting for user
    """
    # First try to get token from cache
    token = _get_jwt_token_from_cache()
    if token:
        return token

    # No valid token - try to refresh via OAuth
    echo(
        "No valid OAuth token found. Opening browser to authenticate...",
        persona=Persona.POWER_USER,
    )

    # refresh_oauth_token() may raise AuthenticationTimeoutError - let it propagate
    if refresh_oauth_token():
        # OAuth succeeded - try to get token again
        return _get_jwt_token_from_cache()

    return None


def send_authenticated_usage(
    command_name: str,  # "check" or "hook"
    usage_data: dict,
    jwt_token: str | None,
) -> None:
    """
    Send usage data to authenticated data_api endpoint.

    Args:
        command_name: Command name ("check" or "hook")
        usage_data: Usage data dictionary
        jwt_token: JWT token from OAuth flow (if available)
    """
    if not jwt_token:
        return

    try:
        # Determine integration identifier
        integration = f"zenable_mcp/{command_name}"

        # Build request body
        request_body = {
            "integration": integration,
            "usage_data": usage_data,
        }

        # Send with JWT authentication
        response = requests.post(
            _usage_api,
            json=request_body,
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json",
            },
            timeout=AUTH_REQUEST_TIMEOUT,
        )

        # Log response (2xx = success)
        if 200 <= response.status_code < 300:
            echo(
                f"Authenticated usage data sent successfully (HTTP {response.status_code})",
                persona=Persona.DEVELOPER,
            )
        else:
            echo(
                f"Authenticated usage tracking failed: HTTP {response.status_code}",
                err=True,
                persona=Persona.DEVELOPER,
            )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        HTTPException,
        json.JSONDecodeError,
        Exception,
    ):
        pass


def extract_command_info(ctx: click.Context) -> tuple[str, dict[str, object]]:
    """
    Extract command name and arguments from click context.

    Args:
        ctx: Click context from command execution

    Returns:
        Tuple of (command_string, command_args_dict)
    """
    # Build command string from context
    command_parts = []
    current_ctx = ctx

    # Walk up the context chain to build full command
    while current_ctx:
        if current_ctx.info_name:
            command_parts.insert(0, current_ctx.info_name)
        current_ctx = current_ctx.parent

    command_string = " ".join(command_parts)

    # Extract command arguments (params) directly from Click context
    command_args: dict[str, object] = {}
    if ctx.params:
        for key, value in ctx.params.items():
            if value is not None:
                # Convert tuples to lists for JSON serialization
                if isinstance(value, tuple):
                    command_args[key] = list(value)
                else:
                    command_args[key] = value

    return command_string, command_args


def _map_command_to_activity_type(command_name: str) -> str:
    """Map command name to activity_type."""
    mapping = {
        "check": "check",
        "hook": "hook",
        "install": "install_mcp",  # will be more specific in the future
        "zenable-mcp": "help",  # Root command shows help
        "cli": "help",  # Alternative root command name
    }
    return mapping.get(command_name, command_name)


def _build_hook_structure_error_data(error: HookInputStructureError) -> dict:
    """Build error data for hook input structure errors.

    This captures metadata about unrecognized hook input formats
    so we can identify new IDE formats or format changes.

    Args:
        error: The HookInputStructureError that occurred

    Returns:
        Dict with error data for telemetry
    """
    return {
        "outcome": "failed",
        "decision": "no_files",  # No files were processed
        "filtering_stats": {
            "total_files": 0,
            "filtered_files": 0,
            "processed_files": 0,
        },
        "error_info": {
            "error_type": "hook_input_structure",
            "received_keys": error.received_keys,
            "hook_event_name": error.hook_event_name,
            "expected_patterns": error.expected_patterns,
            "message": str(error),
        },
    }


def _build_cli_parsing_error_data(
    error: click.exceptions.ClickException, activity_type: str
) -> dict | None:
    """Build minimal failure data for CLI parsing errors.

    Args:
        error: The Click exception that occurred
        activity_type: The activity type (install_mcp, check, hook, etc.)

    Returns:
        Dict with error data matching the schema, or None if not applicable
    """
    # Commands like doctor, version, logs don't require a data field
    # so we return None and let the schema validation handle it
    if activity_type in ["doctor", "version", "logs"]:
        return None

    # Determine specific error type from Click exception class
    error_type_name = type(error).__name__

    # Build error data based on activity type
    if activity_type == "install_mcp":
        return {
            "outcome": "failed",
            "results_by_ide": {},  # No IDEs attempted
            "stats": {
                "total_attempts": 0,
                "successful": 0,
                "already_installed": 0,
                "upgraded": 0,
                "failed": 1,  # One failure: the CLI parsing
                "capability_mismatch": 0,
            },
            "error_info": {
                "error_types": [
                    "cli_parsing_error",
                    error_type_name,
                ],  # Generic + specific
                "error_count": 1,
            },
        }
    elif activity_type == "check":
        return {
            "outcome": "failed",
            "zenable_mcp_version": __version__,
            # error_info omitted - CLI parsing errors don't fit the schema's error_type enum
            # The outcome="failed" and command_args are sufficient signal
        }
    elif activity_type == "hook":
        return {
            "outcome": "failed",
            "decision": "no_files",  # Closest semantic match - no files were processed
            "filtering_stats": {
                "total_files": 0,
                "filtered_files": 0,
                "processed_files": 0,
            },
            # error_info omitted - CLI parsing errors don't fit the schema's error_type enum
        }
    elif activity_type == "install_hook":
        return {
            "outcome": "failed",
            "hook_action": "no_change",  # Closest semantic match - nothing was changed
            # error_info omitted - CLI parsing errors don't fit the schema's error_type enum
        }

    # Unknown activity type - return None
    return None


def record_command_usage(
    ctx: click.Context,
    results: list[InstallResult] | None = None,
    duration_ms: int | None = None,
    error: Exception | None = None,
    **kwargs,
) -> None:
    """
    Record usage data for a zenable_mcp command.

    Sends usage data to the appropriate API endpoint:
    - check/hook commands WITH JWT → /api/data/usage (authenticated, includes detailed metrics)
    - check/hook commands WITHOUT JWT → /api/public/usage (anonymous tracking)
    - all other commands → /api/public/usage (anonymous: install, doctor, version, logs)

    Args:
        ctx: Click context from command execution
        results: Optional list of InstallResult objects from IDE operations
        duration_ms: Command execution duration in milliseconds
        error: Optional exception if command failed
        **kwargs: Additional data to include (e.g., loc, finding_suggestion, conformance metrics)
    """
    # Check if usage data collection is disabled
    if not is_usage_enabled():
        return

    try:
        # Get system fingerprint
        system_info, system_hash = get_system_fingerprint()

        # Extract command info
        command_string, command_args = extract_command_info(ctx)

        # Determine command name and activity type
        # Walk up context chain to find the top-level command (install, check, hook, etc.)
        # For subcommands like "install mcp", we want "install_mcp" not just "mcp" or "install"
        command_name = ctx.info_name  # Start with current command

        # If this is a subcommand (has a parent that's not the root), build the full command path
        # Top-level commands have the root "zenable-mcp" as their parent
        if ctx.parent and ctx.parent.parent and ctx.parent.info_name:
            # This is a subcommand (like "mcp" under "install" or "hook" under "install")
            # Build the full command name: "install_mcp" or "install_hook"
            parent_name = ctx.parent.info_name
            current_name = ctx.info_name
            # For install subcommands, create the full activity type
            if parent_name == "install":
                command_name = f"{parent_name}_{current_name}"
            else:
                command_name = parent_name

        activity_type = _map_command_to_activity_type(command_name)

        # Determine event type and outcome
        if error:
            event = "completed"  # still completed, just with error
            error_message = str(error)
        else:
            event = "completed"
            error_message = None

        # Default duration if not provided
        if duration_ms is None:
            duration_ms = 0

        # Determine which endpoint to use based on command type
        is_check_or_hook = command_name in ["check", "hook"]

        # Skip usage tracking entirely if auth already failed - can't track without auth
        if isinstance(error, AuthenticationTimeoutError):
            return

        # Get JWT token for authenticated endpoints (with OAuth refresh if needed)
        jwt_token = get_jwt_token_with_refresh() if is_check_or_hook else None

        # 1. Send to authenticated data_api endpoint (for check/hook WITH JWT only)
        if is_check_or_hook and jwt_token:
            # Build legacy format for authenticated endpoint
            usage_data = {
                "command": command_string,
                "command_args": command_args,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": error is None,
                "error_message": error_message,
                "zenable_mcp_version": __version__,
                "duration_ms": duration_ms,
                "loc": kwargs.get("loc", 0),
                "finding_suggestion": kwargs.get("finding_suggestion", 0),
            }

            # Add metrics
            for metric in [
                "passed_checks",
                "failed_checks",
                "warning_checks",
                "total_checks_run",
                "total_files_checked",
            ]:
                if metric in kwargs:
                    usage_data[metric] = kwargs[metric]

            send_authenticated_usage(command_name, usage_data, jwt_token)

        # 2. Send to public API for all other cases:
        #    - check/hook WITHOUT JWT (anonymous usage tracking)
        #    - install, doctor, version, logs (always anonymous)
        else:
            # Build error-specific data for telemetry
            event_data = None

            # For HookInputStructureError, include detailed metadata about the unknown format
            # This helps us identify new IDE formats or format changes
            if error and isinstance(error, HookInputStructureError):
                event_data = _build_hook_structure_error_data(error)
                echo(
                    f"Tracking hook input structure error: {error.received_keys}",
                    persona=Persona.DEVELOPER,
                )
            # For Click exceptions (CLI parsing errors), build minimal error data
            # This tracks UX issues like typos in flags (e.g., --helpo instead of --help)
            elif error and isinstance(error, click.exceptions.ClickException):
                event_data = _build_cli_parsing_error_data(error, activity_type)
                echo(
                    f"Tracking CLI parsing error: {type(error).__name__}",
                    persona=Persona.DEVELOPER,
                )

            # All commands can be tracked anonymously via public API
            # Server has specific models for each activity type:
            # - InstallMcpEvent (install command)
            # - CheckEvent, HookEvent (check/hook without auth)
            # - DoctorEvent, VersionEvent, LogsEvent (simple commands)
            usage_event = UsageEventData(
                activity_type=activity_type,
                event=event,
                timestamp=datetime.now(timezone.utc),
                duration_ms=duration_ms,
                command_args=command_args,
                zenable_mcp_version=__version__,
                data=event_data,
            )

            payload = ZenableMcpUsagePayload(
                system_info=system_info,
                system_hash=system_hash,
                usage_data=usage_event,
            )

            send_usage_data(payload)

    except Exception as e:
        # Never fail the main command due to usage data errors
        echo(
            f"Failed to record usage data: {type(e).__name__}: {e}",
            err=True,
            persona=Persona.DEVELOPER,
        )
