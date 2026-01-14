"""Main CLI entry point for dotfiles."""

from importlib.metadata import version

import typer

from dotfiles.commands.backup import backup
from dotfiles.commands.config import config
from dotfiles.commands.install import install
from dotfiles.commands.update import update
from dotfiles.commands.verify import verify

app = typer.Typer(
    help="🚀 Dotfiles automation and configuration management",
    no_args_is_help=True,
)

# Add subcommands
app.command()(install)
app.command()(update)
app.command()(verify)
app.command()(config)
app.command()(backup)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    show_version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
    ),
) -> None:
    """Dotfiles CLI - Manage your development environment configuration."""
    if show_version:
        try:
            v = version("dotfiles")
        except Exception:
            v = "0.1.0"
        typer.echo(f"dotfiles version {v}")
        raise typer.Exit(0)


def run() -> None:
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    app()
