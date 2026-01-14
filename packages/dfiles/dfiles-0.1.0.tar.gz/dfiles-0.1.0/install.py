#!/usr/bin/env python3
"""
Main installation script for dotfiles.

Usage:
    uv run install.py [OPTIONS]

This script will:
1. Detect your system (macOS, Windows, or Linux)
2. Install core tools via package managers (Homebrew/winget/apt)
3. Create symlinks for all configuration files
4. Backup existing configurations before overwriting
"""

import argparse
import sys
from pathlib import Path

from dotfiles.config_manager import ConfigManager
from dotfiles.helpers import command_exists, get_home_dir, get_platform
from dotfiles.package_manager import PackageManager


def bootstrap_uv() -> bool:
    """
    Ensure uv is installed and accessible.

    Returns:
        True if uv is available
    """
    if command_exists("uv"):
        return True

    print("⚠ UV not found. Installing UV...")
    platform = get_platform()

    if platform == "macos" or platform == "linux":
        try:
            from dotfiles.helpers import run_command

            run_command(
                ["bash", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
                verbose=True,
            )
            return True
        except Exception as e:
            print(f"✗ Failed to install UV: {e}", file=sys.stderr)
            return False

    elif platform == "windows":
        try:
            from dotfiles.helpers import run_command

            run_command(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "ByPass",
                    "-Command",
                    "irm https://astral.sh/uv/install.ps1 | iex",
                ],
                verbose=True,
            )
            return True
        except Exception as e:
            print(f"✗ Failed to install UV: {e}", file=sys.stderr)
            return False

    return False


def get_python_install_command() -> list[str]:
    """
    Get the command to install Python 3.12+ as a system version.

    Uses --python-preference only-system to ensure Python is installed
    as a system Python rather than a uv-managed version.
    """
    return [
        "uv",
        "python",
        "install",
        "--python-preference",
        "only-system",
        "3.12",
    ]


def main() -> int:
    """Main installation orchestration."""
    parser = argparse.ArgumentParser(
        description="Install and configure dotfiles for your system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run install.py                 # Full installation
  uv run install.py --no-packages   # Skip package manager updates
  uv run install.py --force         # Overwrite existing configs
  uv run install.py --dry-run       # Preview without changes
        """,
    )
    parser.add_argument(
        "--no-packages",
        action="store_true",
        help="Skip package manager updates/installs",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing configuration files",
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

    # Get repo root (parent of this script)
    repo_root = Path(__file__).parent.resolve()
    print("\n🚀 Dotfiles Installation")
    print(f"   Platform: {get_platform()}")
    print(f"   Home: {get_home_dir()}")
    print(f"   Repo: {repo_root}\n")

    # Step 1: Ensure UV is available
    print("1️⃣  Checking UV installation...")
    if not command_exists("uv"):
        print("   → Installing UV...")
        if not bootstrap_uv():
            print("✗ Failed to bootstrap UV", file=sys.stderr)
            return 1
    print("   ✓ UV is available\n")

    # Step 1.5: Ensure Git is available
    print("1️⃣ .5️⃣  Checking Git installation...")
    if not command_exists("git"):
        platform = get_platform()
        if platform == "windows":
            print("   ✗ Git not found in PATH")
            print("   → Windows requires manual Git installation")
            print("   → Download from: https://git-scm.com/download/win")
            print("   → Or install via: winget install Git.Git\n")
            return 1
        else:
            print("   ⚠ Git not found (may be needed for full functionality)")
    else:
        print("   ✓ Git is available\n")

    # Step 2: Ensure Python 3.12+ is available
    print("2️⃣  Ensuring Python 3.12+ (as system version)...")
    from dotfiles.helpers import run_command

    try:
        run_command(
            get_python_install_command(),
            verbose=args.verbose,
            dry_run=args.dry_run,
        )
        print("   ✓ Python 3.12+ is available\n")
    except Exception as e:
        print(f"⚠ Python 3.12 setup: {e}", file=sys.stderr)
        print("   (This may be OK if already installed)\n")

    # Step 3: Detect existing configurations
    print("3️⃣  Detecting existing configurations...")
    config_mgr = ConfigManager(repo_root)
    existing = config_mgr.detect_existing_configs()
    if existing:
        print(f"   Found {len(existing)} existing config(s):")
        for config_name, config_path in existing.items():
            print(f"     - {config_name}: {config_path}")

        if not args.force:
            print("   (Use --force to overwrite existing configs)\n")
    else:
        print("   No existing configs detected\n")

    # Step 4: Update system packages (optional)
    if not args.no_packages:
        print("4️⃣  Updating system packages...")
        pkg_mgr = PackageManager(dry_run=args.dry_run, verbose=args.verbose)
        if pkg_mgr.update_packages():
            print("   ✓ Packages updated\n")
        else:
            print("   ⚠ Package update had issues (continuing...)\n")
    else:
        print("4️⃣  Skipping package updates (--no-packages)\n")

    # Step 5: Create configuration symlinks
    print("5️⃣  Creating configuration symlinks...")
    successful, failed = config_mgr.symlink_configs(
        force=args.force,
        verbose=args.verbose,
    )
    print(f"   ✓ Successful: {successful}, Failed: {failed}\n")

    if failed > 0 and not args.force:
        print("   ⚠ Some symlinks failed. Use --force to overwrite existing files.\n")

    # Step 6: Success summary
    print("✅ Installation Complete!")
    print("\n📋 Next Steps:")
    print("   1. Review created symlinks: ls -la ~/")
    print("   2. Reload shell: exec zsh")
    print("   3. Check command availability: which uv bun cargo go")
    print("   4. For updates later: uv run update.py\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
