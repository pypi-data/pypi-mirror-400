"""
Cross-platform helper utilities for command execution and system detection.
"""

import platform
import subprocess
import sys
from pathlib import Path


def get_platform() -> str:
    """
    Get the current platform: 'macos', 'linux', or 'windows'.
    """
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    elif system == "Windows":
        return "windows"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def get_home_dir() -> Path:
    """Get the user's home directory."""
    return Path.home()


def find_repo_root() -> Path:
    """
    Find the dotfiles repository root directory.

    Searches in this order:
    1. DOTFILES_HOME environment variable (if set)
    2. Current working directory (if running from repo)
    3. ~/.dotfiles (standard installation location)
    4. Development/dotfiles folder

    Returns:
        Path to the dotfiles repository root
    """
    import os

    home = get_home_dir()

    # Check environment variable first
    if "DOTFILES_HOME" in os.environ:
        return Path(os.environ["DOTFILES_HOME"]).resolve()

    # Check current working directory
    if (Path.cwd() / "manifests" / "links.json").exists():
        return Path.cwd()

    # Check standard location
    if (home / ".dotfiles" / "manifests" / "links.json").exists():
        return home / ".dotfiles"

    # Check Development/dotfiles
    dev_location = home / "Development" / "dotfiles"
    if (dev_location / "manifests" / "links.json").exists():
        return dev_location

    # Fallback to package location
    return Path(__file__).parent.parent.parent.resolve()


def command_exists(cmd: str) -> bool:
    """Check if a command exists in the system PATH."""
    try:
        subprocess.run(
            ["which" if get_platform() != "windows" else "where", cmd],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_command(
    cmd: list[str],
    shell: bool = False,
    check: bool = True,
    verbose: bool = True,
    dry_run: bool = False,
) -> subprocess.CompletedProcess:
    """
    Execute a system command with consistent error handling and logging.

    Args:
        cmd: Command as list of strings
        shell: Whether to run in shell mode
        check: Whether to raise exception on non-zero exit
        verbose: Whether to print command execution
        dry_run: Whether to print without executing

    Returns:
        CompletedProcess object

    Raises:
        subprocess.CalledProcessError: If check=True and command fails
    """
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd

    if verbose:
        print(f"→ {cmd_str}")

    if dry_run:
        print("  [DRY RUN - not executed]")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=check,
            capture_output=False,
            text=True,
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ Command failed: {cmd_str}", file=sys.stderr)
        if e.stderr:
            print(f"  Error: {e.stderr}", file=sys.stderr)
        raise


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to ensure exists

    Returns:
        The path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_symlink(
    source: Path,
    target: Path,
    force: bool = False,
    verbose: bool = True,
) -> bool:
    """
    Safely create a symlink with idempotency checks.

    Args:
        source: Source file/directory (usually in repo)
        target: Target location (usually in home directory)
        force: Whether to overwrite existing symlink
        verbose: Whether to print operations

    Returns:
        True if symlink was created/verified, False if skipped

    Raises:
        FileExistsError: If target exists and force=False
    """
    source = source.resolve()
    target = target.resolve()

    if not source.exists():
        print(f"✗ Source does not exist: {source}")
        return False

    # If target is already a symlink pointing to source, we're done
    if target.is_symlink():
        if target.resolve() == source:
            if verbose:
                print(f"✓ Symlink already correct: {target} → {source}")
            return True
        elif force:
            target.unlink()
        else:
            print(f"✗ Symlink exists but points elsewhere: {target}")
            return False

    # If target exists and is not a symlink
    elif target.exists():
        if force:
            target.unlink()
        else:
            print(f"✗ Target exists: {target}")
            return False

    # Create parent directories if needed
    ensure_dir(target.parent)

    # Create the symlink
    try:
        target.symlink_to(source)
        if verbose:
            print(f"✓ Symlink created: {target} → {source}")
        return True
    except OSError as e:
        print(f"✗ Failed to create symlink: {e}")
        return False
