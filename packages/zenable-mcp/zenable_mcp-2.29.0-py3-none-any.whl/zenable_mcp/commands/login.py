"""Login command to authenticate with Zenable via OAuth."""

import time

import click

from zenable_mcp.logging.command_logger import log_command
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.usage.manager import (
    _get_jwt_token_from_cache,
    record_command_usage,
    refresh_oauth_token,
)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.pass_context
@log_command
def login(ctx):
    """Authenticate with Zenable via OAuth.

    Opens a browser to complete the authentication flow.
    Credentials are cached locally for future commands.
    """
    start_time = time.time()
    error = None

    try:
        # Check if already logged in with a valid token
        existing_token = _get_jwt_token_from_cache()
        if existing_token:
            echo("Already authenticated with a valid token.")
            echo("Use 'zenable-mcp logout' to clear credentials first.")
            return

        # Trigger OAuth flow
        echo("Opening browser for authentication...")

        if refresh_oauth_token():
            echo("Successfully authenticated!")
        else:
            echo("Authentication failed. Please try again.", err=True)
            error = Exception("OAuth authentication failed")

    except Exception as e:
        error = e
        echo(f"Authentication failed: {e}", err=True)
        raise
    finally:
        duration_ms = int((time.time() - start_time) * 1000)
        record_command_usage(ctx=ctx, duration_ms=duration_ms, error=error)
