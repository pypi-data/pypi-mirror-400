# src/satflow/commands/config.py

"""Configuration management command."""

import typer


def config_cmd() -> None:
    """Get or set configuration values.

    Examples:
        bolt-on config                          # List all configuration keys and values
        bolt-on config game.game-dir            # Show value for a specific key
        bolt-on config game.game-dir /path      # Set value for a key
    """
    typer.echo("Hello, World! - Config")
