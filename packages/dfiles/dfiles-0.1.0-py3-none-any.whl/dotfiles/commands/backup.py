"""Backup management for dotfiles."""

import typer

from dotfiles.helpers import get_home_dir


def backup(
    restore: bool = typer.Option(
        False,
        "--restore",
        help="Restore from backups instead of listing",
    ),
    list_only: bool = typer.Option(
        False,
        "--list",
        help="List all backup files",
    ),
) -> None:
    """
    Manage dotfiles backups.

    List or restore backup files created during installation.
    """
    home = get_home_dir()

    typer.echo("\n💾 Backup Management\n")

    # Find all backup files
    backup_files = list(home.glob("*.backup"))
    backup_files.extend(home.glob(".zsh/*.backup"))
    backup_files.extend(home.glob(".config/*.backup"))

    if not backup_files:
        typer.echo("No backup files found.\n")
        return

    if restore:
        typer.echo(f"Found {len(backup_files)} backup file(s) to restore:\n")

        for backup_file in sorted(backup_files):
            original_file = backup_file.with_suffix("")

            typer.echo(f"  {backup_file.name} → {original_file.name}")

        confirm = typer.confirm(
            "\n⚠️  This will overwrite your current configurations. Continue?"
        )

        if confirm:
            for backup_file in backup_files:
                original_file = backup_file.with_suffix("")
                if original_file.exists() or original_file.is_symlink():
                    original_file.unlink()
                backup_file.rename(original_file)
                typer.echo(f"  ✓ Restored {original_file.name}")

            typer.echo("\n✅ Restore complete! Run 'exec zsh' to reload.\n")
        else:
            typer.echo("Cancelled.\n")

    else:
        typer.echo(f"Found {len(backup_files)} backup file(s):\n")
        for backup_file in sorted(backup_files):
            size = backup_file.stat().st_size
            typer.echo(f"  • {backup_file} ({size} bytes)")

        typer.echo("\nRun 'dotfiles backup --restore' to restore from backups.\n")
