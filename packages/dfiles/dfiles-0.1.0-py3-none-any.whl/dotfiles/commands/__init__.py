"""Command-line interface commands for dotfiles."""

from pathlib import Path

import typer

app = typer.Typer(help="Dotfiles management and synchronization")
