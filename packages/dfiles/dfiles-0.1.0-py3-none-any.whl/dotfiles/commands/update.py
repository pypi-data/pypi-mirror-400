"""Update system packages and development tools."""

import typer

from dotfiles.helpers import command_exists, get_platform, run_command
from dotfiles.package_manager import PackageManager


def update_uv() -> bool:
    """Update UV itself."""
    if not command_exists("uv"):
        typer.echo("✗ UV not found")
        return False

    try:
        run_command(["uv", "self", "update"], verbose=True)
        return True
    except Exception as e:
        typer.echo(f"⚠ UV self-update failed: {e}")
        return False


def update_uv_tools() -> bool:
    """Update all UV tools."""
    if not command_exists("uv"):
        return False

    try:
        run_command(["uv", "tool", "upgrade", "--all"], verbose=True)
        return True
    except Exception as e:
        typer.echo(f"⚠ UV tools update failed: {e}")
        return False


def update_rust() -> bool:
    """Update Rust and installed cargo tools."""
    if not command_exists("rustup"):
        return False

    try:
        typer.echo("→ Updating Rust...")
        run_command(["rustup", "update"], verbose=True)

        if command_exists("cargo-install-update"):
            typer.echo("→ Updating cargo-installed tools...")
            run_command(["cargo", "install-update", "-a"], verbose=True)

        return True
    except Exception as e:
        typer.echo(f"⚠ Rust update failed: {e}")
        return False


def update_bun() -> bool:
    """Update Bun."""
    if not command_exists("bun"):
        return False

    try:
        run_command(["bun", "upgrade"], verbose=True)
        return True
    except Exception as e:
        typer.echo(f"⚠ Bun update failed: {e}")
        return False


def update_npm_global() -> bool:
    """Update npm global packages."""
    if not command_exists("npm"):
        return False

    try:
        run_command(["npm", "update", "-g"], verbose=True)
        return True
    except Exception as e:
        typer.echo(f"⚠ npm global update failed: {e}")
        return False


def update(
    tools_only: bool = typer.Option(
        False,
        "--tools-only",
        help="Only update development tools (skip system packages)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without executing",
    ),
    verbose: bool = typer.Option(
        True,
        "--verbose",
        "-v",
        help="Print detailed output",
    ),
) -> None:
    """
    Update dotfiles, system packages, and development tools.

    This command will:
    1. Update system packages (Homebrew/winget/apt)
    2. Update all development tools (uv, cargo, bun, npm)
    3. Clean up caches and unused packages
    """
    typer.echo("\n🔄 Dotfiles Update")
    typer.echo(f"   Platform: {get_platform()}\n")

    # Phase 1: System packages
    if not tools_only:
        typer.echo("1️⃣  Updating system packages...")
        pkg_mgr = PackageManager(dry_run=dry_run, verbose=verbose)

        if pkg_mgr.update_packages():
            typer.echo("   ✓ System packages updated\n")
        else:
            typer.echo("   ⚠ Some package updates failed\n")
    else:
        typer.echo("1️⃣  Skipping system packages (--tools-only)\n")

    # Phase 2: Development tools
    typer.echo("2️⃣  Updating development tools...")

    typer.echo("   • UV...")
    update_uv()

    typer.echo("   • UV tools...")
    update_uv_tools()

    typer.echo("   • Rust/Cargo...")
    update_rust()

    typer.echo("   • Bun...")
    update_bun()

    typer.echo("   • npm (global)...")
    update_npm_global()

    typer.echo("   ✓ Tool updates complete\n")

    # Phase 3: Cleanup
    if not dry_run:
        typer.echo("3️⃣  Cleaning up...")
        pkg_mgr = PackageManager(dry_run=dry_run, verbose=False)

        if pkg_mgr.cleanup():
            typer.echo("   ✓ Cleanup complete\n")
        else:
            typer.echo("   ⚠ Some cleanup failed (non-critical)\n")
    else:
        typer.echo("3️⃣  Skipping cleanup (--dry-run)\n")

    typer.echo("✅ Update Complete!")
    typer.echo("   Next: exec zsh  (reload your shell)\n")
