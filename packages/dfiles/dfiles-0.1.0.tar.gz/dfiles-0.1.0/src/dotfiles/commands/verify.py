"""Verify symlink status."""

import typer

from dotfiles.config_manager import ConfigManager
from dotfiles.helpers import find_repo_root


def verify() -> None:
    """
    Verify all dotfiles symlinks are correctly set up.

    Shows:
    - Number of valid symlinks
    - Any broken or missing symlinks
    """
    repo_root = find_repo_root()
    config_mgr = ConfigManager(repo_root)

    typer.echo("\n🔍 Verifying Symlinks\n")

    valid, broken = config_mgr.verify_symlinks()

    if valid:
        typer.echo(f"✅ Valid symlinks: {len(valid)}")
        for link in valid:
            typer.echo(f"   ✓ {link}")

    if broken:
        typer.echo(f"\n❌ Broken/Missing symlinks: {len(broken)}")
        for link in broken:
            typer.echo(f"   ✗ {link}")
        typer.echo("\n💡 Run 'dotfiles install --force' to fix these.\n")
    else:
        typer.echo(f"\n✅ All {len(valid)} symlinks are valid!\n")
