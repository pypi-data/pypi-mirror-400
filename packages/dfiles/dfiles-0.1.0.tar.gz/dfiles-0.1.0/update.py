#!/usr/bin/env python3
"""
Update script for dotfiles and installed tools.

Usage:
    uv run update.py [OPTIONS]

This script will:
1. Update system packages (brew/winget/apt)
2. Update tool versions (uv, cargo, bun, npm)
3. Clean up unused packages and caches
"""

import argparse
import sys

from dotfiles.helpers import command_exists, get_platform, run_command
from dotfiles.package_manager import PackageManager


def update_uv() -> bool:
    """Update UV itself."""
    if not command_exists("uv"):
        print("✗ UV not found")
        return False

    try:
        run_command(["uv", "self", "update"], verbose=True)
        return True
    except Exception as e:
        print(f"⚠ UV self-update failed: {e}")
        return False


def update_uv_tools() -> bool:
    """Update all UV tools."""
    if not command_exists("uv"):
        return False

    try:
        run_command(["uv", "tool", "upgrade", "--all"], verbose=True)
        return True
    except Exception as e:
        print(f"⚠ UV tools update failed: {e}")
        return False


def update_rust() -> bool:
    """Update Rust and installed cargo tools."""
    if not command_exists("rustup"):
        return False

    try:
        print("→ Updating Rust...")
        run_command(["rustup", "update"], verbose=True)

        if command_exists("cargo-install-update"):
            print("→ Updating cargo-installed tools...")
            run_command(["cargo", "install-update", "-a"], verbose=True)

        return True
    except Exception as e:
        print(f"⚠ Rust update failed: {e}")
        return False


def update_bun() -> bool:
    """Update Bun."""
    if not command_exists("bun"):
        return False

    try:
        run_command(["bun", "upgrade"], verbose=True)
        return True
    except Exception as e:
        print(f"⚠ Bun update failed: {e}")
        return False


def update_npm_global() -> bool:
    """Update npm global packages."""
    if not command_exists("npm"):
        return False

    try:
        run_command(["npm", "update", "-g"], verbose=True)
        return True
    except Exception as e:
        print(f"⚠ npm global update failed: {e}")
        return False


def main() -> int:
    """Main update orchestration."""
    parser = argparse.ArgumentParser(
        description="Update dotfiles, system packages, and development tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run update.py              # Full update
  uv run update.py --tools-only # Skip system packages
  uv run update.py --dry-run    # Preview without changes
        """,
    )
    parser.add_argument(
        "--tools-only",
        action="store_true",
        help="Only update development tools (skip system packages)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Print detailed output (default: on)",
    )

    args = parser.parse_args()

    print("\n🔄 Dotfiles Update")
    print(f"   Platform: {get_platform()}\n")

    # Phase 1: System packages
    if not args.tools_only:
        print("1️⃣  Updating system packages...")
        pkg_mgr = PackageManager(dry_run=args.dry_run, verbose=args.verbose)

        if pkg_mgr.update_packages():
            print("   ✓ System packages updated\n")
        else:
            print("   ⚠ Some package updates failed\n")
    else:
        print("1️⃣  Skipping system packages (--tools-only)\n")

    # Phase 2: Development tools
    print("2️⃣  Updating development tools...")

    print("   • UV...")
    update_uv()

    print("   • UV tools...")
    update_uv_tools()

    print("   • Rust/Cargo...")
    update_rust()

    print("   • Bun...")
    update_bun()

    print("   • npm (global)...")
    update_npm_global()

    print("   ✓ Tool updates complete\n")

    # Phase 3: Cleanup
    if not args.dry_run:
        print("3️⃣  Cleaning up...")
        pkg_mgr = PackageManager(dry_run=args.dry_run, verbose=False)

        if pkg_mgr.cleanup():
            print("   ✓ Cleanup complete\n")
        else:
            print("   ⚠ Some cleanup failed (non-critical)\n")
    else:
        print("3️⃣  Skipping cleanup (--dry-run)\n")

    print("✅ Update Complete!")
    print("   Next: exec zsh  (reload your shell)\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
