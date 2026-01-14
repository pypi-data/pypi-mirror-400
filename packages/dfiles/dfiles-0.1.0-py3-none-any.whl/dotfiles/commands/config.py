"""Configuration and system information."""

import typer

from dotfiles.config_manager import ConfigManager
from dotfiles.helpers import find_repo_root, get_home_dir, get_platform


def config() -> None:
    """
    Show current dotfiles configuration and system information.

    Displays:
    - Current platform
    - Repo location
    - Home directory
    - Manifest path
    - Available configurations
    """
    repo_root = find_repo_root()
    config_mgr = ConfigManager(repo_root)
    manifest = config_mgr.load_manifest()

    typer.echo("\n⚙️  Configuration\n")

    typer.echo(f"Platform:        {get_platform()}")
    typer.echo(f"Home:            {get_home_dir()}")
    typer.echo(f"Repo:            {repo_root}")
    typer.echo(f"Manifest:        {config_mgr.manifest_path}\n")

    typer.echo(f"Managed configs: {len(manifest)}")
    for repo_path, home_path in sorted(manifest.items()):
        typer.echo(f"  • {repo_path:<45} → {home_path}")

    typer.echo()
