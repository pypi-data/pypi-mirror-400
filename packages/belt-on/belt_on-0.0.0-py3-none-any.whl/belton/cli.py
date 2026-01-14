# src/belton/cli.py

import click
import typer
from rich.console import Console
from rich.panel import Panel

from .commands import calc_cmd, config_cmd, import_cmd
from .constants import PROG_NAME


# --------------------------------------------------------------------------- #
# Typer app
# --------------------------------------------------------------------------- #

app = typer.Typer()

# Register commands
app.command("calc")(calc_cmd.calc_cmd)
app.command("config")(config_cmd.config_cmd)
app.command("import")(import_cmd.import_cmd)


def _show_help_and_error(ctx: click.Context, error_msg: str) -> None:
    """Show help followed by error message with Typer's formatting."""
    # Show help
    click.echo(ctx.get_help(), err=True)
    # Show error with Typer's Rich formatting (same box style as Typer uses)
    console = Console(stderr=True)
    error_panel = Panel(
        error_msg,
        title="[red]Error[/red]",
        border_style="red",
        title_align="left",
    )
    console.print(error_panel)


# --------------------------------------------------------------------------- #
# Main entry
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:  # noqa: ARG001
    """Main CLI entry point.

    Args:
        argv: Command line arguments. If None, uses sys.argv.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        app(prog_name=PROG_NAME, standalone_mode=False)
    except click.UsageError as e:
        # Check if it's a missing command error
        if "Missing command" in str(e):
            # Get the context from the error
            ctx = e.ctx if hasattr(e, "ctx") and e.ctx else None
            if ctx:
                # Check if this is a subcommand error
                # (e.g., "satflow import" without subcommand)
                # If ctx.command is None but we have a parent, it's a subcommand error
                if ctx.command is None and ctx.parent and ctx.parent.command:  # pyright: ignore[reportUnnecessaryComparison]
                    # This is a subcommand error - show help for the parent
                    _show_help_and_error(ctx.parent, str(e))
                else:
                    # Top-level missing command
                    _show_help_and_error(ctx, str(e))
            else:
                # Fallback: create a new context
                fallback_ctx = click.Context(app, info_name=PROG_NAME)  # type: ignore[arg-type]
                _show_help_and_error(fallback_ctx, str(e))
            return 2
        # Re-raise other usage errors (they'll be formatted by Click/Typer)
        raise
    except SystemExit as e:
        # Typer may raise SystemExit with an exit code (e.g., on --help or errors)
        return e.code if isinstance(e.code, int) else 0
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully (standard exit code for SIGINT)
        return 130
    else:
        return 0
